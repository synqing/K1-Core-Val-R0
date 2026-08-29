#!/usr/bin/env python3
"""Phase D vendor-pack downloader. Does not bind any MPN."""

from __future__ import annotations

import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
CTX = ssl.create_default_context()
STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url: str, dest: Path, *, timeout: int = 90, extra_headers: dict | None = None) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": UA, "Accept": "*/*"}
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            data = resp.read()
            final = resp.geturl()
            ctype = resp.headers.get("Content-Type", "")
            status = getattr(resp, "status", 200)
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        return {
            "ok": False,
            "url": url,
            "dest": str(dest.name),
            "error": f"HTTP {e.code}",
            "bytes": len(body),
            "ctype": e.headers.get("Content-Type", "") if e.headers else "",
        }
    except Exception as e:
        return {"ok": False, "url": url, "dest": str(dest.name), "error": str(e)}

    dest.write_bytes(data)
    kind = "bin"
    if data[:5] == b"%PDF-":
        kind = "pdf"
    elif data[:2] == b"PK":
        kind = "zip"
    elif data.lstrip()[:1] in (b"<", b"{", b"["):
        kind = "text"
    elif dest.suffix.lower() in {".html", ".htm", ".json", ".md", ".txt"}:
        kind = "text"
    sha = hashlib.sha256(data).hexdigest()
    return {
        "ok": True,
        "url": url,
        "final": final,
        "dest": dest.name,
        "bytes": len(data),
        "sha256": sha,
        "ctype": ctype,
        "kind": kind,
        "status": status,
        "secs": round(time.time() - t0, 2),
    }


JOBS = [
    # D1–D3 Microchip USB2422
    (
        "https://ww1.microchip.com/downloads/en/DeviceDoc/00001726B.pdf",
        OUT / "D1-USB2422-DS00001726B.pdf",
    ),
    (
        "https://ww1.microchip.com/downloads/aemDocuments/documents/UNG/ProductDocuments/DesignChecklist/USB2422-Hardware-Design-Checklist-DS00004196.pdf",
        OUT / "D2-USB2422-Hardware-Checklist-DS00004196.pdf",
    ),
    (
        "https://ww1.microchip.com/downloads/en/DeviceDoc/00001576A.pdf",
        OUT / "D3-USB2422-Errata-DS00001576A.pdf",
    ),
    # D4 NXP
    (
        "https://www.nxp.com/docs/en/data-sheet/IMXRT1060CEC.pdf",
        OUT / "D4-NXP-IMXRT1060CEC.pdf",
    ),
    (
        "https://www.nxp.com/docs/en/data-sheet/IMXRT1060IEC.pdf",
        OUT / "D4-NXP-IMXRT1060IEC.pdf",
    ),
    # D5 Espressif HTML
    (
        "https://docs.espressif.com/projects/esp-usb/en/latest/esp32s3/usb_device.html",
        OUT / "D5-ESP32-S3-usb_device.html",
    ),
    # D5a TI TPS2052B
    (
        "https://www.ti.com/lit/ds/symlink/tps2052b.pdf",
        OUT / "D5a-TI-TPS2052B.pdf",
    ),
    (
        "https://www.lcsc.com/product-detail/C130049.html",
        OUT / "D5a-LCSC-C130049.html",
    ),
    (
        "https://www.lcsc.com/product-detail/C2680445.html",
        OUT / "D5a-LCSC-C2680445.html",
    ),
    # D5b USB-IF
    (
        "https://www.usb.org/sites/default/files/USB_Upstream_Facing_Port_Powered_Hub_White_Paper_0.9.pdf",
        OUT / "D5b-USB-IF-UFP-Powered-Hub-WP-0.9.pdf",
    ),
    # D5c Hirose CX70M
    (
        "https://www.hirose.com/product/p/CL0480-0304-0-00",
        OUT / "D5c-Hirose-CX70M-24P1-product.html",
    ),
    (
        "https://www.hirose.com/en/product/p/CL0480-0304-0-00",
        OUT / "D5c-Hirose-CX70M-24P1-product-en.html",
    ),
    (
        "https://www.hirose.com/product/document?clcode=CL0480-0304-0-00&documentid=D52488_en&documenttype=Catalog&lang=en&productname=CX70M-24P1&series=CX",
        OUT / "D5c-Hirose-CX70M-catalog-page.html",
    ),
    (
        "https://www.hirose.com/medias/ed_CX_20240801.pdf?context=bWFzdGVyfHByaXZhdGVfc3lzX3VwbG9hZHw0MzEzODA1fGFwcGxpY2F0aW9uL3BkZnxjM2x6TFcxaGMzUmxjaTl3Y21sMllYUmxYM041YzE5MWNHeHZZV1F2YUdNd0wyZzRaUzg1TmpjeU5qQTBNekU1TnpjMEwyVmtYME5ZWHpJd01qUXdPREF4TG5Ca1pnfGIxNTViZjhhYzBlMTM4MDAwM2Y0YmFmYmZjNTU1YmRjZjA5YjJlMGUxN2Q0YTVkOTNkYWMzZDU5ZmZkYzc5ZWE",
        OUT / "D5c-Hirose-CX-series-catalog-20240801.pdf",
    ),
    # D5d Hirose CX90B2
    (
        "https://www.hirose.com/product/p/CL0480-0889-0-00",
        OUT / "D5d-Hirose-CX90B2-24P-product.html",
    ),
    (
        "https://www.hirose.com/en/product/p/CL0480-0889-0-00",
        OUT / "D5d-Hirose-CX90B2-24P-product-en.html",
    ),
    (
        "https://www.hirose.com/en/product/document?clcode=CL0480-0889-0-00&documentid=CX90B2-24P_4800889000_Design+Guide_EN&documenttype=Guideline&lang=en&productname=CX90B2-24P&series=CX",
        OUT / "D5d-Hirose-CX90B2-design-guide.html",
    ),
    (
        "https://www.hirose.com/en/product/document?clcode=CL0480-0889-0-00&documentid=CX90B2-24P_4800889000_Spechsheet_EN&documenttype=SpecSheet&lang=en&productname=CX90B2-24P&series=CX",
        OUT / "D5d-Hirose-CX90B2-spec-sheet.html",
    ),
    # D5e HYC
    (
        "https://www.lcsc.com/product-detail/C3034184.html",
        OUT / "D5e-LCSC-C3034184.html",
    ),
    (
        "https://www.szhoauc.com/product/usb/waterproof%20USB/359.html",
        OUT / "D5e-HOAUC-HYC78-USBC24-140-manufacturer.html",
    ),
    # D5f TI protection
    (
        "https://www.ti.com/lit/an/slvaf82b/slvaf82b.pdf",
        OUT / "D5f-TI-SLVAF82B.pdf",
    ),
    (
        "https://www.ti.com/lit/ds/symlink/tpd2s300.pdf",
        OUT / "D5f-TI-TPD2S300.pdf",
    ),
    (
        "https://www.ti.com/lit/ds/symlink/tpd4s201.pdf",
        OUT / "D5f-TI-TPD4S201.pdf",
    ),
    # D5g G-Switch primary
    (
        "https://dg-switch.com/woshitype/2538.html",
        OUT / "D5g-GSwitch-GT-USB-7005X-manufacturer.html",
    ),
    (
        "https://www.lcsc.com/product-detail/C5250872.html",
        OUT / "D5g-LCSC-C5250872.html",
    ),
    (
        "https://www.unikeyic.com/products/usb-dvi-hdmi-connectors/gt-usb-7005a/733071207.html",
        OUT / "D5g-Unikeyic-GT-USB-7005A-paraphrase-only.html",
    ),
    # D5h TE archive
    (
        "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=1-1773868-8_USB_Type-C_datasheet&DocType=Data+Sheet",
        OUT / "D5h-TE-1-1773868-8-USB-Type-C-datasheet.pdf",
    ),
    (
        "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=2129691&DocType=Customer+Drawing&DocLang=English",
        OUT / "D5h-TE-2129691-customer-drawing.pdf",
    ),
    (
        "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=108-99061&DocType=SS&DocLang=EN",
        OUT / "D5h-TE-108-99061.pdf",
    ),
    (
        "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=108-115109-2&DocType=SS&DocLang=EN",
        OUT / "D5h-TE-108-115109-2.pdf",
    ),
    (
        "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=108-160251&DocType=SS&DocLang=EN",
        OUT / "D5h-TE-108-160251.pdf",
    ),
    (
        "https://www.lcsc.com/product-detail/C590834.html",
        OUT / "D5h-LCSC-C590834.html",
    ),
    # D6 / D7 procurement pages
    (
        "https://www.microchip.com/en-us/product/usb2422",
        OUT / "D6-Microchip-USB2422-product.html",
    ),
    (
        "https://www.lcsc.com/product-detail/C622610.html",
        OUT / "D7-LCSC-C622610.html",
    ),
    (
        "https://jlcpcb.com/partdetail/G-Switch-GT_USB_7005A/C5250872",
        OUT / "D5g-JLC-C5250872.html",
    ),
    (
        "https://jlcpcb.com/partdetail/C622610",
        OUT / "D7-JLC-C622610.html",
    ),
    (
        "https://jlcpcb.com/partdetail/C3034184",
        OUT / "D5e-JLC-C3034184.html",
    ),
    (
        "https://jlcpcb.com/partdetail/C590834",
        OUT / "D5h-JLC-C590834.html",
    ),
]


JLCSEARCH = {
    "C5250872": OUT / "D5g-jlcsearch-C5250872.json",
    "C622610": OUT / "D7-jlcsearch-C622610.json",
    "C130049": OUT / "D5a-jlcsearch-C130049.json",
    "C2680445": OUT / "D5a-jlcsearch-C2680445.json",
    "C590834": OUT / "D5h-jlcsearch-C590834.json",
    "C3034184": OUT / "D5e-jlcsearch-C3034184.json",
}


def main() -> int:
    results = []
    for url, dest in JOBS:
        r = fetch(url, dest)
        results.append(r)
        flag = "OK" if r.get("ok") else "FAIL"
        print(f"{flag:4} {dest.name:55} {r.get('bytes', 0):8} {r.get('kind', r.get('error', ''))}")
        time.sleep(0.25)

    for code, dest in JLCSEARCH.items():
        url = f"https://jlcsearch.tscircuit.com/api/search?q={code}&limit=5&full=true"
        r = fetch(url, dest)
        r["note"] = f"jlcsearch {code}"
        results.append(r)
        flag = "OK" if r.get("ok") else "FAIL"
        print(f"{flag:4} {dest.name:55} {r.get('bytes', 0):8} {r.get('kind', r.get('error', ''))}")
        time.sleep(0.3)

    meta = {"captured_utc": STAMP, "results": results}
    (OUT / "_download_receipt.json").write_text(json.dumps(meta, indent=2) + "\n")
    ok = sum(1 for r in results if r.get("ok"))
    fail = sum(1 for r in results if not r.get("ok"))
    pdfs = [r for r in results if r.get("kind") == "pdf"]
    print(f"SUMMARY ok={ok} fail={fail} pdfs={len(pdfs)}")
    for r in results:
        if not r.get("ok"):
            print("MISSING", r["dest"], r.get("error"))
        elif r.get("kind") != "pdf" and r["dest"].endswith(".pdf"):
            print("NOT_PDF", r["dest"], r.get("ctype"), r.get("bytes"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
