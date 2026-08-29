#!/usr/bin/env python3
"""Download remaining LCSC catalog PDFs and extract text for Phase D writes."""

from __future__ import annotations

import hashlib
import json
import ssl
import subprocess
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent
TXT = OUT / "_extract"
TXT.mkdir(exist_ok=True)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
CTX = ssl._create_unverified_context()


def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, context=CTX, timeout=90) as resp:
        dest.write_bytes(resp.read())
    kind = "pdf" if dest.read_bytes()[:5] == b"%PDF-" else "other"
    print(f"{kind:5} {dest.name:55} {dest.stat().st_size}")


def pdftotext(pdf: Path, dest: Path, pages: str | None = None) -> None:
    cmd = ["pdftotext", "-layout", "-enc", "UTF-8"]
    if pages:
        first, last = pages.split("-")
        cmd += ["-f", first, "-l", last]
    cmd += [str(pdf), str(dest)]
    subprocess.check_call(cmd)
    print(f"txt   {dest.name:55} {dest.stat().st_size}")


def main() -> None:
    pdfs = {
        "C5250872": "https://datasheet.lcsc.com/datasheet/pdf/3337127375ea10a041a2d81d01b0bc80.pdf?productCode=C5250872",
        "C622610": "https://datasheet.lcsc.com/datasheet/pdf/e19ca2e6f5eb6f7aee1006b1c22efab4.pdf?productCode=C622610",
        "C3034184": "https://datasheet.lcsc.com/datasheet/pdf/4c3b51ce46e943510b8ad364c0b47ac0.pdf?productCode=C3034184",
        "C590834": "https://datasheet.lcsc.com/datasheet/pdf/e893e58d1e237d5762d91c677e214a6a.pdf?productCode=C590834",
        "C130049": "https://datasheet.lcsc.com/datasheet/pdf/6f77f3ce87c6480e873c2e86cc0d94a2.pdf?productCode=C130049",
        "C2680445": "https://datasheet.lcsc.com/datasheet/pdf/65a6ceacc405c11b85183a983d5939a9.pdf?productCode=C2680445",
    }
    for code, url in pdfs.items():
        dest = OUT / f"LCSC-{code}-catalog-or-vendor.pdf"
        if dest.exists() and dest.stat().st_size > 1000:
            print("skip", dest.name)
        else:
            try:
                fetch(url, dest)
            except Exception as e:
                print("FAIL", code, e)

    extracts = [
        (OUT / "D1-USB2422-DS00001726B.pdf", "usb2422-ds.txt", None),
        (OUT / "D2-USB2422-Hardware-Checklist-DS00004196.pdf", "usb2422-checklist.txt", None),
        (OUT / "D3-USB2422-Errata-DS00001576A.pdf", "usb2422-errata.txt", None),
        (OUT / "D5g-GSwitch-GT-USB-7005A-manufacturer-drawing.pdf", "gswitch-7005a.txt", None),
        (OUT / "D5c-Hirose-CX70M-24P1-spec-sheet.pdf", "cx70m-spec.txt", None),
        (OUT / "D5c-Hirose-CX70M-24P1-design-guide.pdf", "cx70m-guide.txt", None),
        (OUT / "D5c-Hirose-CX70M-24P1-2D-drawing.pdf", "cx70m-2d.txt", None),
        (OUT / "D5d-Hirose-CX90B2-24P-spec-sheet.pdf", "cx90b2-spec.txt", None),
        (OUT / "D5d-Hirose-CX90B2-24P-design-guide.pdf", "cx90b2-guide.txt", None),
        (OUT / "D4-NXP-IMXRT1060CEC-pjrc-mirror-rev4.pdf", "nxp-cec.txt", None),
        (OUT / "D4-NXP-IMXRT1060IEC-singtown-mirror.pdf", "nxp-iec.txt", None),
        (OUT / "D5a-TI-TPS2052B.pdf", "tps2052b.txt", "1-20"),
        (OUT / "D5b-USB-IF-UFP-Powered-Hub-WP-0.9.pdf", "usbif-wp.txt", None),
        (OUT / "D5f-TI-SLVAF82B.pdf", "slvaf82.txt", "1-8"),
        (OUT / "D5h-TE-2129691-customer-drawing.pdf", "te-2129691.txt", None),
        (OUT / "D5h-TE-1-1773868-8-USB-Type-C-datasheet.pdf", "te-family.txt", "1-4"),
        (OUT / "LCSC-C3034184-catalog-or-vendor.pdf", "hyc-lcsc.txt", None),
        (OUT / "LCSC-C5250872-catalog-or-vendor.pdf", "gswitch-lcsc.txt", None),
    ]
    for pdf, name, pages in extracts:
        if not pdf.exists():
            print("MISSING", pdf.name)
            continue
        pdftotext(pdf, TXT / name, pages)

    # procurement snippets from HTML/JSON
    snippets = {}
    for code in ["C5250872", "C622610", "C130049", "C2680445", "C3034184", "C590834"]:
        jp = OUT / f"LCSC-wmsc-{code}.json"
        if jp.exists():
            js = json.loads(jp.read_text())
            r = js.get("result") or {}
            snippets[code] = {
                "productCode": r.get("productCode"),
                "productModel": r.get("productModel") or r.get("productName"),
                "brandName": r.get("brandNameEn") or r.get("brandName"),
                "stock": r.get("stockNumber") or r.get("stock"),
                "encap": r.get("encapStandard"),
                "isExpand": r.get("expand"),
                "pdfUrl": r.get("pdfUrl"),
                "keys": sorted([k for k in r.keys() if any(x in k.lower() for x in ("stock", "basic", "expand", "smt", "assembly", "price", "product"))])[:40],
            }
    (TXT / "wmsc-snippets.json").write_text(json.dumps(snippets, indent=2, ensure_ascii=False) + "\n")
    print("done")


if __name__ == "__main__":
    main()
