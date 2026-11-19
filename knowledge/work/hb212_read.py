#!/usr/bin/env python3
"""(c4-narrow-212/211/213/214) Read B&M hand-body Wayback captures; judge formula
by exact INCI string counts, extract size/price, find the Lavender review."""
import re, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
OUTDIR = "/home/hatch/workspace/goals/sotd-canonical-product-catalog/hidden_files/cdx"

JOBS = [
    ("bayrum", "hand-body-soap-bay-rum", ["20240913114701", "20241202170602"]),
    ("lav", "hand-body-soap-barristers-reserve-lavender", ["20240419051940", "20240913111542", "20240921164008"]),
    ("cr", "hand-body-soap-cologne-russe", ["20240913123627", "20240921164008", "20241202175006", "20250217082317"]),
    ("lavanille", "hand-body-soap-lavanille", ["20240419064521", "20240812174439", "20241214014449"]),
    ("lgc", "hand-body-soap-le-grand-chypre", ["20240225024851", "20240718090451", "20240913124208"]),
]

def fetch(ts, slug):
    url = f"https://web.archive.org/web/{ts}id_/https://barristerandmann.com/products/{slug}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")

for tag, slug, tss in JOBS:
    for ts in tss:
        try:
            html = fetch(ts, slug)
        except Exception as e:
            print(f"{tag} {ts}: FETCH FAIL {e}")
            continue
        with open(f"{OUTDIR}/hb212_{tag}_{ts[:8]}.html", "w") as f:
            f.write(html)
        goat = len(re.findall(r"Goat Milk Powder", html))
        coco = len(re.findall(r"Coconut Milk", html))
        tallow = len(re.findall(r"Tallow \(Beef\)", html))
        # price: JSON-LD / variant price
        prices = sorted(set(re.findall(r'"price":\s*"?([\d.]+)"?', html)))[:6]
        sizes = sorted(set(re.findall(r"Net Wt\.?\s*([\d.]+)\s*oz", html)))
        compare = sorted(set(re.findall(r'"compare_at_price":\s*"?([\d.]+)"?', html)))[:4]
        review = "previous tallow bar soap formulation" in html
        # review date near the review text
        rdate = ""
        if review:
            i = html.find("previous tallow bar soap formulation")
            window = html[max(0, i-3000):i+200]
            m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+20\d\d", window)
            if m:
                rdate = m.group(0)
            else:
                m2 = re.search(r"20\d\d-\d\d-\d\d", window)
                rdate = m2.group(0) if m2 else "(no date in 3k window)"
        print(f"{tag} {ts}: goat={goat} coco={coco} tallow={tallow} prices={prices} compare={compare} size={sizes} review={review} review_date={rdate!r} bytes={len(html)}")
