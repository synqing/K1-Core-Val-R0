#!/usr/bin/env python3
"""Prove two electrical graphs are identical where G2.2 is forbidden to differ.

Geometry is invisible here. One pin changing net membership is a fail.
Either graph with zero designators or zero nets fails closed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from extract_electrical_graph import canonical_identity


IDENTITY_FIELDS = (
    "devices",
    "unique_ids",
    "symbols",
    "footprints",
    "mpns",
    "supplier_parts",
    "suppliers",
    "supplier_ids",
    "bom",
    "pcb",
    "unit_count",
)


def load_graph(path: Path) -> dict:
    graph = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(graph, dict) or graph.get("schema") != "k1.electrical-graph.v1":
        raise SystemExit(f"{path}: not a k1.electrical-graph.v1 document")
    counts = graph.get("counts") or {}
    if not counts.get("designators"):
        raise SystemExit(f"{path}: 0 designators; failing closed")
    if not counts.get("named_nets"):
        raise SystemExit(f"{path}: 0 named nets; failing closed")
    return graph


def _diff_sets(name, left, right, errors):
    lost = sorted(set(left) - set(right))
    gained = sorted(set(right) - set(left))
    if lost:
        errors.append(f"{name} lost: {lost[:12]}{'…' if len(lost) > 12 else ''}")
    if gained:
        errors.append(f"{name} gained: {gained[:12]}{'…' if len(gained) > 12 else ''}")


def compare_graphs(reference: dict, candidate: dict) -> list[str]:
    errors = []
    ref_id = canonical_identity(reference)
    cand_id = canonical_identity(candidate)
    _diff_sets("designators", ref_id, cand_id, errors)
    for designator in sorted(set(ref_id) & set(cand_id)):
        left = ref_id[designator]
        right = cand_id[designator]
        for field in IDENTITY_FIELDS:
            if left[field] != right[field]:
                errors.append(
                    f"{designator}.{field}: {left[field]!r} -> {right[field]!r}"
                )

    _diff_sets("named_nets", reference.get("nets") or [], candidate.get("nets") or [], errors)

    def nc_keys(graph):
        return {(row["designator"], row["pin_id"]) for row in graph.get("nc") or []}

    _diff_sets("nc_intent", nc_keys(reference), nc_keys(candidate), errors)

    ref_pins = (reference.get("pin_membership") or {}).get("pins") or {}
    cand_pins = (candidate.get("pin_membership") or {}).get("pins") or {}
    shared = set(ref_pins) & set(cand_pins)
    for key in sorted(shared):
        left = ref_pins[key]
        right = cand_pins[key]
        if bool(left.get("nc")) != bool(right.get("nc")):
            errors.append(f"{key} nc: {left.get('nc')} -> {right.get('nc')}")
        if left.get("net") != right.get("net"):
            errors.append(f"{key} net: {left.get('net')!r} -> {right.get('net')!r}")
        if sorted(left.get("nets") or []) != sorted(right.get("nets") or []):
            errors.append(f"{key} nets: {left.get('nets')} -> {right.get('nets')}")

    missing = sorted(set(ref_pins) - set(cand_pins))
    if missing:
        errors.append(
            f"pin_membership lost {len(missing)} reference pin(s): {missing[:12]}"
        )

    ref_cov = (reference.get("pin_membership") or {}).get("coverage")
    cand_cov = (candidate.get("pin_membership") or {}).get("coverage")
    extra = sorted(set(cand_pins) - set(ref_pins))
    if extra and ref_cov == "COMPLETE" and cand_cov == "COMPLETE":
        errors.append(
            f"pin_membership gained {len(extra)} pin(s) under COMPLETE coverage: {extra[:12]}"
        )

    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args(argv)
    reference = load_graph(args.reference)
    candidate = load_graph(args.candidate)
    errors = compare_graphs(reference, candidate)
    if errors:
        print("ELECTRICAL_EQUIVALENCE=FAIL")
        print(f"compared_designators={reference['counts']['designators']}")
        print(f"compared_nets={reference['counts']['named_nets']}")
        for item in errors:
            print(f"  {item}")
        return 2
    print("ELECTRICAL_EQUIVALENCE=PASS")
    print(
        f"designators={reference['counts']['designators']} "
        f"nets={reference['counts']['named_nets']} "
        f"nc={reference['counts']['nc']} "
        f"bound_pins={reference['counts']['bound_pins']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
