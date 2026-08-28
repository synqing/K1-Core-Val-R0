#!/usr/bin/env python3

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("single_schematic_check", HERE / "check_single_schematic.py")
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class SingleSchematicCheckerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline_path = CHECKER.DEFAULT_READBACK
        cls.baseline = json.loads(cls.baseline_path.read_text())

    def run_mutant(self, records: list[dict]) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutant.json"
            path.write_text(json.dumps(records))
            with self.assertRaises(CHECKER.CheckError):
                CHECKER.check(path)

    def test_current_canonical_readback(self) -> None:
        summary = CHECKER.check(self.baseline_path, "389936:080d43fd")
        self.assertEqual(summary["unique_designators"], 181)
        self.assertEqual(summary["rectangles"], 10)

    def test_missing_source_record_fails_closed(self) -> None:
        mutant = [item for item in copy.deepcopy(self.baseline) if item.get("tag") != "source"]
        self.run_mutant(mutant)

    def test_second_page_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.baseline)
        objects = next(item for item in mutant if item.get("tag") == "project_objects")["result"]
        page = copy.deepcopy(objects["schematics"][0]["page"][0])
        page["uuid"] = "mutant-second-page"
        objects["schematics"][0]["page"].append(page)
        self.run_mutant(mutant)

    def test_bad_domain_suffix_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.baseline)
        source = next(item for item in mutant if item.get("tag") == "source")["result"]
        source["source"] = source["source"].replace('"C1-PWR1"', '"C1-BAD"', 1)
        self.run_mutant(mutant)

    def test_missing_domain_rectangle_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.baseline)
        source = next(item for item in mutant if item.get("tag") == "source")["result"]
        lines = source["source"].splitlines()
        source["source"] = "\n".join(line for line in lines if not line.startswith('["RECT","e62"'))
        self.run_mutant(mutant)

    def test_stale_hash_is_rejected(self) -> None:
        with self.assertRaises(CHECKER.CheckError):
            CHECKER.check(self.baseline_path, "stale:deadbeef")


if __name__ == "__main__":
    unittest.main()
