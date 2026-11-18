#!/usr/bin/env python3
"""(c4-narrow-168) Rumble new-bottle evidence census.
Find every aftershave-field HoM Rumble row and print date/author/notes,
flagging new-bottle / recent-purchase language and cooling language.
Also: all Rumble splash rows 2025-2026 with any cooling-related note.
"""
import json, glob, re

ROWS = []
for f in sorted(glob.glob("/home/hatch/workspace/sotd/sotd_*_full.json")):
    ROWS.extend(json.load(open(f)))
print("corpus rows:", len(ROWS))

def is_rumble_splash(row):
    af = row.get("aftershave") or ""
    parts = [p.strip() for p in af.split(" | ")]
    for p in parts:
        if re.search(r"\brumble\b", p, re.I) and re.search(r"mammoth|house of mammoth|\bhom\b", p, re.I):
            return p
    return None

cool_re = re.compile(r"menthol|ws-?23|cool|cold|chill|frost|ice|icy|tingl", re.I)
newb_re = re.compile(r"new bottle|fresh bottle|just (got|received|arrived|bought|picked)|recently (bought|purchased|ordered|received)|new (splash|aftershave)|arrived (today|yesterday|this week)|just arrived", re.I)
nocoo_re = re.compile(r"no(t|t\s+any)?\s+(cool|menthol|ws-?23)|not cool|uncool|no cooling|without (any )?(cool|menthol)", re.I)

hits = []
for r in ROWS:
    p = is_rumble_splash(r)
    if p:
        hits.append((r.get("thread_date"), r.get("author"), p, r.get("notes") or ""))
hits.sort()
print("Rumble aftershave-field rows:", len(hits))
print("date range:", hits[0][0], "->", hits[-1][0] if hits else None)
print()
print("=== ALL rows with cooling language or new-bottle language in notes ===")
for d, a, p, n in hits:
    flags = []
    if cool_re.search(n): flags.append("COOL")
    if newb_re.search(n): flags.append("NEWBOTTLE")
    if nocoo_re.search(n): flags.append("NOCOOL")
    if flags:
        print(f"{d} {a} [{','.join(flags)}] :: {p} :: {n[:400]}")
print()
print("=== ALL rows 2025-2026 (date/author/product) ===")
for d, a, p, n in hits:
    if d and d >= "2025-01-01":
        print(f"{d} {a} :: {p}")
print()
print("=== authors ===")
from collections import Counter
print(Counter(a for _, a, _, _ in hits).most_common())
