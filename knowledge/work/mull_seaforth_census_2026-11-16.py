import json, glob, re
files = sorted(glob.glob('sotd_*_full.json'))
total = 0; maxd = ''
newrows = 0
mull_rows = []
hom_seaforth = []
pattern_hits = 0
pats = ['formerly','used to be','rebrand','now called','aka','same as','bought out','closed']
for f in files:
    rows = json.load(open(f))
    for r in rows:
        if r is None: continue
        total += 1
        d = r.get('thread_date','') or ''
        if d > maxd: maxd = d
        if d >= '2026-11-15': newrows += 1
        af = (r.get('aftershave') or '')
        soap = (r.get('soap') or '')
        frag = (r.get('fragrance') or '')
        fields = af + ' | ' + soap + ' | ' + frag
        if re.search(r'\bmull\b', fields, re.I) and 'mammoth' in fields.lower():
            mull_rows.append((d, r.get('author'), af[:90]))
        if 'seaforth' in fields.lower() and 'mammoth' in fields.lower():
            hom_seaforth.append((d, r.get('author'), af[:90], soap[:60]))
        notes = (r.get('notes') or '').lower()
        if d >= '2026-11-15' and any(p in notes for p in pats):
            pattern_hits += 1
print('total rows:', total, '| max thread_date:', maxd)
print('rows >= 2026-11-15:', newrows)
print('notes-pattern hits in new slice:', pattern_hits)
print('Mull (HoM) field rows:', len(mull_rows))
for m in mull_rows: print('  ', m)
print('HoM+Seaforth field rows:', len(hom_seaforth))
for s in hom_seaforth: print('  ', s)
