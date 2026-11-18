#!/usr/bin/env python3
"""Abbrev miner: extract ALL-CAPS-ish tokens from product-field strings.

Per the learner charter's glossary-mining thread. Writes a candidate list
ranked by frequency with author counts + sample strings for human review.
"""
import json, re, glob
from collections import defaultdict, Counter

FIELDS = ["razor", "blade", "brush", "soap", "preshave", "aftershave",
          "fragrance", "bowl", "other"]

# uppercase-dominant token, 2-6 chars, allows & + / . interior, may end with digits
TOK = re.compile(r"\b[A-Z][A-Z0-9&+/.]{1,5}\b")

stats = defaultdict(lambda: {"n": 0, "authors": Counter(), "samples": []})
MONTHS = {"JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"}
STOP = {"DE","SE","BB","SS","AS","AT","OR","OF","IN","ON","BY","TO","VS","USA",
        "LTD","INC","CO","OS","NOS","HTF","FS","WTS","WTB","ISO","MINT","BNIB",
        "SOTD","LG","V2","V3","B1","B2","B5","B6","B7","B8","B9"}

for path in sorted(glob.glob("/home/hatch/workspace/sotd/sotd_2*_full.json")):
    rows = json.load(open(path))
    for r in rows:
        author = r.get("author") or "?"
        for f in FIELDS:
            s = r.get(f)
            if not s:
                continue
            if isinstance(s, dict):
                s = " ".join(str(v) for v in s.values() if isinstance(v, str))
            if not isinstance(s, str):
                continue
            for m in TOK.findall(s):
                tok = m.strip(".")
                if tok in MONTHS or tok in STOP:
                    continue
                if tok.isdigit():
                    continue
                st = stats[tok]
                st["n"] += 1
                st["authors"][author] += 1
                if len(st["samples"]) < 4 and s not in st["samples"]:
                    st["samples"].append(s)

out = []
for tok, st in stats.items():
    out.append({"tok": tok, "n": st["n"],
                "nauth": len(st["authors"]),
                "top_authors": st["authors"].most_common(5),
                "samples": st["samples"][:3]})
out.sort(key=lambda x: -x["n"])
json.dump(out, open("/home/hatch/workspace/sotd/knowledge/tools/abbrev_cands_2026-11-04.json", "w"), indent=1)
print("tokens:", len(out))
for c in out[:60]:
    print(f"{c['tok']:8} n={c['n']:5} auth={c['nauth']:3}  {c['samples'][0][:80]!r}")
