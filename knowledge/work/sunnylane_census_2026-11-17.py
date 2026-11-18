import json, glob, re
rows=[]
for f in sorted(glob.glob('sotd_*_full.json')):
    with open(f) as fh:
        d=json.load(fh)
    for r in d:
        blob=json.dumps(r).lower()
        if 'sunny lane' in blob or 'sunnylane' in blob:
            rows.append(r)
print('ROWS', len(rows))
for r in sorted(rows, key=lambda x:(x.get('thread_date',''), x.get('author',''))):
    print(r.get('thread_date'), r.get('author'),
          '| soap:', r.get('soap'), '| as:', r.get('aftershave'), '| frag:', r.get('fragrance'),
          '| notes:', (r.get('notes') or '')[:200])
