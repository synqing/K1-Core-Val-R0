#!/usr/bin/env python3
"""Hirose remaining docs, NXP mirrors, LCSC wmsc, Microchip snapshot."""

from __future__ import annotations

import hashlib
import json
import ssl
import time
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
CTX = ssl._create_unverified_context()
BASE = "https://www.hirose.com"


def fetch(url: str, dest: Path, *, headers=None, timeout=90) -> dict:
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            data = resp.read()
            final = resp.geturl()
            ctype = resp.headers.get("Content-Type", "")
    except Exception as e:
        return {"ok": False, "url": url, "dest": dest.name, "error": str(e)}
    dest.write_bytes(data)
    kind = "bin"
    if data[:5] == b"%PDF-":
        kind = "pdf"
    elif data[:2] == b"PK":
        kind = "zip"
    elif data.lstrip()[:1] in (b"<", b"{", b"["):
        kind = "text"
    return {
        "ok": True,
        "url": url,
        "final": final,
        "dest": dest.name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "ctype": ctype,
        "kind": kind,
    }


HIROSE = [
    (
        f"{BASE}/product/document?clcode=CL0480-0304-0-00&productname=CX70M-24P1&series=CX&documenttype=2DDrawing&lang=en&documentid=CX70M-24P1_48003040_2D_ENG",
        OUT / "D5c-Hirose-CX70M-24P1-2D-drawing.pdf",
    ),
    (
        f"{BASE}/product/document?clcode=CL0480-0304-0-00&productname=CX70M-24P1&series=CX&documenttype=SpecSheet&lang=en&documentid=CX70M-24P1_4800304000_Specsheet_Eng",
        OUT / "D5c-Hirose-CX70M-24P1-spec-sheet.pdf",
    ),
    (
        f"{BASE}/product/document?clcode=CL0480-0304-0-00&productname=CX70M-24P1&series=CX&documenttype=Guideline&lang=en&documentid=CX70M-24P1_4800304000_Design+Guide_EN",
        OUT / "D5c-Hirose-CX70M-24P1-design-guide.pdf",
    ),
    (
        f"{BASE}/product/document?clcode=CL0480-0304-0-00&productname=CX70M-24P1&series=CX&documenttype=3DDrawing_STEP&lang=en&documentid=D52491_en",
        OUT / "D5c-Hirose-CX70M-24P1-STEP.zip",
    ),
    (
        f"{BASE}/en/product/document?clcode=CL0480-0889-0-00&productname=CX90B2-24P&series=CX&documenttype=2DDrawing&lang=en&documentid=CX90B2-24P_4800889000_2D_EN",
        OUT / "D5d-Hirose-CX90B2-24P-2D-drawing.pdf",
    ),
    (
        f"{BASE}/en/product/document?clcode=CL0480-0889-0-00&productname=CX90B2-24P&series=CX&documenttype=3DDrawing_STEP&lang=en&documentid=CX90B2-24P_4800889000_3D_STEP",
        OUT / "D5d-Hirose-CX90B2-24P-STEP.zip",
    ),
    (
        f"{BASE}/en/product/document?clcode=CL0480-0889-0-00&productname=CX90B2-24P&series=CX&documenttype=Guideline&lang=en&documentid=CX90B2-24P_4800889000_Design+Guide_EN",
        OUT / "D5d-Hirose-CX90B2-24P-design-guide.pdf",
    ),
    (
        f"{BASE}/en/product/document?clcode=CL0480-0889-0-00&productname=CX90B2-24P&series=CX&documenttype=SpecSheet&lang=en&documentid=CX90B2-24P_4800889000_Spechsheet_EN",
        OUT / "D5d-Hirose-CX90B2-24P-spec-sheet.pdf",
    ),
]

NXP = [
    (
        "https://www.nxp.com/docs/en/nxp/data-sheets/IMXRT1060CEC.pdf",
        OUT / "D4-NXP-IMXRT1060CEC.pdf",
        {"Referer": "https://www.nxp.com/products/i.MX-RT1060"},
    ),
    (
        "https://www.nxp.com/docs/en/nxp/data-sheets/IMXRT1060IEC.pdf",
        OUT / "D4-NXP-IMXRT1060IEC.pdf",
        {"Referer": "https://www.nxp.com/products/i.MX-RT1060"},
    ),
    (
        "https://www.pjrc.com/teensy/IMXRT1060CEC_rev4.pdf",
        OUT / "D4-NXP-IMXRT1060CEC-pjrc-mirror-rev4.pdf",
        None,
    ),
    (
        "https://dl.singtown.com/datasheet/IMXRT1060IEC.pdf",
        OUT / "D4-NXP-IMXRT1060IEC-singtown-mirror.pdf",
        None,
    ),
]

WMSC = [
    "C5250872",
    "C622610",
    "C130049",
    "C2680445",
    "C3034184",
    "C590834",
]


def main() -> int:
    results = []
    for url, dest in HIROSE:
        r = fetch(url, dest)
        results.append(r)
        print(f"{'OK' if r.get('ok') else 'FAIL':4} {dest.name:55} {r.get('bytes',0):8} {r.get('kind', r.get('error',''))[:70]}")
        time.sleep(0.2)

    for url, dest, hdrs in NXP:
        r = fetch(url, dest, headers=hdrs)
        results.append(r)
        print(f"{'OK' if r.get('ok') else 'FAIL':4} {dest.name:55} {r.get('bytes',0):8} {r.get('kind', r.get('error',''))[:70]}")
        time.sleep(0.2)

    for code in WMSC:
        url = f"https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={code}"
        dest = OUT / f"LCSC-wmsc-{code}.json"
        r = fetch(url, dest)
        results.append(r)
        print(f"{'OK' if r.get('ok') else 'FAIL':4} {dest.name:55} {r.get('bytes',0):8} {r.get('kind', r.get('error',''))[:70]}")
        if r.get("ok"):
            try:
                js = json.loads(dest.read_text())
                result = js.get("result") or js.get("data") or js
                # walk for pdf
                blob = json.dumps(result)
                import re

                pdfs = re.findall(r"https?://[^\"'\\s]+\\.pdf", blob)
                print("  pdfs", pdfs[:4])
                if pdfs:
                    pr = fetch(pdfs[0], OUT / f"LCSC-{code}-wmsc-datasheet.pdf")
                    results.append(pr)
                    print(f"  {'OK' if pr.get('ok') else 'FAIL'} datasheet {pr.get('bytes')} {pr.get('kind', pr.get('error'))}")
            except Exception as e:
                print("  parse", e)
        time.sleep(0.25)

    (OUT / "_download_hirose_nxp_receipt.json").write_text(json.dumps(results, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    main()
