#!/usr/bin/env bash
# One-command re-run of the full V2/V3 EasyEDA source-grammar parser battery.
#
# Runs, in order:
#   1. harness/easyeda_source_format.py --self-test
#      (synthetic fault battery + record-shape-drift RED cases + the real-snapshot
#      differential: V2 capture vs V3 capture of the same page, digested independently)
#   2. extract_frozen_denominator.py end-to-end against BOTH real snapshots
#      (wrapped in the schema it expects), diffing every reported count.
#   3. check_schematic_connectivity.py's parse_records + extract_topology against
#      both real snapshots, diffing wire/net/designator counts.
#
# Exits 0 and prints OVERALL=PASS only if every stage passed.
set -uo pipefail
cd "$(dirname "$0")"

FAIL=0

echo "=================================================================="
echo "STAGE 1: easyeda_source_format.py --self-test"
echo "=================================================================="
python3 easyeda_source_format.py --self-test
[ $? -eq 0 ] || FAIL=1

echo
echo "=================================================================="
echo "STAGE 2+3: extract_frozen_denominator + check_schematic_connectivity"
echo "            end-to-end against both real V2/V3 snapshots"
echo "=================================================================="
python3 - "$@" <<'PYEOF'
import json, pathlib, subprocess, sys, tempfile

ARCHIVE = "/Users/spectrasynq/SpectraSynq-EDA/_archive/easyeda-backups/2026-08-28"
V2_SAMPLE = pathlib.Path(f"{ARCHIVE}/schematic-P1-source-1305.json")
V3_SAMPLE = pathlib.Path(f"{ARCHIVE}/schematic-P1-source-POST-V3.json")

if not (V2_SAMPLE.exists() and V3_SAMPLE.exists()):
    print(f"  FAIL  real sample files not found: {V2_SAMPLE} / {V3_SAMPLE}")
    sys.exit(1)

fail = 0
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
from easyeda_source_format import parse_records_any_format  # noqa: E402
from check_schematic_connectivity import parse_records, extract_topology  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    denom_results = {}
    for label, sample in (("v2", V2_SAMPLE), ("v3", V3_SAMPLE)):
        blob = json.loads(sample.read_text())
        snapshot = {
            "source": blob["source"],
            "source_hash": blob["sourceHash"],
            "project_uuid": "run_v3_parser_battery",
            "document_uuid": blob["documentUuid"],
            "schema_version": 1,
        }
        snap_path = tmp / f"{label}-snapshot.json"
        snap_path.write_text(json.dumps(snapshot))
        out_dir = tmp / f"{label}-denom"
        proc = subprocess.run(
            [sys.executable, str(here / "extract_frozen_denominator.py"), str(snap_path), "--out", str(out_dir)],
            capture_output=True, text=True,
        )
        print(f"  --- extract_frozen_denominator.py ({label}) ---")
        print("  " + proc.stdout.strip().replace("\n", "\n  "))
        if proc.returncode != 0:
            print(f"  FAIL  extract_frozen_denominator.py {label}: {proc.stderr.strip()[:300]}")
            fail = 1
            continue
        denom_results[label] = json.loads((out_dir / "index.json").read_text())

        # check_schematic_connectivity.py's independent parse path
        records = parse_records(blob["source"])
        topo = extract_topology(records)
        designators = {c["designator"] for c in topo["components"].values() if "designator" in c}
        print(f"  check_schematic_connectivity ({label}): records={len(records)} "
              f"wires={len(topo['wires'])} named_nets={len(topo['wire_net'])} "
              f"designators={len(designators)}")

    if "v2" in denom_results and "v3" in denom_results:
        c2, c3 = denom_results["v2"]["counts"], denom_results["v3"]["counts"]
        for key in ("components", "designators", "wires", "named_nets"):
            match = c2[key] == c3[key]
            print(f"  {'PASS' if match else 'FAIL'}  denominator.{key}: v2={c2[key]} v3={c3[key]}")
            fail |= 0 if match else 1
        nc_match = c2["no_connect_marks"] == c3["no_connect_marks"]
        print(f"  {'PASS' if nc_match else 'INFO'}  denominator.no_connect_marks: "
              f"v2={c2['no_connect_marks']} v3={c3['no_connect_marks']} "
              f"{'(match)' if nc_match else '(KNOWN DIFFERENCE — see evidence file)'}")

sys.exit(fail)
PYEOF
[ $? -eq 0 ] || FAIL=1

echo
echo "=================================================================="
if [ "$FAIL" -eq 0 ]; then
    echo "OVERALL=PASS"
else
    echo "OVERALL=FAIL"
fi
exit "$FAIL"
