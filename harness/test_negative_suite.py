#!/usr/bin/env python3
"""Disposable negative suite for the two VAL-G0 authority harnesses."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AUTHORITY_CHECKER = "harness/check_authority_consistency.py"
TERMINOLOGY_CHECKER = "harness/check_terminology.py"

# id, description, checker, mutation, path, old text, new text, expected failure
CASES = [
    (
        "N1", "ESP32_S3 assigned audio_capture", AUTHORITY_CHECKER, "replace",
        "authority/03-OWNERSHIP-MATRIX.csv",
        "audio_capture,RT1062,RATIFIED", "audio_capture,ESP32_S3,RATIFIED",
        "ownership matrix: audio_capture must be owned by RT1062, found ESP32_S3",
    ),
    (
        "N2", "ownership matrix emptied", AUTHORITY_CHECKER, "header_only",
        "authority/03-OWNERSHIP-MATRIX.csv", None, None,
        "ownership matrix parsed zero rows",
    ),
    (
        "N3", "required contract deleted", AUTHORITY_CHECKER, "delete",
        "contracts/nfc-interface.md", None, None,
        "required authority file missing: contracts/nfc-interface.md",
    ),
    (
        "N4", "K1BR permits RAW_PCM", AUTHORITY_CHECKER, "replace",
        "contracts/k1br-bridge.md", "  - RAW_PCM\n", "",
        "K1BR does not forbid required payload class: RAW_PCM",
    ),
    (
        "N5", "affirmative RT1062 hardware-PDM claim", AUTHORITY_CHECKER, "append",
        "architecture/CLOCK-ARCHITECTURE.md", None,
        "\nRT1062 provides native PDM hardware decimation via MICFIL.\n",
        "affirmative RT1062 hardware-PDM claim",
    ),
    (
        "N6", "bare AP in a Wi-Fi context", TERMINOLOGY_CHECKER, "append",
        "architecture/CLOCK-ARCHITECTURE.md", None,
        "\nThe S3 runs in AP mode over Wi-Fi for service access.\n",
        "bare 'AP' in a Wi-Fi context",
    ),
    (
        "N7", "WebSocket marked current", TERMINOLOGY_CHECKER, "append",
        "project.yaml", None, "\nwebsocket_control: CURRENT\n",
        "Wi-Fi/REST/WebSocket marked current",
    ),
    (
        "N8", "audio_capture owner changed to UNRESOLVED", AUTHORITY_CHECKER, "replace",
        "authority/03-OWNERSHIP-MATRIX.csv",
        "audio_capture,RT1062,RATIFIED", "audio_capture,UNRESOLVED,RATIFIED",
        "ownership matrix: audio_capture must be owned by RT1062, found UNRESOLVED",
    ),
    (
        "N9", "audio_processing status changed to OPEN", AUTHORITY_CHECKER, "replace",
        "authority/03-OWNERSHIP-MATRIX.csv",
        "audio_processing,RT1062,RATIFIED", "audio_processing,RT1062,OPEN",
        "ownership matrix: audio_processing status must be RATIFIED, found OPEN",
    ),
    (
        "N10", "nfc_frontend owner changed to ESP32_S3", AUTHORITY_CHECKER, "replace",
        "authority/03-OWNERSHIP-MATRIX.csv",
        "nfc_frontend,K1_CARRIER,RATIFIED", "nfc_frontend,ESP32_S3,RATIFIED",
        "ownership matrix: nfc_frontend must be owned by K1_CARRIER, found ESP32_S3",
    ),
    (
        "N11", "render reassigned to K1_CARRIER", AUTHORITY_CHECKER, "replace",
        "authority/03-OWNERSHIP-MATRIX.csv",
        "render,RT1062,RATIFIED", "render,K1_CARRIER,RATIFIED",
        "ownership matrix: render must be owned by RT1062, found K1_CARRIER",
    ),
    (
        "N12", "led_output reassigned to EXPERIMENT_ONLY", AUTHORITY_CHECKER, "replace",
        "authority/03-OWNERSHIP-MATRIX.csv",
        "led_output,RT1062,RATIFIED", "led_output,EXPERIMENT_ONLY,RATIFIED",
        "ownership matrix: led_output must be owned by RT1062, found EXPERIMENT_ONLY",
    ),
    (
        "N13", "required ownership key removed from project.yaml", AUTHORITY_CHECKER, "replace",
        "project.yaml", "  mic_power_enable: RT1062\n", "",
        "project.yaml ownership block is missing required function: mic_power_enable",
    ),
    (
        "N14", "supersession exemption used outside permitted documents", TERMINOLOGY_CHECKER,
        "append", "contracts/audio-interface.md", None,
        "\nSome text with a bogus AP-only Wi-Fi claim [quoted-superseded]\n",
        "[quoted-superseded] is not permitted outside",
    ),
    (
        "N15", "STATUS recovery mismatch", AUTHORITY_CHECKER, "replace", "STATUS.md",
        "SSCM1_RECOVERY_STATE = COMPLETE_NOT_FOUND", "SSCM1_RECOVERY_STATE = NOT_RUN",
        "STATUS.md SSCM1_RECOVERY_STATE must be COMPLETE_NOT_FOUND, found NOT_RUN",
    ),
    (
        "N16", "contract recovery mismatch", AUTHORITY_CHECKER, "replace",
        "contracts/sscm1-v2/STATUS.md",
        "SSCM1_RECOVERY_STATE = COMPLETE_NOT_FOUND", "SSCM1_RECOVERY_STATE = OUTSTANDING",
        "contracts/sscm1-v2/STATUS.md SSCM1_RECOVERY_STATE must be COMPLETE_NOT_FOUND, found OUTSTANDING",
    ),
    (
        "N17", "source-register recovery mismatch", AUTHORITY_CHECKER, "replace",
        "sources/SOURCE-REGISTER.md",
        "SSCM1_RECOVERY_STATE = COMPLETE_NOT_FOUND", "SSCM1_RECOVERY_STATE = FOUND",
        "sources/SOURCE-REGISTER.md SSCM1_RECOVERY_STATE must be COMPLETE_NOT_FOUND, found FOUND",
    ),
    (
        "N18", "STATUS prematurely permits EDA execution", AUTHORITY_CHECKER, "replace",
        "STATUS.md",
        "VAL_G2_0_EDA_EXECUTION = BLOCKED_ON_FIXTURE_DEFINITION",
        "VAL_G2_0_EDA_EXECUTION = READY",
        "STATUS.md VAL_G2_0_EDA_EXECUTION must be BLOCKED_ON_FIXTURE_DEFINITION, found READY",
    ),
    (
        "N19", "test plan substitutes a numeric floor for unresolved estimate",
        AUTHORITY_CHECKER, "replace", "schematic/single-sheet-qualification/TEST-PLAN.md",
        "OPTION_C_SYMBOL_ESTIMATE = UNRESOLVED", "OPTION_C_SYMBOL_ESTIMATE = 200",
        "schematic/single-sheet-qualification/TEST-PLAN.md is missing OPTION_C_SYMBOL_ESTIMATE",
    ),
    (
        "N20", "source register prematurely closes fixture definition",
        AUTHORITY_CHECKER, "replace", "sources/SOURCE-REGISTER.md",
        "VAL_G2_0_FIXTURE_DEFINITION = REQUIRED_NOT_COMPLETE",
        "VAL_G2_0_FIXTURE_DEFINITION = COMPLETE",
        "sources/SOURCE-REGISTER.md VAL_G2_0_FIXTURE_DEFINITION must be REQUIRED_NOT_COMPLETE, found COMPLETE",
    ),
    (
        "N21", "project manifest prematurely permits EDA execution",
        AUTHORITY_CHECKER, "replace", "project.yaml",
        "  val_g2_0_eda_execution: BLOCKED_ON_FIXTURE_DEFINITION",
        "  val_g2_0_eda_execution: READY",
        "project.yaml eda.val_g2_0_eda_execution must be BLOCKED_ON_FIXTURE_DEFINITION, found READY",
    ),
]


def run_checker(root, checker):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, checker],
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def mutate(root, mode, rel, old, new):
    target = root / rel
    if mode == "delete":
        target.unlink()
        return
    text = target.read_text(encoding="utf-8")
    if mode == "header_only":
        target.write_text(text.splitlines()[0] + "\n", encoding="utf-8")
        return
    if mode == "append":
        target.write_text(text + new, encoding="utf-8")
        return
    if mode == "replace":
        if text.count(old) != 1:
            raise RuntimeError("%s replacement count for %r is %d" % (rel, old, text.count(old)))
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
        return
    raise RuntimeError("unknown mutation mode: %s" % mode)


for checker in (AUTHORITY_CHECKER, TERMINOLOGY_CHECKER):
    baseline = run_checker(ROOT, checker)
    if baseline.returncode != 0:
        print("BASELINE=FAIL checker=%s" % checker)
        print(baseline.stdout.rstrip())
        sys.exit(1)
print("BASELINES=PASS authority=1 terminology=1")

passed = 0
for case_id, description, checker, mode, rel, old, new, expected in CASES:
    with tempfile.TemporaryDirectory(prefix="k1-negative-") as temp_dir:
        temp_root = Path(temp_dir) / "repo"
        shutil.copytree(
            ROOT,
            temp_root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "evidence"),
        )
        try:
            mutate(temp_root, mode, rel, old, new)
        except (OSError, RuntimeError) as exc:
            print("%s RESULT=SETUP_FAIL description=%s" % (case_id, description))
            print(str(exc))
            sys.exit(1)

        result = run_checker(temp_root, checker)
        if result.returncode == 0 or expected not in result.stdout:
            print("%s RESULT=FAIL description=%s" % (case_id, description))
            print(result.stdout.rstrip())
            sys.exit(1)

        passed += 1
        print("%s RESULT=CORRECTLY_FAILED description=%s" % (case_id, description))

print("NEGATIVE_CASES=%d/%d" % (passed, len(CASES)))
print("NEGATIVE_SUITE=PASS")
