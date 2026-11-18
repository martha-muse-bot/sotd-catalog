#!/usr/bin/env python3
"""(c4-narrow-169) hugbckt's uncool-Embrace belief census.
Q: did hugbckt (or anyone) ever attest an uncool / no-cooling Embrace splash,
or is it a mistake / request-only variant?
Print: all hugbckt Embrace rows (any field) with notes; all Embrace splash rows
with cooling/uncool language; all authors of Embrace splash rows.
"""
import json, glob, re
from collections import Counter

ROWS = []
for f in sorted(glob.glob("/home/hatch/workspace/sotd/sotd_*_full.json")):
    ROWS.extend(json.load(open(f)))
print("corpus rows:", len(ROWS))
print("max thread_date:", max(r.get("thread_date", "") for r in ROWS))

def field_has(row, field, pat):
    return bool(re.search(pat, row.get(field) or "", re.I))

emb_re = re.compile(r"\bembrace\b", re.I)
hom_re = re.compile(r"mammoth|house of mammoth|\bhom\b", re.I)

def embrace_splash(row):
    af = row.get("aftershave") or ""
    for p in [x.strip() for x in af.split(" | ")]:
        if emb_re.search(p) and hom_re.search(p):
            return p
    return None

cool_re = re.compile(r"menthol|ws-?23|cool|cold|chill|frost|ice|icy|tingl", re.I)
nocoo_re = re.compile(r"no(t)?\s+(cool|menthol|ws-?23)|not cool|uncool|no cooling|without (any )?(cool|menthol)|doesn'?t (cool|have)", re.I)
uncool_word = re.compile(r"uncool", re.I)

print()
print("=== hugbckt rows mentioning Embrace in ANY field ===")
hug = [r for r in ROWS if r.get("author") == "hugbckt" and any(emb_re.search(str(r.get(k) or "")) for k in ("aftershave", "soap", "fragrance", "razor", "brush", "blade", "notes"))]
hug.sort(key=lambda r: r.get("thread_date", ""))
print("count:", len(hug))
for r in hug:
    print(f"{r.get('thread_date')} | AS: {r.get('aftershave')} | SOAP: {r.get('soap')} | FRAG: {r.get('fragrance')} | NOTES: {(r.get('notes') or '')[:400]}")

print()
print("=== ALL Embrace splash rows with uncool/no-cool language in notes ===")
hits = []
for r in ROWS:
    p = embrace_splash(r)
    if p:
        hits.append((r.get("thread_date"), r.get("author"), p, r.get("notes") or ""))
hits.sort()
print("Embrace aftershave-field rows:", len(hits), "| range:", hits[0][0] if hits else None, "->", hits[-1][0] if hits else None)
for d, a, p, n in hits:
    if uncool_word.search(n) or nocoo_re.search(n):
        print(f"{d} {a} :: {p} :: {n[:400]}")

print()
print("=== ALL Embrace splash rows with ANY cooling language in notes ===")
for d, a, p, n in hits:
    if cool_re.search(n):
        print(f"{d} {a} :: {p} :: {n[:400]}")

print()
print("=== Embrace splash authors ===")
print(Counter(a for _, a, _, _ in hits).most_common())
print()
print("=== hugbckt ALL rows (count + date range) ===")
allhug = [r for r in ROWS if r.get("author") == "hugbckt"]
print(len(allhug), allhug[0].get("thread_date") if allhug else None, "->", allhug[-1].get("thread_date") if allhug else None)
