#!/usr/bin/env python3
"""Retry failed Phase D downloads; scrape LCSC datasheet URLs."""

from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

try:
    import certifi

    CTX_STRICT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX_STRICT = ssl.create_default_context()
CTX_INSECURE = ssl._create_unverified_context()


def fetch(url: str, dest: Path, ctx, *, timeout=90, headers=None) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
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
    import hashlib

    return {
        "ok": True,
        "url": url,
        "final": final,
        "dest": dest.name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "ctype": ctype,
        "kind": kind,
        "secs": round(time.time() - t0, 2),
    }


def try_fetch(url: str, dest: Path, **kw) -> dict:
    r = fetch(url, dest, CTX_STRICT, **kw)
    if r.get("ok"):
        return r
    r2 = fetch(url, dest, CTX_INSECURE, **kw)
    r2["insecure_ssl"] = True
    r2["first_error"] = r.get("error")
    return r2


JOBS = [
    (
        "https://www.nxp.com/docs/en/nxp/data-sheets/IMXRT1060CEC.pdf",
        OUT / "D4-NXP-IMXRT1060CEC.pdf",
    ),
    (
        "https://www.nxp.com/docs/en/nxp/data-sheets/IMXRT1060IEC.pdf",
        OUT / "D4-NXP-IMXRT1060IEC.pdf",
    ),
    (
        "https://dg-switch.com/uploads/soft/230408/GT-USB-7005A.pdf",
        OUT / "D5g-GSwitch-GT-USB-7005A-manufacturer-drawing.pdf",
    ),
    (
        "https://dg-switch.com/uploads/soft/230408/GT-USB-7005A-3D.zip",
        OUT / "D5g-GSwitch-GT-USB-7005A-3D.zip",
    ),
    (
        "https://www.hirose.com/product/p/CL0480-0304-0-00",
        OUT / "D5c-Hirose-CX70M-24P1-product.html",
    ),
    (
        "https://www.hirose.com/en/product/p/CL0480-0304-0-00",
        OUT / "D5c-Hirose-CX70M-24P1-product-en.html",
    ),
    (
        "https://www.hirose.com/product/p/CL0480-0889-0-00",
        OUT / "D5d-Hirose-CX90B2-24P-product.html",
    ),
    (
        "https://www.hirose.com/en/product/p/CL0480-0889-0-00",
        OUT / "D5d-Hirose-CX90B2-24P-product-en.html",
    ),
    (
        "https://www.hirose.com/medias/ed_CX_20240801.pdf?context=bWFzdGVyfHByaXZhdGVfc3lzX3VwbG9hZHw0MzEzODA1fGFwcGxpY2F0aW9uL3BkZnxjM2x6TFcxaGMzUmxjaTl3Y21sMllYUmxYM041YzE5MWNHeHZZV1F2YUdNd0wyZzRaUzg1TmpjeU5qQTBNekU1TnpjMEwyVmtYME5ZWHpJd01qUXdPREF4TG5Ca1pnfGIxNTViZjhhYzBlMTM4MDAwM2Y0YmFmYmZjNTU1YmRjZjA5YjJlMGUxN2Q0YTVkOTNkYWMzZDU5ZmZkYzc5ZWE",
        OUT / "D5c-Hirose-CX-series-catalog-20240801.pdf",
    ),
    (
        "https://www.hirose.com/product/document?clcode=CL0480-0304-0-00&documentid=D52488_en&documenttype=Catalog&lang=en&productname=CX70M-24P1&series=CX",
        OUT / "D5c-Hirose-CX70M-catalog-page.html",
    ),
    (
        "https://www.hirose.com/en/product/document?clcode=CL0480-0889-0-00&documentid=CX90B2-24P_4800889000_Design+Guide_EN&documenttype=Guideline&lang=en&productname=CX90B2-24P&series=CX",
        OUT / "D5d-Hirose-CX90B2-design-guide.html",
    ),
    (
        "https://www.hirose.com/en/product/document?clcode=CL0480-0889-0-00&documentid=CX90B2-24P_4800889000_Spechsheet_EN&documenttype=SpecSheet&lang=en&productname=CX90B2-24P&series=CX",
        OUT / "D5d-Hirose-CX90B2-spec-sheet.html",
    ),
    (
        "https://www.microchip.com/en-us/product/usb2422",
        OUT / "D6-Microchip-USB2422-product.html",
    ),
    (
        "https://www.microchip.com/en-us/product/USB2422",
        OUT / "D6-Microchip-USB2422-product-alt.html",
    ),
    (
        "https://www.mouser.com/ProductDetail/Microchip-Technology/USB2422T-I-MJ",
        OUT / "D6-Mouser-USB2422T-I-MJ-status.html",
    ),
]


def scrape_lcsc_pdfs() -> list[tuple[str, Path]]:
    extra = []
    htmls = {
        "C5250872": OUT / "D5g-LCSC-C5250872.html",
        "C622610": OUT / "D7-LCSC-C622610.html",
        "C3034184": OUT / "D5e-LCSC-C3034184.html",
        "C130049": OUT / "D5a-LCSC-C130049.html",
        "C2680445": OUT / "D5a-LCSC-C2680445.html",
        "C590834": OUT / "D5h-LCSC-C590834.html",
    }
    for code, path in htmls.items():
        if not path.exists():
            continue
        text = path.read_text(errors="replace")
        urls = set(re.findall(r"https?://[^\"'\\s>]+\.pdf", text, re.I))
        urls |= set(re.findall(r"https?://wmsc\.lcsc\.com[^\"'\\s>]+", text, re.I))
        print(f"LCSC {code} pdf-ish urls: {len(urls)}")
        for i, u in enumerate(sorted(urls)):
            if "wmsc.lcsc.com" in u or u.lower().endswith(".pdf"):
                print(" ", u[:180])
                extra.append((u, OUT / f"LCSC-{code}-datasheet-{i}.pdf"))
    return extra


def extract_hirose_doc_urls(html_path: Path) -> list[str]:
    if not html_path.exists() or html_path.stat().st_size < 200:
        return []
    text = html_path.read_text(errors="replace")
    urls = re.findall(r"https?://[^\"'\\s>]+(?:\.pdf|/document[^\"'\\s>]*)", text, re.I)
    names = re.findall(r"[\w\-\+\.]+\.pdf", text, re.I)
    print(html_path.name, "pdf names", names[:20], "url hits", len(urls))
    return urls


def main() -> int:
    results = []
    for url, dest in JOBS:
        r = try_fetch(url, dest)
        results.append(r)
        flag = "OK" if r.get("ok") else "FAIL"
        print(f"{flag:4} {dest.name:60} {r.get('bytes', 0):8} {r.get('kind', r.get('error', ''))[:80]}")
        time.sleep(0.2)

    for url, dest in scrape_lcsc_pdfs():
        if dest.exists() and dest.stat().st_size > 1000:
            print("SKIP", dest.name)
            continue
        r = try_fetch(url, dest)
        results.append(r)
        flag = "OK" if r.get("ok") else "FAIL"
        print(f"{flag:4} {dest.name:60} {r.get('bytes', 0):8} {r.get('kind', r.get('error', ''))[:80]}")
        time.sleep(0.2)

    for hp in [
        OUT / "D5c-Hirose-CX70M-24P1-product-en.html",
        OUT / "D5c-Hirose-CX70M-24P1-product.html",
        OUT / "D5d-Hirose-CX90B2-24P-product-en.html",
        OUT / "D5d-Hirose-CX90B2-24P-product.html",
    ]:
        extract_hirose_doc_urls(hp)

    (OUT / "_download_retry_receipt.json").write_text(json.dumps(results, indent=2) + "\n")
    print("RETRY_DONE", sum(1 for r in results if r.get("ok")), "/", len(results))
    return 0


if __name__ == "__main__":
    main()
