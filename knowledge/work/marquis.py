import json, glob
from collections import Counter
c = Counter(); dates = []
for f in sorted(glob.glob('/home/hatch/workspace/sotd/sotd_*_full.json')):
    d = json.load(open(f))
    for r in d:
        if r.get('author') == 'Marquis90' and 'rumble' in (r.get('aftershave') or '').lower():
            c[r['thread_date'][:4]] += 1
            dates.append(r['thread_date'])
print('Marquis90 Rumble AS rows by year:', dict(sorted(c.items())))
print('first:', min(dates), 'last:', max(dates), 'total:', len(dates))
c2 = Counter()
for f in sorted(glob.glob('/home/hatch/workspace/sotd/sotd_*_full.json')):
    d = json.load(open(f))
    for r in d:
        if r.get('author') == 'Marquis90' and 'rumble' in (r.get('soap') or '').lower():
            c2[r['thread_date'][:4]] += 1
print('Marquis90 Rumble soap rows by year:', dict(sorted(c2.items())))
