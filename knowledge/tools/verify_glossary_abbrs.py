#!/usr/bin/env python3
"""Verify bare glossary abbreviations against SOTD dataset usage.

For each (abbreviation, expansion) pair, counts rows (2016-2025 matched
+ 2026 full) where the abbreviation token appears in product fields
(razor/blade/brush/soap/preshave/aftershave/fragrance) and rows where
the full expansion appears, plus rows with both. Notes-field terms
(BBS/DFS/WTG/XTG/ATG/PIF/LG/SOTN/SOTE) are searched in notes too.

Fast path: cheap substring pre-filter per row, token-boundary regex
only on substring hits.
"""
import json
import re
from pathlib import Path

SOTD = Path("/home/hatch/workspace/sotd")
PROD_FIELDS = ["razor", "blade", "brush", "soap", "preshave", "aftershave", "fragrance"]
NOTE_FIELDS = ["notes"]

# (abbr, expansion, search_notes_too)
CHECKS = [
    ("B&M", "Barrister and Mann", False),
    ("HoM", "House of Mammoth", False),
    ("NO", "Noble Otter", False),
    ("CF", "Chiseled Face", False),
    ("WK", "Wholly Kaw", False),
    ("A&E", "Ariana & Evans", False),
    ("M&M", "Murphy & McNeil", False),
    ("SBS", "Summer Break Soaps", False),
    ("GD", "Grooming Dept", False),
    ("T+S", "Tallow + Steel", False),
    ("APR", "Australian Private Reserve", False),
    ("TOBS", "Taylor of Old Bond Street", False),
    ("SV", "Saponificio Varesino", False),
    ("RR", "RazoRock", False),
    ("EJ", "Edwin Jagger", False),
    ("WSP", "Wet Shaving Products", False),
    ("MLS", "Mickey Lee Soapworks", False),
    ("SW", "Southern Witchcraft", False),
    ("AP", "AP Shave Co", False),
    ("LGC", "Le Grand Chypre", False),
    ("GTB", "Ghost Town Barber", False),
    ("MMOC", "Micromatic Open Comb", False),
    ("MMCP", "Micromatic Clog-Pruf", False),
    ("Fatboy", "Gillette 195", False),
    ("SB", "solid bar", False),
    ("SP", "Super Platinum", False),
    ("SI", "Super Iridium", False),
    ("AS", "aftershave", False),
    ("OC", "Open Comb", False),
    ("DE", "Double Edge", False),
    ("SE", "Single Edge", False),
    ("AC", "Artist Club", False),
    ("NEW", "Gillette NEW", False),
    ("LC", "Long Comb", False),
    ("SC", "Short Comb", False),
    ("GC", "Game Changer", False),
    ("CG", "Charcoal Goods", False),
    ("MR", "Maggard", False),
    ("HD", "Heavy Duty", False),
    ("FH", "Full Hollow", False),
    ("XL", "Silvertip Fibre XL", False),
    ("STF", "Silvertip Fibre", False),
    ("HMW", "High Mountain White", False),
    ("GSB", "Silver Blue", False),
    ("PTFE", "polytetrafluoroethylene", False),
    ("LE", "Limited Edition", False),
    ("EDP", "Eau de Parfum", False),
    ("CNC", "CNC", False),
    ("BBS", "Baby Butt Smooth", True),
    ("DFS", "Damn Fine Shave", True),
    ("SOTN", "Shave Of The Night", True),
    ("SOTE", "Shave Of The Evening", True),
    ("PIF", "Pay It Forward", True),
    ("LG", "Lather Games", True),
    ("WTG", "with the grain", True),
    ("XTG", "across the grain", True),
    ("ATG", "against the grain", True),
]


def token_pat(s):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(s) + r"(?![A-Za-z0-9])")


def main():
    files = [SOTD / f"matched_{y}.json" for y in range(2016, 2026)]
    files.append(SOTD / "sotd_2026_full.json")
    compiled = []
    for abbr, expansion, in_notes in CHECKS:
        compiled.append((abbr, expansion, in_notes, token_pat(abbr), token_pat(expansion)))
    counts = {abbr: [0, 0, 0] for abbr, _, _ in CHECKS}
    nrows = 0
    for f in files:
        with open(f) as fh:
            rows = json.load(fh)
        for r in rows:
            nrows += 1
            prod = " | ".join(str(r.get(f) or "") for f in PROD_FIELDS)
            notes = str(r.get("notes") or "")
            for abbr, expansion, in_notes, ap, ep in compiled:
                text = prod + (" | " + notes if in_notes else "")
                has_a = abbr in text and bool(ap.search(text))
                has_e = expansion in text and bool(ep.search(text))
                c = counts[abbr]
                c[0] += has_a
                c[1] += has_e
                c[2] += has_a and has_e
    print(f"rows: {nrows}")
    for abbr, _, _ in CHECKS:
        a, e, b = counts[abbr]
        print(f"{abbr:8} token={a:6} expansion={e:6} both={b:6}")


if __name__ == "__main__":
    main()
