#!/usr/bin/env python3
"""K1-CORE-VAL-R0 terminology check.

AP means Audio Processing only. A Wi-Fi access point is WIFI_AP, SOFTAP or ACCESS_POINT.
BLE-MIDI is the current wireless control plane; Wi-Fi, REST and WebSocket are parked.

Scans authority-bearing material only. archive/, sources/ and evidence/ are excluded because
they may legitimately quote superseded language.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILURES = []
EXEMPTIONS = []
FILES_SCANNED = 0
LINES_SCANNED = 0

SCAN_DIRS = ["authority", "contracts", "architecture", "schematic", "pcb"]
SCAN_ROOTS = ["README.md", "AGENTS.md", "STATUS.md", "project.yaml"]
EXCLUDED = {"archive", "sources", "evidence", "experiments"}

# The quoting exemption exists so the terminology rule and the supersession log can name the
# language they ban and record. It is deliberately restricted to those two documents. Widening
# it is a code change, which is the point: an exemption must never be convenient.
QUOTED_OK = re.compile(r"\[quoted-superseded\]")
QUOTED_ALLOWED_FILES = {
    "authority/04-TERMINOLOGY.md",
    "authority/05-SUPERSESSIONS.md",
}

BARE_AP = re.compile(r"(?<![A-Za-z0-9_])AP(?![A-Za-z0-9_])")
WIFI_CTX = re.compile(
    r"(wi-?fi|access\s+point|softap|station\s+mode|ssid|802\.11|websocket|\brest\b)", re.I)
AP_DEFINED = re.compile(
    r"AP[\s`'\"*:]*(=|means|is)?[\s`'\"*:]*Audio[\s_]+Processing|Audio\s+Processing\s*\(\s*AP\s*\)", re.I)

FORBIDDEN_PHRASES = [
    (re.compile(r"AP-only\s+(Wi-?Fi|radio)", re.I), "forbidden phrase 'AP-only Wi-Fi/radio'"),
    (re.compile(r"\bthe\s+processor\b", re.I), "ambiguous ownership language 'the processor'"),
    (re.compile(r"\bthe\s+MCU\b", re.I), "ambiguous ownership language 'the MCU'"),
]

ASSIGN = r"(=|:|\bis\b|\bmarked\b|\bstatus\b)"
WIFI_CURRENT = re.compile(
    r"(wi-?fi|websocket|\brest\b)[^\n]{0,40}" + ASSIGN + r"[\s`*]*(CURRENT|AUTHORITATIVE)\b", re.I)
BLE_PARKED = re.compile(
    r"BLE-?MIDI[^\n]{0,40}" + ASSIGN + r"[\s`*]*(PARKED|SUPERSEDED|RETIRED)\b", re.I)

targets = []
for name in SCAN_ROOTS:
    p = ROOT / name
    if p.is_file():
        targets.append(p)
for d in SCAN_DIRS:
    base = ROOT / d
    if base.is_dir():
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix in {".md", ".csv", ".yaml", ".yml"}:
                if EXCLUDED & set(p.relative_to(ROOT).parts):
                    continue
                targets.append(p)

for path in targets:
    FILES_SCANNED += 1
    rel = path.relative_to(ROOT).as_posix()
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        LINES_SCANNED += 1
        snippet = line.strip()[:90]
        if QUOTED_OK.search(line):
            if rel in QUOTED_ALLOWED_FILES:
                EXEMPTIONS.append("%s:%d" % (rel, n))
                continue
            FAILURES.append(
                "%s:%d [quoted-superseded] is not permitted outside %s: %s"
                % (rel, n, " or ".join(sorted(QUOTED_ALLOWED_FILES)), snippet))
            continue
        if BARE_AP.search(line) and WIFI_CTX.search(line) and not AP_DEFINED.search(line):
            FAILURES.append("%s:%d bare 'AP' in a Wi-Fi context: %s" % (rel, n, snippet))
        for pattern, why in FORBIDDEN_PHRASES:
            if pattern.search(line):
                FAILURES.append("%s:%d %s: %s" % (rel, n, why, snippet))
        if WIFI_CURRENT.search(line):
            FAILURES.append("%s:%d Wi-Fi/REST/WebSocket marked current: %s" % (rel, n, snippet))
        if BLE_PARKED.search(line):
            FAILURES.append("%s:%d BLE-MIDI marked parked or superseded: %s" % (rel, n, snippet))

for e in EXEMPTIONS:
    print("QUOTED_EXEMPTION=%s" % e)
print("TERMINOLOGY_FILES_SCANNED=%d" % FILES_SCANNED)
print("TERMINOLOGY_LINES_SCANNED=%d" % LINES_SCANNED)
print("QUOTED_EXEMPTIONS_HONOURED=%d" % len(EXEMPTIONS))
print("VIOLATIONS=%d" % len(FAILURES))

if FILES_SCANNED == 0 or LINES_SCANNED == 0:
    print("TERMINOLOGY=FAIL")
    print("reason: scanned nothing; a zero input count may never report PASS")
    sys.exit(1)

if FAILURES:
    for f in FAILURES:
        print("FAIL: %s" % f)
    print("TERMINOLOGY=FAIL")
    sys.exit(1)

print("TERMINOLOGY=PASS")
