import json, glob, re
pat = re.compile(r'discontinu|no more|retir|sold out|last chance|gone for good|final batch|farewell', re.I)
rows = []
for f in sorted(glob.glob('sotd_*_full.json')):
    with open(f) as fh:
        data = json.load(fh)
    for r in data:
        d = str(r.get('thread_date',''))
        if not ('2025-05-01' <= d <= '2025-06-30'):
            continue
        blob = ' '.join(str(r.get(k,'')) for k in ('soap','aftershave','fragrance','notes','other'))
        if 'indigo' not in blob.lower():
            continue
        if pat.search(blob):
            rows.append((d, r.get('author'), {k: r.get(k) for k in ('soap','aftershave','fragrance','notes') if r.get(k) and ('indigo' in str(r.get(k)).lower() or pat.search(str(r.get(k))))}))
print(len(rows), 'candidate rows')
for d, a, fields in sorted(rows):
    print(d, '|', a, '|', fields)
