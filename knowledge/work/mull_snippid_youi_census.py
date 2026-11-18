import json, glob, re
from collections import Counter
COOL = re.compile(r"menthol|ws-?23|uncool|not cool|no cooling|cooling|chilly|ice cold|freez|cold (splash|blast|tingle|feel)|cool (splash|blast|tingle)", re.I)
NEWB = re.compile(r"new bottle|cracked open|fresh bottle|just (got|received|picked up|bought)|first (use|time)|mail ?call|haul", re.I)

def is_mammoth(r):
    af = (r.get('aftershave') or '').lower()
    return 'mammoth' in af

mull_all, snip_all, yi_all = [], [], []
for f in sorted(glob.glob('/home/hatch/workspace/sotd/sotd_*_full.json')):
    for r in json.load(open(f)):
        af = (r.get('aftershave') or '')
        a = af.lower()
        if 'mammoth' not in a:
            continue
        if 'mull' in a:
            mull_all.append(r)
        if 'snippid' in a:
            snip_all.append(r)
        if "you & i" in a or "you and i" in a or "you &amp; i" in a:
            yi_all.append(r)

print(f"Mull AS rows: {len(mull_all)}; Snippid AS rows: {len(snip_all)}; You & I AS rows: {len(yi_all)}")
print("Mull authors:", Counter(r['author'] for r in mull_all).most_common(10))
print("Snippid authors:", Counter(r['author'] for r in snip_all).most_common(10))
print("You & I rows by year:", Counter(r['thread_date'][:4] for r in yi_all))

print("\n=== Mull: ALL rows (date, author, AS field) ===")
for r in sorted(mull_all, key=lambda x: x['thread_date']):
    print(f"  {r['thread_date']} {r['author']}: {r.get('aftershave')!r}")

print("\n=== Snippid: ALL rows (date, author, AS field) ===")
for r in sorted(snip_all, key=lambda x: x['thread_date']):
    print(f"  {r['thread_date']} {r['author']}: {r.get('aftershave')!r}")

print("\n=== Mull: cooling-language rows, full notes ===")
for r in sorted(mull_all, key=lambda x: x['thread_date']):
    if COOL.search(r.get('notes') or ''):
        print(f"\n--- {r['thread_date']} {r['author']} | AS={r.get('aftershave')!r}")
        print((r.get('notes') or '').replace('\n', ' ')[:900])

print("\n=== Snippid: cooling-language rows, full notes ===")
for r in sorted(snip_all, key=lambda x: x['thread_date']):
    if COOL.search(r.get('notes') or ''):
        print(f"\n--- {r['thread_date']} {r['author']} | AS={r.get('aftershave')!r}")
        print((r.get('notes') or '').replace('\n', ' ')[:900])

print("\n=== You & I: rows inside maker bracket (2024-11-10, 2025-02-10] ===")
for r in sorted(yi_all, key=lambda x: x['thread_date']):
    d = r['thread_date']
    if '2024-11-10' < d <= '2025-02-10':
        print(f"\n--- {d} {r['author']} | AS={r.get('aftershave')!r}")
        print((r.get('notes') or '').replace('\n', ' ')[:900])

print("\n=== You & I: cooling/new-bottle rows, ALL dates, full notes ===")
for r in sorted(yi_all, key=lambda x: x['thread_date']):
    if COOL.search(r.get('notes') or '') or NEWB.search(r.get('notes') or ''):
        print(f"\n--- {r['thread_date']} {r['author']} | AS={r.get('aftershave')!r}")
        print((r.get('notes') or '').replace('\n', ' ')[:900])

print("\n=== You & I: ALL rows (date, author) ===")
for r in sorted(yi_all, key=lambda x: x['thread_date']):
    print(f"  {r['thread_date']} {r['author']}: {r.get('aftershave')!r}")
