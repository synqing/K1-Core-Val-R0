#!/usr/bin/env python3
"""K1-CORE-VAL-R0 authority consistency check.

This is NOT the DualMCU firmware scanner. That tool inspects firmware source; in this
hardware and documentation repository it would find no source files, iterate over nothing
and pass vacuously. This checker inspects structured authority records instead, and refuses
to print PASS unless it can report non-zero input counts.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILURES = []
COUNTS = {
    "authority_files": 0,
    "ownership_rows": 0,
    "contracts": 0,
    "text_files_scanned": 0,
    "recovery_state_records": 0,
}

try:
    import yaml
except ImportError:
    print("AUTHORITY_CONSISTENCY=FAIL")
    print("reason: PyYAML unavailable; cannot parse structured authority. Failing closed.")
    sys.exit(1)


def fail(msg):
    FAILURES.append(msg)


REQUIRED_FILES = [
    "project.yaml",
    "authority/03-OWNERSHIP-MATRIX.csv",
    "contracts/k1br-bridge.md",
    "contracts/audio-interface.md",
    "contracts/usb-interface.md",
    "contracts/nfc-interface.md",
    "contracts/motion-interface.md",
]

EXPECTED_RECOVERY_STATE = "COMPLETE_NOT_FOUND"
RECOVERY_STATE_FILES = [
    "STATUS.md",
    "contracts/sscm1-v2/STATUS.md",
    "sources/SOURCE-REGISTER.md",
]
RECOVERY_STATE_RE = re.compile(
    r"^SSCM1_RECOVERY_STATE\s*=\s*([A-Z][A-Z0-9_]*)\s*$", re.MULTILINE
)
STALE_RECOVERY_RE = re.compile(
    r"(?i)(?:SSCM-1\s+recovery\s+pass|recovery\s+pass)[^\n]*"
    r"(?:\bNOT[ _-]?RUN\b|\bOUTSTANDING\b)"
)

# Every function below must appear in BOTH project.yaml and the ownership matrix, with the
# exact owner and status recorded here. The invariant lives in this checker; project.yaml and
# the CSV are the data being checked. That is not duplication to be tidied away later -- remove
# the invariant and the check stops being able to falsify anything.
EXPECTED_OWNER = {
    "audio_capture": "RT1062",
    "audio_processing": "RT1062",
    "gdft_spectral": "RT1062",
    "tempo_onset_saliency": "RT1062",
    "vp": "RT1062",
    "render": "RT1062",
    "pixel_buffers": "RT1062",
    "fastled_adaptation": "RT1062",
    "led_output": "RT1062",
    "audio_clock_master": "RT1062",
    "mic_power_enable": "RT1062",
    "radio": "ESP32_S3",
    "wireless_control": "ESP32_S3",
    "nfc_host": "ESP32_S3",
    "service_usb": "ESP32_S3",
    "nfc_frontend": "K1_CARRIER",
    "usb_audio": "EXPERIMENT_ONLY",
    "debug_fabric_endpoint": "ESP32_S3",
    "rt_reset_request": "ESP32_S3",
    "rt_recovery_request": "ESP32_S3",
}

# Deliberately not pinned: the accelerometer carries a 0R/DNP ownership matrix and may be
# assigned to either MCU during validation. It may never be assigned anywhere else.
UNPINNED_OWNER = {
    "accelerometer": {"RT1062", "ESP32_S3"},
}

EXPECTED_STATUS = {
    "audio_capture": "RATIFIED",
    "audio_processing": "RATIFIED",
    "gdft_spectral": "RATIFIED",
    "tempo_onset_saliency": "RATIFIED",
    "vp": "RATIFIED",
    "render": "RATIFIED",
    "pixel_buffers": "RATIFIED",
    "fastled_adaptation": "RATIFIED",
    "led_output": "RATIFIED",
    "radio": "RATIFIED",
    "wireless_control": "RATIFIED",
    "nfc_frontend": "RATIFIED",
    "audio_clock_master": "DEFAULT",
    "mic_power_enable": "DEFAULT",
    "accelerometer": "DEFAULT",
    "nfc_host": "DEFAULT",
    "service_usb": "DEFAULT",
    "usb_audio": "EXPERIMENT",
    "debug_fabric_endpoint": "DEFAULT",
    "rt_reset_request": "DEFAULT",
    "rt_recovery_request": "DEFAULT",
}

REQUIRED_FUNCTIONS = set(EXPECTED_OWNER) | set(UNPINNED_OWNER)

VALID_OWNERS = {"RT1062", "ESP32_S3", "K1_CARRIER", "EXPERIMENT_ONLY", "UNRESOLVED"}
VALID_STATUSES = {"RATIFIED", "DEFAULT", "OPEN", "EXPERIMENT"}

K1BR_REQUIRED_FORBIDDEN = {
    "RAW_PCM", "RAW_PDM", "AUDIO_FEATURES", "RENDER_BUFFER", "PIXEL_BUFFER", "CRGB",
}

# Affirmative claims that RT1062 has hardware PDM decimation. Negated lines are allowed.
PDM_CLAIM = re.compile(r"(MICFIL|native\s+PDM|hardware\s+PDM\s+decim)", re.I)
NEGATION = re.compile(r"\b(no|not|never|without|lacks|absent|false|does not)\b", re.I)

# ---------------------------------------------------------------- required files
for rel in REQUIRED_FILES:
    if not (ROOT / rel).is_file():
        fail("required authority file missing: %s" % rel)
    else:
        COUNTS["authority_files"] += 1

if COUNTS["authority_files"] != len(REQUIRED_FILES):
    print("AUTHORITY_FILES_PARSED=%d/%d" % (COUNTS["authority_files"], len(REQUIRED_FILES)))
    for f in FAILURES:
        print("FAIL: %s" % f)
    print("AUTHORITY_CONSISTENCY=FAIL")
    sys.exit(1)

# ---------------------------------------------------------------- SSCM-1 recovery state
for rel in RECOVERY_STATE_FILES:
    path = ROOT / rel
    if not path.is_file():
        fail("required SSCM-1 recovery-state file missing: %s" % rel)
        continue

    text = path.read_text(encoding="utf-8")
    states = RECOVERY_STATE_RE.findall(text)
    if len(states) != 1:
        fail("%s must contain exactly one SSCM1_RECOVERY_STATE record, found %d"
             % (rel, len(states)))
    else:
        COUNTS["recovery_state_records"] += 1
        if states[0] != EXPECTED_RECOVERY_STATE:
            fail("%s SSCM1_RECOVERY_STATE must be %s, found %s"
                 % (rel, EXPECTED_RECOVERY_STATE, states[0]))

    stale = STALE_RECOVERY_RE.search(text)
    if stale:
        fail("%s contains stale SSCM-1 recovery state: %s"
             % (rel, stale.group(0).strip()))

# ---------------------------------------------------------------- project.yaml
project = yaml.safe_load((ROOT / "project.yaml").read_text(encoding="utf-8")) or {}
py_own = (project.get("ownership") or {})
if not py_own:
    fail("project.yaml declares no ownership block")

audio_block = project.get("audio") or {}
if audio_block.get("rt1062_native_pdm_decimator") is not False:
    fail("project.yaml must declare audio.rt1062_native_pdm_decimator: false")

# ---------------------------------------------------------------- ownership CSV
seen = {}
with (ROOT / "authority/03-OWNERSHIP-MATRIX.csv").open(encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        fn = (row.get("function") or "").strip()
        if not fn:
            continue
        COUNTS["ownership_rows"] += 1
        owner = (row.get("owner") or "").strip()
        status = (row.get("status") or "").strip()
        if fn in seen:
            fail("duplicate ownership row: %s" % fn)
        seen[fn] = owner
        if owner not in VALID_OWNERS:
            fail("unknown owner '%s' for %s" % (owner, fn))
        if status not in VALID_STATUSES:
            fail("unknown status '%s' for %s" % (status, fn))
        if fn in EXPECTED_OWNER and owner != EXPECTED_OWNER[fn]:
            fail("ownership matrix: %s must be owned by %s, found %s"
                 % (fn, EXPECTED_OWNER[fn], owner))
        if fn in UNPINNED_OWNER and owner not in UNPINNED_OWNER[fn]:
            fail("ownership matrix: %s owner must be one of %s, found %s"
                 % (fn, sorted(UNPINNED_OWNER[fn]), owner))
        if fn in EXPECTED_STATUS and status != EXPECTED_STATUS[fn]:
            fail("ownership matrix: %s status must be %s, found %s"
                 % (fn, EXPECTED_STATUS[fn], status))

if COUNTS["ownership_rows"] == 0:
    fail("ownership matrix parsed zero rows")

missing_fn = sorted(REQUIRED_FUNCTIONS - set(seen))
for fn in missing_fn:
    fail("required ownership function absent: %s" % fn)

for fn in sorted(REQUIRED_FUNCTIONS):
    if fn not in py_own:
        fail("project.yaml ownership block is missing required function: %s" % fn)
        continue
    if fn in EXPECTED_OWNER and py_own[fn] != EXPECTED_OWNER[fn]:
        fail("project.yaml: %s must be owned by %s, found %s"
             % (fn, EXPECTED_OWNER[fn], py_own[fn]))
    if fn in UNPINNED_OWNER and py_own[fn] not in UNPINNED_OWNER[fn]:
        fail("project.yaml: %s owner must be one of %s, found %s"
             % (fn, sorted(UNPINNED_OWNER[fn]), py_own[fn]))
    if fn in seen and py_own[fn] != seen[fn]:
        fail("project.yaml and ownership matrix disagree on %s: %s vs %s"
             % (fn, py_own[fn], seen[fn]))

# ---------------------------------------------------------------- contract front matter
def front_matter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return yaml.safe_load(text[3:end]) or {}

contracts = {}
for path in sorted((ROOT / "contracts").rglob("*.md")):
    fm = front_matter(path)
    rel = path.relative_to(ROOT).as_posix()
    if fm is None:
        if rel in REQUIRED_FILES:
            fail("required contract lacks machine-readable front matter: %s" % rel)
        continue
    COUNTS["contracts"] += 1
    contracts[rel] = fm

if COUNTS["contracts"] == 0:
    fail("zero contracts parsed")

k1br = contracts.get("contracts/k1br-bridge.md", {})
if k1br.get("transport_class") != "COMMAND_STATE_TELEMETRY":
    fail("K1BR transport_class must be COMMAND_STATE_TELEMETRY")
declared = {str(p).upper() for p in (k1br.get("forbidden_payloads") or [])}
for payload in sorted(K1BR_REQUIRED_FORBIDDEN - declared):
    fail("K1BR does not forbid required payload class: %s" % payload)

audio_c = contracts.get("contracts/audio-interface.md", {})
if audio_c.get("rt1062_native_pdm_decimator") is not False:
    fail("audio contract must declare rt1062_native_pdm_decimator: false")
if audio_c.get("external_clock_override") != "REQUIRED":
    fail("audio contract must declare external_clock_override: REQUIRED")
for key, expect in (("capture_owner", "RT1062"), ("clock_master_default", "RT1062")):
    if audio_c.get(key) != expect:
        fail("audio contract %s must be %s" % (key, expect))

nfc_c = contracts.get("contracts/nfc-interface.md", {})
if nfc_c.get("frontend_location") != "K1_CARRIER":
    fail("NFC front end must remain K1_CARRIER")

usb_c = contracts.get("contracts/usb-interface.md", {})
if usb_c.get("service_usb_owner") != "ESP32_S3":
    fail("service USB owner must be ESP32_S3")
if usb_c.get("usb_audio") != "EXPERIMENT_ONLY":
    fail("usb_audio must be EXPERIMENT_ONLY")

motion_c = contracts.get("contracts/motion-interface.md", {})
if motion_c.get("owner") != seen.get("accelerometer"):
    fail("motion contract owner disagrees with ownership matrix")

# ---------------------------------------------------------------- text claim scan
SCAN_DIRS = ["authority", "contracts", "architecture", "schematic", "pcb"]
SCAN_ROOTS = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "STATUS.md"]
targets = [p for p in SCAN_ROOTS if p.is_file()]
for d in SCAN_DIRS:
    targets.extend(sorted((ROOT / d).rglob("*.md")))

for path in targets:
    COUNTS["text_files_scanned"] += 1
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if PDM_CLAIM.search(line) and not NEGATION.search(line):
            fail("%s:%d affirmative RT1062 hardware-PDM claim: %s"
                 % (path.relative_to(ROOT).as_posix(), n, line.strip()[:90]))

if COUNTS["text_files_scanned"] == 0:
    fail("scanned zero documents")

# ---------------------------------------------------------------- report
print("AUTHORITY_FILES_PARSED=%d" % COUNTS["authority_files"])
print("OWNERSHIP_ROWS_PARSED=%d" % COUNTS["ownership_rows"])
print("REQUIRED_FUNCTIONS_PRESENT=%d/%d"
      % (len(REQUIRED_FUNCTIONS) - len(missing_fn), len(REQUIRED_FUNCTIONS)))
print("CONTRACTS_PARSED=%d" % COUNTS["contracts"])
print("DOCUMENTS_SCANNED=%d" % COUNTS["text_files_scanned"])
print("SSCM1_RECOVERY_RECORDS_PARSED=%d/%d"
      % (COUNTS["recovery_state_records"], len(RECOVERY_STATE_FILES)))
if COUNTS["recovery_state_records"] == len(RECOVERY_STATE_FILES):
    print("SSCM1_RECOVERY_STATE=%s" % EXPECTED_RECOVERY_STATE)
print("CONTRADICTIONS=%d" % len(FAILURES))

if FAILURES:
    for f in FAILURES:
        print("FAIL: %s" % f)
    print("AUTHORITY_CONSISTENCY=FAIL")
    sys.exit(1)

if min(COUNTS.values()) == 0:
    print("AUTHORITY_CONSISTENCY=FAIL")
    print("reason: a zero input count may never report PASS")
    sys.exit(1)

print("AUTHORITY_CONSISTENCY=PASS")
