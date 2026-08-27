#!/usr/bin/env python3
"""Behavioural tests for the EasyEDA mutation write lock."""

from __future__ import annotations

import json
import struct
import tempfile
import threading
import unittest
import zlib
from pathlib import Path

import easyeda_mutation_gate as gate


PROJECT = "09e9c541fd3d404082d4b92e55ae5336"
DOCUMENT = "1991698f35bf4c09b8de4bcf78bd2b7b"


def write_json(path: Path, value: dict) -> Path:
    path.write_text(json.dumps(value, indent=2) + "\n")
    return path


def write_png(path: Path, width: int = 1280, height: int = 720) -> Path:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    raw = b"".join(b"\x00" + b"\xff\xff\xff" * width for _ in range(height))
    payload = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(payload)
    return path


class EasyEdaMutationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.state = self.root / "state.json"
        self.ledger = self.root / "ledger.jsonl"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def snapshot(self, source_hash: str = "100:aaaa") -> Path:
        return write_json(
            self.root / f"snapshot-{source_hash.replace(':', '-')}.json",
            {
                "schema_version": 1,
                "project_uuid": PROJECT,
                "document_uuid": DOCUMENT,
                "source_hash": source_hash,
                "source": "[\"DOCTYPE\",\"SCH\"]",
            },
        )

    def semantic(
        self,
        transaction_id: str,
        pre_hash: str = "100:aaaa",
        post_hash: str = "110:bbbb",
    ) -> Path:
        return write_json(
            self.root / f"{transaction_id}-semantic.json",
            {
                "schema_version": 1,
                "transaction_id": transaction_id,
                "project_uuid": PROJECT,
                "document_uuid": DOCUMENT,
                "pre_source_hash": pre_hash,
                "post_source_hash": post_hash,
                "saved": True,
                "affected": ["U1", "C1"],
                "census": {"components": 2, "wires": 4, "nets": 3},
            },
        )

    def visual(
        self,
        transaction_id: str,
        intended_delta: str,
        verdict: str = "ACCEPTED",
        checks: int = 4,
    ) -> Path:
        screenshot = write_png(self.root / f"{transaction_id}.png")
        results = "OK" if verdict == "ACCEPTED" else "DEFECT"
        return write_json(
            self.root / f"{transaction_id}-visual.json",
            {
                "schema_version": 1,
                "transaction_id": transaction_id,
                "project_uuid": PROJECT,
                "document_uuid": DOCUMENT,
                "screenshot_path": str(screenshot),
                "captured_after_settle": True,
                "scale": "block",
                "intended_delta": intended_delta,
                "observed_delta": "The declared block-stage delta is visible at readable scale.",
                "unexpected_changes": [] if verdict == "ACCEPTED" else ["Duplicate U1 appeared"],
                "checks": [
                    {"name": f"check-{index}", "result": results, "detail": "inspected"}
                    for index in range(checks)
                ],
                "verdict": verdict,
            },
        )

    def block(self) -> None:
        gate.block_state(
            self.state,
            self.ledger,
            PROJECT,
            DOCUMENT,
            "Current live sheet requires read-only reconciliation",
        )

    def ready(self) -> None:
        self.block()
        transaction_id = "RECONCILE-001"
        semantic = write_json(
            self.root / "reconcile-semantic.json",
            {
                "schema_version": 1,
                "transaction_id": transaction_id,
                "project_uuid": PROJECT,
                "document_uuid": DOCUMENT,
                "source_hash": "100:aaaa",
                "census": {"components": 0, "wires": 0, "nets": 0},
            },
        )
        visual = self.visual(transaction_id, "Read-only reconciliation of current live sheet")
        gate.reconcile_state(self.state, self.ledger, semantic, visual)

    def begin(self, transaction_id: str = "POWER_ENTRY-place-001", kind: str = "normal") -> str:
        intended = "Place the complete POWER_ENTRY circuit block"
        gate.begin_transaction(
            self.state,
            self.ledger,
            transaction_id=transaction_id,
            project_uuid=PROJECT,
            document_uuid=DOCUMENT,
            scope="POWER_ENTRY",
            stage="place" if kind == "normal" else "repair",
            kind=kind,
            intended_delta=intended,
            snapshot_path=self.snapshot("110:bbbb" if kind == "repair" else "100:aaaa"),
            expected_checks=["block visible", "no duplicates", "labels readable", "no unrelated movement"],
            repairs_transaction_id="POWER_ENTRY-place-001" if kind == "repair" else None,
        )
        return intended

    def test_missing_state_never_authorises_write(self) -> None:
        with self.assertRaisesRegex(gate.GateError, "state file is missing"):
            gate.assert_ready(self.state, PROJECT, DOCUMENT)

    def test_blocked_state_refuses_normal_begin(self) -> None:
        self.block()
        with self.assertRaisesRegex(gate.GateError, "BLOCKED_RECONCILIATION"):
            self.begin()

    def test_reconcile_requires_real_screenshot(self) -> None:
        self.block()
        transaction_id = "RECONCILE-001"
        semantic = write_json(
            self.root / "semantic.json",
            {
                "schema_version": 1,
                "transaction_id": transaction_id,
                "project_uuid": PROJECT,
                "document_uuid": DOCUMENT,
                "source_hash": "100:aaaa",
                "census": {"components": 0, "wires": 0, "nets": 0},
            },
        )
        visual = self.visual(transaction_id, "Read-only reconciliation of current live sheet")
        Path(json.loads(visual.read_text())["screenshot_path"]).unlink()
        with self.assertRaisesRegex(gate.GateError, "screenshot is missing"):
            gate.reconcile_state(self.state, self.ledger, semantic, visual)

    def test_reconcile_opens_ready_state(self) -> None:
        self.ready()
        observed = gate.assert_ready(self.state, PROJECT, DOCUMENT)
        self.assertEqual(observed["state"], "READY")

    def test_begin_requires_existing_snapshot(self) -> None:
        self.ready()
        with self.assertRaisesRegex(gate.GateError, "snapshot is missing"):
            gate.begin_transaction(
                self.state,
                self.ledger,
                transaction_id="TX-001",
                project_uuid=PROJECT,
                document_uuid=DOCUMENT,
                scope="POWER_ENTRY",
                stage="place",
                kind="normal",
                intended_delta="Place POWER_ENTRY",
                snapshot_path=self.root / "missing.json",
                expected_checks=["a", "b", "c", "d"],
            )

    def test_second_begin_is_refused(self) -> None:
        self.ready()
        self.begin()
        with self.assertRaisesRegex(gate.GateError, "IN_FLIGHT"):
            self.begin("POWER_SENSE-place-001")

    def test_concurrent_begins_are_serialised(self) -> None:
        self.ready()
        barrier = threading.Barrier(3)
        outcomes: list[str] = []

        def attempt(transaction_id: str) -> None:
            barrier.wait()
            try:
                self.begin(transaction_id)
                outcomes.append("opened")
            except gate.GateError:
                outcomes.append("refused")

        first = threading.Thread(target=attempt, args=("POWER_ENTRY-place-001",))
        second = threading.Thread(target=attempt, args=("POWER_SENSE-place-001",))
        first.start()
        second.start()
        barrier.wait()
        first.join()
        second.join()
        self.assertEqual(sorted(outcomes), ["opened", "refused"])

    def test_unchanged_source_rejects_claimed_mutation(self) -> None:
        self.ready()
        self.begin()
        semantic = self.semantic("POWER_ENTRY-place-001", post_hash="100:aaaa")
        with self.assertRaisesRegex(gate.GateError, "source hash did not change"):
            gate.record_mutation(self.state, self.ledger, semantic)

    def test_wrong_semantic_identity_is_refused(self) -> None:
        self.ready()
        self.begin()
        semantic = self.semantic("POWER_ENTRY-place-001")
        data = json.loads(semantic.read_text())
        data["document_uuid"] = "wrong"
        write_json(semantic, data)
        with self.assertRaisesRegex(gate.GateError, "document_uuid mismatch"):
            gate.record_mutation(self.state, self.ledger, semantic)

    def test_record_mutation_waits_for_visual_evidence(self) -> None:
        self.ready()
        self.begin()
        gate.record_mutation(self.state, self.ledger, self.semantic("POWER_ENTRY-place-001"))
        state = json.loads(self.state.read_text())
        self.assertEqual(state["state"], "AWAITING_EVIDENCE")
        with self.assertRaisesRegex(gate.GateError, "AWAITING_EVIDENCE"):
            gate.assert_ready(self.state, PROJECT, DOCUMENT)

    def test_close_requires_four_granular_checks(self) -> None:
        self.ready()
        intended = self.begin()
        gate.record_mutation(self.state, self.ledger, self.semantic("POWER_ENTRY-place-001"))
        with self.assertRaisesRegex(gate.GateError, "at least four"):
            gate.close_transaction(
                self.state,
                self.ledger,
                self.visual("POWER_ENTRY-place-001", intended, checks=3),
            )

    def test_close_refuses_non_png_screenshot(self) -> None:
        self.ready()
        intended = self.begin()
        gate.record_mutation(self.state, self.ledger, self.semantic("POWER_ENTRY-place-001"))
        visual = self.visual("POWER_ENTRY-place-001", intended)
        visual_data = json.loads(visual.read_text())
        Path(visual_data["screenshot_path"]).write_text("not an image")
        with self.assertRaisesRegex(gate.GateError, "not a PNG"):
            gate.close_transaction(self.state, self.ledger, visual)

    def test_close_refuses_accepted_record_with_defect(self) -> None:
        self.ready()
        intended = self.begin()
        gate.record_mutation(self.state, self.ledger, self.semantic("POWER_ENTRY-place-001"))
        visual = self.visual("POWER_ENTRY-place-001", intended)
        visual_data = json.loads(visual.read_text())
        visual_data["checks"][0]["result"] = "DEFECT"
        write_json(visual, visual_data)
        with self.assertRaisesRegex(gate.GateError, "every granular check"):
            gate.close_transaction(self.state, self.ledger, visual)

    def test_accepted_evidence_returns_ready(self) -> None:
        self.ready()
        intended = self.begin()
        gate.record_mutation(self.state, self.ledger, self.semantic("POWER_ENTRY-place-001"))
        gate.close_transaction(
            self.state,
            self.ledger,
            self.visual("POWER_ENTRY-place-001", intended),
        )
        self.assertEqual(gate.assert_ready(self.state, PROJECT, DOCUMENT)["state"], "READY")

    def test_rejection_blocks_normal_work_and_allows_repair(self) -> None:
        self.ready()
        intended = self.begin()
        gate.record_mutation(self.state, self.ledger, self.semantic("POWER_ENTRY-place-001"))
        gate.close_transaction(
            self.state,
            self.ledger,
            self.visual("POWER_ENTRY-place-001", intended, verdict="REJECTED"),
        )
        with self.assertRaisesRegex(gate.GateError, "only a repair transaction"):
            self.begin("POWER_SENSE-place-001")
        self.begin("POWER_ENTRY-repair-001", kind="repair")
        self.assertEqual(json.loads(self.state.read_text())["state"], "IN_FLIGHT")

    def test_abort_requires_unchanged_source_and_restores_ready(self) -> None:
        self.ready()
        self.begin()
        gate.abort_unchanged(self.state, self.ledger, "POWER_ENTRY-place-001", "100:aaaa")
        self.assertEqual(gate.assert_ready(self.state, PROJECT, DOCUMENT)["state"], "READY")

    def test_executor_has_no_all_mutation_mode_and_uses_gate(self) -> None:
        executor = (
            Path(__file__).parents[1]
            / "schematic"
            / "single-sheet-qualification"
            / "execute_fixture_block.py"
        ).read_text()
        self.assertNotIn('"all"', executor)
        self.assertIn("begin_transaction", executor)
        self.assertIn("record_mutation", executor)
        self.assertIn("EASYEDA-MUTATION-STATE.json", executor)

    def test_repo_canon_wires_the_gate_into_agent_authority(self) -> None:
        repo = Path(__file__).parents[1]
        agents = (repo / "AGENTS.md").read_text()
        decision = (repo / "authority/01-DECISION-REGISTER.md").read_text()
        canon = (repo / "docs/agent/EASYEDA-EXECUTION-CANON.md").read_text()
        self.assertIn("easyeda_mutation_gate.py", agents)
        self.assertIn("D-038", decision)
        self.assertIn("K1E-060", canon)

    def test_validator_rejects_state_ledger_hash_disagreement(self) -> None:
        self.ready()
        state = json.loads(self.state.read_text())
        state["current_source_hash"] = "999:tampered"
        write_json(self.state, state)
        with self.assertRaisesRegex(gate.GateError, "replayed source hash"):
            gate.validate_repository_state(self.state, self.ledger)

    def test_quarantine_establishes_a_new_closed_trust_boundary(self) -> None:
        self.ready()
        state = json.loads(self.state.read_text())
        state["current_source_hash"] = "999:tampered"
        write_json(self.state, state)
        gate.quarantine_state(self.state, self.ledger, "state and ledger disagree")
        validation = gate.validate_repository_state(self.state, self.ledger)
        self.assertEqual(validation["state"]["state"], "BLOCKED_RECONCILIATION")
        self.assertEqual(validation["terminal_event"], "STATE_QUARANTINED")

    def test_incident_freeze_has_no_automatic_reconciliation_path(self) -> None:
        self.ready()
        gate.freeze_incident(self.state, self.ledger, "competing live operator")
        validation = gate.validate_repository_state(self.state, self.ledger)
        self.assertEqual(validation["state"]["state"], "FROZEN_INCIDENT")
        self.assertEqual(validation["terminal_event"], "STATE_FROZEN")
        with self.assertRaisesRegex(gate.GateError, "requires BLOCKED_RECONCILIATION"):
            gate.reconcile_state(
                self.state,
                self.ledger,
                self.root / "not-used-semantic.json",
                self.root / "not-used-visual.json",
            )
        with self.assertRaisesRegex(gate.GateError, "FROZEN_INCIDENT"):
            self.begin()


if __name__ == "__main__":
    unittest.main(verbosity=2)
