#!/usr/bin/env python3
"""Offline validation of the G2.2 HOLD post-ILM recovery payload. No EasyEDA write."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "harness"))
from extract_electrical_graph import _load_source  # noqa: E402
from easyeda_source_format import parse_v3_records  # noqa: E402
from g22_pwr1_ilm import _attrs_by_owner, _components, analyse as analyse_ilm  # noqa: E402
from g22_usb_hub import analyse as analyse_usb  # noqa: E402

HOLD = "55ed9ee948734a0e903f37744b51f3b8"
PAGE = "1435cb46f39e48c8a8aadbb84ca81603"
EXPECTED_HASH = "3165690:5aad2e78"
EXPECTED_DIGEST = "ccf3ec9546330a204b56773a71eba14ca534d6f35944a0ff81652ac965064423"
REQUIRED = (
    "U20-USB",
    "U21-USB",
    "U22-USB",
    "U23-USB",
    "U24-USB",
    "U25-USB",
    "Y3-USB",
    "J12-USB",
    "U1-PWR1",
    "J1-PWR1",
)


def fnv1a(text: str) -> str:
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return f"{len(text)}:{h:08x}"


def skip_dochead(source: str) -> str:
    lines = source.splitlines(keepends=True)
    if lines and '"DOCHEAD"' in lines[0]:
        return "".join(lines[1:])
    return source


def main() -> int:
    payload_path = ROOT / (
        "evidence/VAL-G2-2026-08-28/g22-hold-lane/anchors/post-ilm-saved-source.json"
    )
    source, meta = _load_source(payload_path)
    digest = hashlib.sha256(skip_dochead(source).encode("utf-8")).hexdigest()
    hash_ = fnv1a(source)
    recs = parse_v3_records(source)
    attrs = _attrs_by_owner(recs)
    comps = _components(recs, attrs)
    ilm = analyse_ilm(source, source_path=str(payload_path))
    usb = analyse_usb(source, source_path=str(payload_path))
    j1 = comps.get("J1-PWR1") or {}
    report = {
        "payload_path": str(payload_path),
        "project_uuid": meta.get("project_uuid"),
        "document_uuid": meta.get("document_uuid"),
        "source_hash": hash_,
        "meta_source_hash": meta.get("source_hash"),
        "normalized_sha256": digest,
        "designated": len(comps),
        "j1_xy": [j1.get("x"), j1.get("y")],
        "present": {name: name in comps for name in REQUIRED},
        "ilm_ok": ilm.ok,
        "ilm_errors": ilm.errors[:8],
        "u1_9": None if "9" not in ilm.u1_pins else ilm.u1_pins["9"].nets,
        "usb_ok": usb.ok,
        "usb_error_count": len(usb.errors),
        "usb_errors_head": usb.errors[:8],
        "u20_proof": usb.transform.get("u20_proof_pins_matched"),
    }
    out = Path(__file__).with_name("g22-hold-recover-payload-validation.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    fail = []
    if meta.get("project_uuid") != HOLD:
        fail.append(f"project_uuid {meta.get('project_uuid')}")
    if meta.get("document_uuid") != PAGE:
        fail.append(f"document_uuid {meta.get('document_uuid')}")
    if hash_ != EXPECTED_HASH:
        fail.append(f"source_hash {hash_}")
    if digest != EXPECTED_DIGEST:
        fail.append(f"normalized {digest}")
    for name in REQUIRED:
        if name not in comps:
            fail.append(f"missing {name}")
    if j1.get("x") != 150 or j1.get("y") != -4120:
        fail.append(f"J1 at {(j1.get('x'), j1.get('y'))}")
    if not ilm.ok:
        fail.append("ILM FAIL")
    u19 = ilm.u1_pins.get("9")
    if not u19 or u19.nets != ["USB_EFUSE_ILIM"]:
        fail.append(f"U1.9 {None if not u19 else u19.nets}")
    if usb.ok:
        fail.append("USB unexpectedly PASS")
    print(json.dumps(report, indent=2))
    if fail:
        print("PAYLOAD_VALIDATE=FAIL")
        for item in fail:
            print(" ", item)
        return 2
    print("PAYLOAD_VALIDATE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
