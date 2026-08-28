#!/usr/bin/env python3
"""Non-vacuity tests for the VAL-G2.0 semantic fixture-plan gate."""

from __future__ import annotations

import copy
import sys
import unittest
from collections import Counter
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
    component_index = 0
    domain_positions = Counter()
    for ref, role, domain, component_class in major_specs + support_specs:
        component_index += 1
        domain_positions[domain] += 1
        components.append({
            "ref": ref,
            "role": role,
            "domain": domain,
            "class": component_class,
            "basis": "source-derived Option-C architecture role",
            "fixture_only": False,
            "manufacturer_part_number": "TEST-%s" % ref,
            "value": "FITTED",
            "device_uuid": "%032x" % component_index,
            "library_uuid": "%032x" % (1000 + component_index),
            "source_ref": {
                "document": "primary-source-test-fixture",
                "revision": "test-rev-a",
                "locator": "circuit-role-%s" % role,
                "url_or_path": "https://example.invalid/primary-source-test-fixture",
                "requirement_type": "REFERENCE_DESIGN_REQUIRED",
            },
            "placement_group": domain,
            "placement": {
                "x": domain_order.index(domain) * 1000 + domain_positions[domain] * 30,
                "y": 100 + domain_positions[domain] * 20,
                "rotation": 0,
                "rationale": "Place beside the functional source and its local support path",
            },
        })
    while len(components) < 166:
        index = len(components) + 1
        component_index += 1
        domain = domain_order[index % len(domain_order)]
        domain_positions[domain] += 1
        components.append({
            "ref": "C%d" % index,
            "role": "decoupler",
            "domain": domain,
            "class": "passive",
            "basis": "source-derived rail decoupling/support quantity",
            "fixture_only": False,
            "manufacturer_part_number": "TEST-CAP-%03d" % index,
            "value": "100nF",
            "device_uuid": "%032x" % component_index,
            "library_uuid": "%032x" % (1000 + component_index),
            "source_ref": {
                "document": "primary-source-test-fixture",
                "revision": "test-rev-a",
                "locator": "decoupling-table-row-%03d" % index,
                "url_or_path": "https://example.invalid/primary-source-test-fixture",
                "requirement_type": "DATASHEET_REQUIRED",
            },
            "placement_group": domain,
            "placement": {
                "x": domain_order.index(domain) * 1000 + domain_positions[domain] * 30,
                "y": 100 + domain_positions[domain] * 20,
                "rotation": 0,
                "rationale": "Place beside the rail endpoint it decouples",
            },
        })
    while len(components) < 200:
        index = len(components) + 1
        component_index += 1
        domain = domain_order[index % len(domain_order)]
        domain_positions[domain] += 1
        components.append({
            "ref": "T%d" % index,
            "role": "stress_passive",
            "domain": domain,
            "class": "passive",
            "basis": "20 percent qualification stress margin",
            "fixture_only": True,
            "stress_basis": "extra passive loading preserves real symbol and local-wire complexity",
            "manufacturer_part_number": "TEST-STRESS-CAP-%03d" % index,
            "value": "100nF",
            "device_uuid": "%032x" % component_index,
            "library_uuid": "%032x" % (1000 + component_index),
            "source_ref": {
                "document": "qualification-stress-contract",
                "revision": "test-rev-a",
                "locator": "passive-margin-%03d" % index,
                "url_or_path": "schematic/single-sheet-qualification/TEST-PLAN.md",
                "requirement_type": "DERIVED",
            },
            "placement_group": domain,
            "placement": {
                "x": domain_order.index(domain) * 1000 + domain_positions[domain] * 30,
                "y": 100 + domain_positions[domain] * 20,
                "rotation": 0,
                "rationale": "Place on the real rail branch whose edit load is stressed",
            },
        })

    component_by_domain = {}
    refs_by_domain = {}
    for component in components:
        component_by_domain.setdefault(component["domain"], component["ref"])
        refs_by_domain.setdefault(component["domain"], []).append(component["ref"])
    passive_refs = [component["ref"] for component in components if component["class"] == "passive"]
    major_refs = [spec[0] for spec in major_specs]
    component_by_ref = {component["ref"]: component for component in components}
    pin_counter = Counter()

    def endpoint(ref: str) -> dict:
        pin_counter[ref] += 1
        return {
            "ref": ref,
            "pin": str(pin_counter[ref]),
            "pin_name": "PIN_%d" % pin_counter[ref],
        }

    def source_ref(locator: str) -> dict:
        return {
            "document": "primary-source-test-fixture",
            "revision": "test-rev-a",
            "locator": locator,
            "url_or_path": "https://example.invalid/primary-source-test-fixture",
        }

    nets = []
    for index in range(10):
        active_ref = major_refs[index % len(major_refs)]
        nets.append({
            "name": "+RAIL_%02d" % (index + 1),
            "kind": "power",
            "render": "explicit_wire",
            "high_fanout": True,
            "source_ref": source_ref("rail-%02d" % (index + 1)),
            "endpoints": [endpoint(active_ref)] + [
                endpoint(passive_refs[index * 3 + offset]) for offset in range(3)
            ],
        })

    for index, active_ref in enumerate(major_refs[:-1]):
        nets.append({
            "name": "CONTROL_INTERFACE_%02d" % (index + 1),
            "kind": "signal",
            "render": "explicit_wire",
            "high_fanout": False,
            "source_ref": source_ref("control-interface-%02d" % (index + 1)),
            "endpoints": [endpoint(active_ref), endpoint(passive_refs[40 + index])],
        })

    for domain in domain_order:
        domain_refs = refs_by_domain[domain]
        left = domain_refs[0]
        right = domain_refs[1]
        nets.append({
            "name": "%s_DOMAIN_CONTROL" % domain,
            "kind": "control",
            "render": "explicit_wire",
            "high_fanout": False,
            "source_ref": source_ref("%s-domain-control" % domain.lower()),
            "endpoints": [endpoint(left), endpoint(right)],
        })

    required_pins = {
        component["ref"]: 2 if component["class"] in {"passive", "protection", "option"} else 1
        for component in components
    }
    pending = []
    for component in components:
        ref = component["ref"]
        pending.extend([ref] * max(0, required_pins[ref] - pin_counter[ref]))
    if len(pending) % 2:
        pending.append(major_refs[0])
    for index in range(0, len(pending), 2):
        left, right = pending[index], pending[index + 1]
        if left == right:
            replacement_index = next(
                (candidate for candidate in range(index + 2, len(pending)) if pending[candidate] != left),
                None,
            )
            if replacement_index is not None:
                pending[index + 1], pending[replacement_index] = pending[replacement_index], right
                right = pending[index + 1]
        nets.append({
            "name": "CIRCUIT_PATH_%03d" % (index // 2 + 1),
            "kind": "signal",
            "render": "explicit_wire",
            "high_fanout": False,
            "source_ref": source_ref("circuit-path-%03d" % (index // 2 + 1)),
            "endpoints": [endpoint(left), endpoint(right)],
        })

    blocks = []
    for domain in domain_order:
        domain_refs = set(refs_by_domain[domain])
        domain_nets = [
            net["name"] for net in nets
            if any(endpoint_record["ref"] in domain_refs for endpoint_record in net["endpoints"])
        ]
        blocks.append({
            "id": "%s_SOURCE_CIRCUIT" % domain,
            "domain": domain,
            "component_refs": sorted(domain_refs),
            "net_names": domain_nets,
            "placement_intent": "Place supply and protection at the source side, active device centrally, and loads at the destination side",
            "source_ref": source_ref("%s-source-circuit" % domain.lower()),
            "bounds": {
                "x1": domain_order.index(domain) * 1000,
                "y1": 0,
                "x2": domain_order.index(domain) * 1000 + 900,
                "y2": 900,
            },
        })

    visual_transactions = []
    for transaction_number, block in enumerate(blocks, start=1):
        visual_transactions.append({
            "id": "VISUAL_TRANSACTION_%02d" % transaction_number,
            "block_ids": [block["id"]],
            "component_refs": block["component_refs"],
            "stop_for_screenshot_inspection": True,
            "intended_delta": "Place and wire the complete %s circuit block" % block["id"],
            "screenshot_path": "evidence/VAL-G2-test/transaction-%02d.png" % transaction_number,
            "readback_path": "evidence/VAL-G2-test/transaction-%02d.json" % transaction_number,
            "inspection_criteria": [
                "no duplicate functional symbols",
                "all components remain inside the circuit block",
                "signal flow and power direction are readable",
                "wires touch only their intended endpoints",
            ],
        })

    return {
        "schema_version": 1,
        "plan_state": "READY_FOR_EDA",
        "project_name": "K1-CORE-VAL-SINGLE-SHEET-QUAL",
        "population_method": "CIRCUIT_BLOCKS_FROM_PRIMARY_SOURCES",
        "generic_device_fallback": False,
        "uniform_grid_placement": False,
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
        "blocks": blocks,
        "visual_transactions": visual_transactions,
    }


class QualificationPlanTests(unittest.TestCase):
    def assert_fails_with(self, plan: dict, expected: str) -> None:
        failures, _ = validate_plan(plan)
        self.assertTrue(any(expected in failure for failure in failures), failures)

    def test_valid_source_derived_plan_passes(self) -> None:
        failures, counts = validate_plan(valid_plan())
        self.assertEqual([], failures)
        self.assertEqual(200, counts["components"])
        self.assertGreaterEqual(counts["nets"], 120)
        self.assertEqual(10, counts["high_fanout_nets"])
        self.assertEqual(11, counts["blocks"])
        self.assertEqual(11, counts["visual_transactions"])

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

    def test_generic_device_fallback_fails(self) -> None:
        plan = valid_plan()
        plan["generic_device_fallback"] = True
        self.assert_fails_with(plan, "generic_device_fallback must be explicitly false")

    def test_uniform_grid_placement_fails(self) -> None:
        plan = valid_plan()
        plan["uniform_grid_placement"] = True
        self.assert_fails_with(plan, "uniform_grid_placement must be explicitly false")

    def test_missing_exact_device_identity_fails(self) -> None:
        plan = valid_plan()
        plan["components"][0]["device_uuid"] = ""
        self.assert_fails_with(plan, "exact 32-hex EasyEDA device_uuid")

    def test_missing_exact_library_identity_fails(self) -> None:
        plan = valid_plan()
        plan["components"][0]["library_uuid"] = ""
        self.assert_fails_with(plan, "exact 32-hex EasyEDA library_uuid")

    def test_missing_source_revision_fails(self) -> None:
        plan = valid_plan()
        del plan["components"][0]["source_ref"]["revision"]
        self.assert_fails_with(plan, "source_ref.revision must be non-empty")

    def test_missing_source_location_fails(self) -> None:
        plan = valid_plan()
        del plan["components"][0]["source_ref"]["url_or_path"]
        self.assert_fails_with(plan, "source_ref.url_or_path must be non-empty")

    def test_duplicate_placement_coordinate_fails(self) -> None:
        plan = valid_plan()
        plan["components"][1]["placement"] = copy.deepcopy(plan["components"][0]["placement"])
        self.assert_fails_with(plan, "share placement coordinate")

    def test_component_outside_block_bounds_fails(self) -> None:
        plan = valid_plan()
        ref = plan["blocks"][0]["component_refs"][0]
        component = next(component for component in plan["components"] if component["ref"] == ref)
        component["placement"]["x"] = 999999
        self.assert_fails_with(plan, "lies outside block")

    def test_active_device_reused_for_different_roles_fails(self) -> None:
        plan = valid_plan()
        plan["components"][1]["device_uuid"] = plan["components"][0]["device_uuid"]
        self.assert_fails_with(plan, "reused across distinct roles without justification")

    def test_one_passive_device_uuid_cannot_claim_multiple_values(self) -> None:
        plan = valid_plan()
        passives = [component for component in plan["components"] if component["class"] == "passive"]
        passives[1]["device_uuid"] = passives[0]["device_uuid"]
        passives[1]["value"] = "10uF"
        self.assert_fails_with(plan, "assigned multiple values")

    def test_generated_chain_net_name_fails(self) -> None:
        plan = valid_plan()
        plan["nets"][20]["name"] = "RT_LINK_001"
        self.assert_fails_with(plan, "generated chain/count topology naming")

    def test_component_pin_assigned_to_two_nets_fails(self) -> None:
        plan = valid_plan()
        reused = copy.deepcopy(plan["nets"][0]["endpoints"][0])
        plan["nets"][1]["endpoints"][0] = reused
        self.assert_fails_with(plan, "assigned to multiple nets")

    def test_missing_circuit_block_coverage_fails(self) -> None:
        plan = valid_plan()
        missing_ref = plan["components"][0]["ref"]
        for block in plan["blocks"]:
            block["component_refs"] = [ref for ref in block["component_refs"] if ref != missing_ref]
        self.assert_fails_with(plan, "components missing source circuit-block coverage")

    def test_visual_transaction_over_40_components_fails(self) -> None:
        plan = valid_plan()
        plan["visual_transactions"][0]["component_refs"] = [
            component["ref"] for component in plan["components"][:41]
        ]
        self.assert_fails_with(plan, "exceeds 40-component visual transaction limit")

    def test_visual_transaction_without_screenshot_stop_fails(self) -> None:
        plan = valid_plan()
        plan["visual_transactions"][0]["stop_for_screenshot_inspection"] = False
        self.assert_fails_with(plan, "must stop_for_screenshot_inspection")

    def test_visual_transaction_must_cover_complete_block_fails(self) -> None:
        plan = valid_plan()
        plan["visual_transactions"][0]["component_refs"] = \
            plan["visual_transactions"][0]["component_refs"][:-1]
        self.assert_fails_with(plan, "complete union of its block_ids")

    def test_visual_transaction_missing_readback_path_fails(self) -> None:
        plan = valid_plan()
        plan["visual_transactions"][0]["readback_path"] = ""
        self.assert_fails_with(plan, "must name readback_path")

    def test_visual_transaction_missing_inspection_criteria_fails(self) -> None:
        plan = valid_plan()
        plan["visual_transactions"][0]["inspection_criteria"] = ["duplicates"]
        self.assert_fails_with(plan, "at least four inspection_criteria")


if __name__ == "__main__":
    unittest.main(verbosity=2)
