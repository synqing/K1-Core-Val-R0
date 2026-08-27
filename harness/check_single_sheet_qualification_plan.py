#!/usr/bin/env python3
"""Fail-closed semantic preflight for the VAL-G2.0 EasyEDA fixture plan.

The qualification measures whether the real Option-C schematic can remain usable on one
EasyEDA page. Primitive counts alone cannot prove that. This checker therefore runs before
project creation and requires an endpoint-level, source-derived fixture plan.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLAN = ROOT / "schematic/single-sheet-qualification/FIXTURE-PLAN.json"
EXPECTED_PROJECT_NAME = "K1-CORE-VAL-SINGLE-SHEET-QUAL"

REQUIRED_DOMAINS = {
    "RT1062_SUPPORT",
    "ESP32_S3_SUPPORT",
    "K1BR",
    "POWER",
    "LED",
    "AUDIO",
    "USB",
    "NFC",
    "MOTION",
    "DEBUG",
    "OPTIONS",
}

REQUIRED_MAJOR_ROLES = {
    "rt1062",
    "esp32_s3",
    "audio_frontend",
    "nfc_frontend",
    "accelerometer",
    "power_entry",
}

COMPONENT_CLASSES = {
    "processor",
    "major_ic",
    "support_ic",
    "power",
    "passive",
    "connector",
    "protection",
    "clock",
    "testpoint",
    "option",
}

ACTIVE_CLASSES = {"processor", "major_ic", "support_ic", "power", "clock"}
LOAD_CLASSES = {"passive", "connector", "protection", "testpoint", "option"}
FUNCTIONAL_NET_KINDS = {"signal", "control", "clock", "bus"}
RAIL_NET_KINDS = {"power", "ground"}
NET_KINDS = FUNCTIONAL_NET_KINDS | RAIL_NET_KINDS | {"test"}
RENDER_KINDS = {"explicit_wire", "labelled_net", "bus"}
PLACEHOLDER_RE = re.compile(r"(?:^|[_-])(QUAL|DUMMY|PLACEHOLDER|PADDING|REPLICA)(?:[_-]|$)", re.I)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_plan(plan: Any) -> tuple[list[str], dict[str, int]]:
    failures: list[str] = []
    counts = {
        "components": 0,
        "baseline_components": 0,
        "fixture_only_components": 0,
        "nets": 0,
        "high_fanout_nets": 0,
        "explicit_wire_nets": 0,
        "domains": 0,
        "major_roles": 0,
        "endpoints": 0,
    }

    def fail(message: str) -> None:
        failures.append(message)

    if not isinstance(plan, dict):
        fail("plan root must be a JSON object")
        return failures, counts

    if plan.get("schema_version") != 1:
        fail("schema_version must be 1")
    if plan.get("plan_state") != "READY_FOR_EDA":
        fail("plan_state must be READY_FOR_EDA")
    if plan.get("project_name") != EXPECTED_PROJECT_NAME:
        fail("project_name must be %s" % EXPECTED_PROJECT_NAME)

    estimate = plan.get("option_c_estimated_symbols")
    if not _is_int(estimate) or estimate <= 0:
        fail("option_c_estimated_symbols must be a resolved positive integer")
        estimate = None

    sources = plan.get("estimate_sources")
    if not isinstance(sources, list) or not sources or not all(
        isinstance(source, str) and source.strip() for source in sources
    ):
        fail("estimate_sources must contain at least one non-empty source reference")

    components = plan.get("components")
    if not isinstance(components, list):
        fail("components must be a list")
        components = []
    counts["components"] = len(components)
    if not components:
        fail("components parsed zero records")

    declared_planned = plan.get("planned_symbols")
    if not _is_int(declared_planned) or declared_planned != len(components):
        fail("planned_symbols must equal the parsed component count")

    refs: dict[str, dict[str, Any]] = {}
    domain_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    baseline_count = 0
    fixture_only_count = 0

    for index, component in enumerate(components):
        prefix = "components[%d]" % index
        if not isinstance(component, dict):
            fail("%s must be an object" % prefix)
            continue
        ref = component.get("ref")
        role = component.get("role")
        domain = component.get("domain")
        component_class = component.get("class")
        basis = component.get("basis")
        fixture_only = component.get("fixture_only", False)

        if not isinstance(ref, str) or not ref.strip():
            fail("%s.ref must be non-empty" % prefix)
            continue
        if ref in refs:
            fail("duplicate component ref: %s" % ref)
        else:
            refs[ref] = component
        if not isinstance(role, str) or not role.strip():
            fail("%s.role must be non-empty" % prefix)
        else:
            role_counts[role] += 1
            if PLACEHOLDER_RE.search(role):
                fail("component %s uses placeholder/count-padding role %s" % (ref, role))
        if domain not in REQUIRED_DOMAINS:
            fail("component %s has unknown domain %r" % (ref, domain))
        else:
            domain_counts[domain] += 1
        if component_class not in COMPONENT_CLASSES:
            fail("component %s has unknown class %r" % (ref, component_class))
        if not isinstance(basis, str) or not basis.strip():
            fail("component %s must record a quantity/architecture basis" % ref)
        if not isinstance(fixture_only, bool):
            fail("component %s fixture_only must be boolean" % ref)
        elif fixture_only:
            fixture_only_count += 1
            stress_basis = component.get("stress_basis")
            if not isinstance(stress_basis, str) or not stress_basis.strip():
                fail("fixture-only component %s must record stress_basis" % ref)
            if component_class in {"processor", "major_ic", "support_ic", "power", "clock"}:
                fail("fixture-only component %s may not duplicate a functional IC/power/clock role" % ref)
        else:
            baseline_count += 1

    counts["baseline_components"] = baseline_count
    counts["fixture_only_components"] = fixture_only_count
    counts["domains"] = len(domain_counts)
    counts["major_roles"] = len(REQUIRED_MAJOR_ROLES & set(role_counts))

    for domain in sorted(REQUIRED_DOMAINS - set(domain_counts)):
        fail("required domain has zero components: %s" % domain)
    for role in sorted(REQUIRED_MAJOR_ROLES - set(role_counts)):
        fail("required major role missing: %s" % role)
    for role in sorted(REQUIRED_MAJOR_ROLES & set(role_counts)):
        if role_counts[role] != 1:
            fail("required major role %s must occur exactly once, found %d" % (role, role_counts[role]))

    if estimate is not None:
        if baseline_count != estimate:
            fail("baseline component count %d must equal option_c_estimated_symbols %d"
                 % (baseline_count, estimate))
        minimum = max(200, math.ceil(1.20 * estimate))
        if len(components) < minimum:
            fail("planned component count %d is below required N_test %d" % (len(components), minimum))

    nets = plan.get("nets")
    if not isinstance(nets, list):
        fail("nets must be a list")
        nets = []
    counts["nets"] = len(nets)
    if not nets:
        fail("nets parsed zero records")
    if len(nets) < 120:
        fail("fixture requires at least 120 named nets, found %d" % len(nets))

    seen_nets: set[str] = set()
    component_net_kinds: dict[str, set[str]] = defaultdict(set)
    domain_explicit_wire_count: Counter[str] = Counter()
    net_by_name: dict[str, dict[str, Any]] = {}

    for index, net in enumerate(nets):
        prefix = "nets[%d]" % index
        if not isinstance(net, dict):
            fail("%s must be an object" % prefix)
            continue
        name = net.get("name")
        kind = net.get("kind")
        render = net.get("render")
        endpoints = net.get("endpoints")
        if not isinstance(name, str) or not name.strip():
            fail("%s.name must be non-empty" % prefix)
            continue
        if name in seen_nets:
            fail("duplicate net name: %s" % name)
        seen_nets.add(name)
        net_by_name[name] = net
        if PLACEHOLDER_RE.search(name):
            fail("net %s uses synthetic qualification/placeholder naming" % name)
        if kind not in NET_KINDS:
            fail("net %s has unknown kind %r" % (name, kind))
        if render not in RENDER_KINDS:
            fail("net %s has unknown render strategy %r" % (name, render))
        if render == "explicit_wire":
            counts["explicit_wire_nets"] += 1
        if not isinstance(endpoints, list):
            fail("net %s endpoints must be a list" % name)
            endpoints = []

        parsed_endpoints: set[tuple[str, str]] = set()
        endpoint_classes: set[str] = set()
        endpoint_domains: set[str] = set()
        for endpoint_index, endpoint in enumerate(endpoints):
            if not isinstance(endpoint, dict):
                fail("net %s endpoint[%d] must be an object" % (name, endpoint_index))
                continue
            ref = endpoint.get("ref")
            pin = endpoint.get("pin")
            if not isinstance(ref, str) or not isinstance(pin, str) or not ref or not pin:
                fail("net %s endpoint[%d] requires non-empty ref and pin" % (name, endpoint_index))
                continue
            if ref not in refs:
                fail("net %s references unknown component %s" % (name, ref))
                continue
            parsed_endpoints.add((ref, pin))
            component_net_kinds[ref].add(kind)
            endpoint_classes.add(str(refs[ref].get("class")))
            endpoint_domains.add(str(refs[ref].get("domain")))
        counts["endpoints"] += len(parsed_endpoints)
        if len(parsed_endpoints) < 2:
            fail("net %s has fewer than two distinct component-pin endpoints" % name)
        if render == "explicit_wire":
            for domain in endpoint_domains:
                domain_explicit_wire_count[domain] += 1

        if net.get("high_fanout") is True:
            counts["high_fanout_nets"] += 1
            if len(parsed_endpoints) < 4:
                fail("high-fanout net %s has fewer than four endpoints" % name)
            if not (endpoint_classes & ACTIVE_CLASSES):
                fail("high-fanout net %s has no active/source IC endpoint" % name)
            if not (endpoint_classes & LOAD_CLASSES):
                fail("high-fanout net %s has no load/protection/passive endpoint" % name)

    if counts["high_fanout_nets"] < 10:
        fail("fixture requires at least 10 high-fanout nets, found %d"
             % counts["high_fanout_nets"])
    if counts["explicit_wire_nets"] < 20:
        fail("fixture requires at least 20 explicitly wired nets, found %d"
             % counts["explicit_wire_nets"])
    for domain in sorted(REQUIRED_DOMAINS):
        if domain_explicit_wire_count[domain] == 0:
            fail("required domain has no explicitly wired net: %s" % domain)

    for ref, component in refs.items():
        if component.get("role") not in REQUIRED_MAJOR_ROLES:
            continue
        kinds = component_net_kinds.get(ref, set())
        if component.get("role") != "power_entry" and not (kinds & RAIL_NET_KINDS):
            fail("major component %s has no planned power/ground endpoint" % ref)
        if component.get("role") != "power_entry" and not (kinds & FUNCTIONAL_NET_KINDS):
            fail("major component %s has no planned functional interface endpoint" % ref)

    power_tree_nets = plan.get("power_tree_nets")
    if not isinstance(power_tree_nets, list) or len(power_tree_nets) < 4:
        fail("power_tree_nets must name at least four real power-tree nets")
        power_tree_nets = []
    for name in power_tree_nets:
        net = net_by_name.get(name)
        if net is None:
            fail("power_tree_nets references unknown net %s" % name)
            continue
        if net.get("kind") != "power":
            fail("power-tree net %s must have kind power" % name)
        if net.get("render") != "explicit_wire":
            fail("power-tree net %s must be explicitly wired" % name)

    if plan.get("stub_only_wiring") is not False:
        fail("stub_only_wiring must be explicitly false")

    return failures, counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    args = parser.parse_args()

    if not args.plan.is_file():
        print("FIXTURE_PLAN_COMPONENTS=0")
        print("FIXTURE_PLAN_NETS=0")
        print("FAIL: fixture plan missing: %s" % args.plan)
        print("SINGLE_SHEET_QUALIFICATION_PLAN=FAIL")
        return 1
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("FIXTURE_PLAN_COMPONENTS=0")
        print("FIXTURE_PLAN_NETS=0")
        print("FAIL: fixture plan could not be parsed: %s" % exc)
        print("SINGLE_SHEET_QUALIFICATION_PLAN=FAIL")
        return 1

    failures, counts = validate_plan(plan)
    print("FIXTURE_PLAN_COMPONENTS=%d" % counts["components"])
    print("FIXTURE_PLAN_BASELINE_COMPONENTS=%d" % counts["baseline_components"])
    print("FIXTURE_PLAN_FIXTURE_ONLY_COMPONENTS=%d" % counts["fixture_only_components"])
    print("FIXTURE_PLAN_NETS=%d" % counts["nets"])
    print("FIXTURE_PLAN_ENDPOINTS=%d" % counts["endpoints"])
    print("FIXTURE_PLAN_HIGH_FANOUT_NETS=%d" % counts["high_fanout_nets"])
    print("FIXTURE_PLAN_EXPLICIT_WIRE_NETS=%d" % counts["explicit_wire_nets"])
    print("FIXTURE_PLAN_DOMAINS=%d/%d" % (counts["domains"], len(REQUIRED_DOMAINS)))
    print("FIXTURE_PLAN_MAJOR_ROLES=%d/%d" % (counts["major_roles"], len(REQUIRED_MAJOR_ROLES)))
    for failure in failures:
        print("FAIL: %s" % failure)
    print("SINGLE_SHEET_QUALIFICATION_PLAN=%s" % ("FAIL" if failures else "PASS"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
