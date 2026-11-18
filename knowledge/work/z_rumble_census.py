import json, glob, re
COOL = re.compile(r"menthol|ws-?23|uncool|not cool|no cooling|cooling|chilly|ice cold|freez|cold (splash|blast|tingle|feel)|cool (splash|blast|tingle)", re.I)
NEWB = re.compile(r"new bottle|cracked open|fresh bottle|just (got|received|picked up|bought)|first (use|time)|mail ?call|haul", re.I)

def is_z(af):
    a = af.lower()
    return 'mammoth' in a and re.search(r'\bz\b', a) and 'splash' in a or ('mammoth' in a and ' z ' in a)

def is_rumble(af):
    a = af.lower()
    return 'mammoth' in a and 'rumble' in a

z_rows, r_rows, z_all, r_all = [], [], [], []
for f in sorted(glob.glob('/home/hatch/workspace/sotd/sotd_*_full.json')):
    for r in json.load(open(f)):
        af = (r.get('aftershave') or '')
        a = af.lower()
        if 'mammoth' not in a:
            continue
        # Z splash: aftershave field contains mammoth + standalone Z token
        if re.search(r'\bz\b', a) and 'zingari' not in a:
            z_all.append(r)
            if COOL.search(r.get('notes') or ''):
                z_rows.append(r)
        if 'rumble' in a:
            r_all.append(r)
            if COOL.search(r.get('notes') or '') or NEWB.search(r.get('notes') or ''):
                r_rows.append(r)

print(f"Z all rows: {len(z_all)}; Z cooling-language rows: {len(z_rows)}")
print(f"Rumble all rows: {len(r_all)}; Rumble cool/newbottle rows: {len(r_rows)}")

print("\n=== Z splash: ALL rows (date, author, aftershave field) ===")
for r in sorted(z_all, key=lambda x: x['thread_date']):
    print(f"  {r['thread_date']} {r['author']}: {r.get('aftershave')!r}")

print("\n=== Z splash: cooling-language rows, full notes ===")
for r in sorted(z_rows, key=lambda x: x['thread_date']):
    print(f"\n--- {r['thread_date']} {r['author']} | AS={r.get('aftershave')!r}")
    print((r.get('notes') or '').replace('\n', ' ')[:900])

print("\n=== Rumble: cooling/new-bottle rows, full notes ===")
for r in sorted(r_rows, key=lambda x: x['thread_date']):
    print(f"\n--- {r['thread_date']} {r['author']} | AS={r.get('aftershave')!r}")
    print((r.get('notes') or '').replace('\n', ' ')[:900])

print("\n=== Rumble: ALL rows count by year ===")
from collections import Counter
print(Counter(r['thread_date'][:4] for r in r_all))
print("Rumble authors:", Counter(r['author'] for r in r_all).most_common(10))
