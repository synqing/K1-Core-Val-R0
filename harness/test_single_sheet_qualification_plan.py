#!/usr/bin/env python3
"""Non-vacuity tests for the VAL-G2.0 semantic fixture-plan gate."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))

from check_single_sheet_qualification_plan import (  # noqa: E402
    REQUIRED_DOMAINS,
    validate_plan,
)


def valid_plan() -> dict:
    domain_order = sorted(REQUIRED_DOMAINS)
    major_specs = [
        ("U_RT", "rt1062", "RT1062_SUPPORT", "processor"),
        ("U_S3", "esp32_s3", "ESP32_S3_SUPPORT", "processor"),
        ("U_AUDIO", "audio_frontend", "AUDIO", "major_ic"),
        ("U_NFC", "nfc_frontend", "NFC", "major_ic"),
        ("U_MOTION", "accelerometer", "MOTION", "major_ic"),
        ("J_POWER", "power_entry", "POWER", "power"),
    ]
    support_specs = [
        ("U_BRIDGE", "k1br_bridge", "K1BR", "support_ic"),
        ("J_LED", "led_connector", "LED", "connector"),
        ("J_USB", "service_usb_connector", "USB", "connector"),
        ("J_DEBUG", "debug_connector", "DEBUG", "connector"),
        ("R_OPTION", "option_link", "OPTIONS", "option"),
    ]
    components = []
    for ref, role, domain, component_class in major_specs + support_specs:
        components.append({
            "ref": ref,
            "role": role,
            "domain": domain,
            "class": component_class,
            "basis": "source-derived Option-C architecture role",
            "fixture_only": False,
        })
    while len(components) < 166:
        index = len(components) + 1
        components.append({
            "ref": "C%d" % index,
            "role": "decoupler",
            "domain": domain_order[index % len(domain_order)],
            "class": "passive",
            "basis": "source-derived rail decoupling/support quantity",
            "fixture_only": False,
        })
    while len(components) < 200:
        index = len(components) + 1
        components.append({
            "ref": "T%d" % index,
            "role": "stress_passive",
            "domain": domain_order[index % len(domain_order)],
            "class": "passive",
            "basis": "20 percent qualification stress margin",
            "fixture_only": True,
            "stress_basis": "extra passive loading preserves real symbol and local-wire complexity",
        })

    component_by_domain = {}
    for component in components:
        component_by_domain.setdefault(component["domain"], component["ref"])
    passive_refs = [component["ref"] for component in components if component["class"] == "passive"]
    major_refs = [spec[0] for spec in major_specs]

    nets = []
    for index in range(10):
        active_ref = major_refs[index % len(major_refs)]
        nets.append({
            "name": "+RAIL_%02d" % (index + 1),
            "kind": "power",
            "render": "explicit_wire",
            "high_fanout": True,
            "endpoints": [
                {"ref": active_ref, "pin": "PWR%d" % index},
                {"ref": passive_refs[index * 3], "pin": "1"},
                {"ref": passive_refs[index * 3 + 1], "pin": "1"},
                {"ref": passive_refs[index * 3 + 2], "pin": "1"},
            ],
        })

    for index, active_ref in enumerate(major_refs[:-1]):
        nets.append({
            "name": "FUNC_%02d" % (index + 1),
            "kind": "signal",
            "render": "explicit_wire",
            "high_fanout": False,
            "endpoints": [
                {"ref": active_ref, "pin": "IO%d" % index},
                {"ref": passive_refs[40 + index], "pin": "2"},
            ],
        })

    domain_refs = [component_by_domain[domain] for domain in domain_order]
    while len(nets) < 120:
        index = len(nets)
        left = domain_refs[index % len(domain_refs)]
        right = passive_refs[(index * 2) % len(passive_refs)]
        if left == right:
            right = passive_refs[(index * 2 + 1) % len(passive_refs)]
        nets.append({
            "name": "SIG_%03d" % (index + 1),
            "kind": "signal",
            "render": "explicit_wire",
            "high_fanout": False,
            "endpoints": [
                {"ref": left, "pin": "A%d" % index},
                {"ref": right, "pin": "B%d" % index},
            ],
        })

    return {
        "schema_version": 1,
        "plan_state": "READY_FOR_EDA",
        "project_name": "K1-CORE-VAL-SINGLE-SHEET-QUAL",
        "option_c_estimated_symbols": 166,
        "planned_symbols": 200,
        "estimate_sources": [
            "authority/03-OWNERSHIP-MATRIX.csv",
            "contracts/*.md",
            "primary vendor support requirements",
        ],
        "components": components,
        "nets": nets,
        "power_tree_nets": [net["name"] for net in nets[:4]],
        "stub_only_wiring": False,
    }


class QualificationPlanTests(unittest.TestCase):
    def assert_fails_with(self, plan: dict, expected: str) -> None:
        failures, _ = validate_plan(plan)
        self.assertTrue(any(expected in failure for failure in failures), failures)

    def test_valid_source_derived_plan_passes(self) -> None:
        failures, counts = validate_plan(valid_plan())
        self.assertEqual([], failures)
        self.assertEqual(200, counts["components"])
        self.assertEqual(120, counts["nets"])
        self.assertEqual(10, counts["high_fanout_nets"])

    def test_unresolved_estimate_fails(self) -> None:
        plan = valid_plan()
        plan["option_c_estimated_symbols"] = "UNRESOLVED"
        self.assert_fails_with(plan, "resolved positive integer")

    def test_count_below_formula_fails(self) -> None:
        plan = valid_plan()
        plan["components"] = plan["components"][:-1]
        plan["planned_symbols"] = len(plan["components"])
        self.assert_fails_with(plan, "below required N_test")

    def test_placeholder_role_fails(self) -> None:
        plan = valid_plan()
        plan["components"][20]["role"] = "padding_resistor"
        self.assert_fails_with(plan, "placeholder/count-padding role")

    def test_fixture_only_functional_duplicate_fails(self) -> None:
        plan = valid_plan()
        plan["components"][-1]["class"] = "major_ic"
        self.assert_fails_with(plan, "may not duplicate a functional IC")

    def test_one_endpoint_named_net_fails(self) -> None:
        plan = valid_plan()
        plan["nets"][20]["endpoints"] = plan["nets"][20]["endpoints"][:1]
        self.assert_fails_with(plan, "fewer than two distinct component-pin endpoints")

    def test_passive_only_high_fanout_fails(self) -> None:
        plan = valid_plan()
        passive_refs = [
            component["ref"] for component in plan["components"]
            if component["class"] == "passive"
        ]
        plan["nets"][0]["endpoints"] = [
            {"ref": ref, "pin": "1"} for ref in passive_refs[:4]
        ]
        self.assert_fails_with(plan, "no active/source IC endpoint")

    def test_unpowered_major_component_fails(self) -> None:
        plan = valid_plan()
        for net in plan["nets"]:
            if net["kind"] in {"power", "ground"}:
                net["endpoints"] = [endpoint for endpoint in net["endpoints"] if endpoint["ref"] != "U_RT"]
        self.assert_fails_with(plan, "major component U_RT has no planned power/ground endpoint")

    def test_stub_only_wiring_fails(self) -> None:
        plan = valid_plan()
        plan["stub_only_wiring"] = True
        self.assert_fails_with(plan, "stub_only_wiring must be explicitly false")

    def test_no_explicit_wiring_fails(self) -> None:
        plan = valid_plan()
        for net in plan["nets"]:
            net["render"] = "labelled_net"
        self.assert_fails_with(plan, "at least 20 explicitly wired nets")

    def test_missing_required_domain_fails(self) -> None:
        plan = valid_plan()
        for component in plan["components"]:
            if component["domain"] == "DEBUG":
                component["domain"] = "OPTIONS"
        self.assert_fails_with(plan, "required domain has zero components: DEBUG")

    def test_zero_records_fail_closed(self) -> None:
        plan = valid_plan()
        plan["components"] = []
        plan["planned_symbols"] = 0
        plan["nets"] = []
        self.assert_fails_with(plan, "components parsed zero records")
        self.assert_fails_with(plan, "nets parsed zero records")


if __name__ == "__main__":
    unittest.main(verbosity=2)
