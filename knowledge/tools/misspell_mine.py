#!/usr/bin/env python3
"""Learner misspellings mining: pair unmatched dataset strings against
near-miss verified catalog products to harvest typed->meant pairs."""
import json, sqlite3, glob, re, unicodedata
from collections import Counter, defaultdict

BASE = '/home/hatch/workspace/sotd'
FIELDS = ['razor', 'blade', 'brush', 'soap', 'aftershave', 'fragrance', 'preshave', 'bowl']

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-z0-9 ]', ' ', s.lower())
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# --- targets: verified entries ---
con = sqlite3.connect(f'{BASE}/catalog/catalog.db')
targets = {}   # norm name -> (entry_id, display)
for eid, brand, product, data in con.execute(
        "select id, brand, product, data from entries where status='verified'"):
    try:
        d = json.loads(data)
    except Exception:
        d = {}
    names = set()
    if brand and product:
        names.add(f'{brand} {product}')
    if product:
        names.add(product)
    if brand:
        names.add(brand)
    for a in (d.get('aliases') or []) + (d.get('loose_aliases') or []):
        if isinstance(a, str):
            names.add(a)
    for n in names:
        nn = norm(n)
        if len(nn) >= 3:
            targets.setdefault(nn, (eid, f'{brand} {product}'))
print('target names:', len(targets))

# --- unmatched strings ---
counts = Counter()
authors = defaultdict(set)
field_hits = defaultdict(set)
for f in sorted(glob.glob(f'{BASE}/matched_*.json')):
    for post in json.load(open(f)):
        a = post.get('author') or ''
        for fld in FIELDS:
            s = post.get(fld)
            if not s or not isinstance(s, str):
                continue
            m = (post.get('matches') or {}).get(fld)
            unmatched = (m is None) or (isinstance(m, dict) and
                                        str(m.get('id', '')).startswith('unverified/'))
            if unmatched:
                counts[(s, fld)] += 1
                authors[(s, fld)].add(a)
                field_hits[s].add(fld)

agg = defaultdict(lambda: [0, set(), set()])
for (s, fld), c in counts.items():
    a = agg[s]
    a[0] += c
    a[1] |= authors[(s, fld)]
    a[2] |= field_hits[s]

print('distinct unmatched strings:', len(agg))

# --- candidate filter ---
cands = []
target_set = set(targets)
for s, (uses, au, fl) in agg.items():
    ns = norm(s)
    if len(ns) < 4 or uses < 2 or ns in target_set:
        continue
    if re.fullmatch(r'[0-9 ]+', ns):
        continue
    cands.append((s, ns, uses, len(au), sorted(fl)))
print('candidates after filter:', len(cands))

def lev(a, b, limit):
    if abs(len(a) - len(b)) > limit:
        return limit + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        row_min = i
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            v = min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + cost)
            cur.append(v)
            if v < row_min:
                row_min = v
        if row_min > limit:
            return limit + 1
        prev = cur
    return prev[-1]

# block targets by (first char, length)
blocks = defaultdict(list)
for nn, info in targets.items():
    blocks[(nn[0] if nn else '', len(nn))].append((nn, info))

results = []
for s, ns, uses, nauth, fl in cands:
    lim = 2 if len(ns) < 12 else 3
    best = None
    for L in range(max(1, len(ns) - lim), len(ns) + lim + 1):
        for nn, info in blocks.get((ns[0], L), []):
            d = lev(ns, nn, lim)
            if d <= lim and (best is None or d < best[0]):
                best = (d, nn, info)
                if d <= 1:
                    break
    if best:
        results.append((uses, best[0], s, ns, best[1], best[2], nauth, fl))

results.sort(key=lambda r: (-r[0], r[1]))
print('near-miss pairs:', len(results))
out = [{'uses': u, 'authors': na, 'fields': fl, 'typed': s, 'typed_norm': ns,
        'dist': d, 'target_norm': tn, 'entry_id': eid, 'entry': disp}
       for u, d, s, ns, tn, (eid, disp), na, fl in results[:400]]
json.dump(out, open('/tmp/misspelling_cands.json', 'w'), indent=1, ensure_ascii=False)
print('wrote /tmp/misspelling_cands.json, top-400')
