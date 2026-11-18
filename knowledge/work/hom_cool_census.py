import json, glob, re
SCENTS = ["shire","voices","everett","rumble","alive","beloved","hygge","embrace",
          "santa noir","fú dào","fu dao","you & i","you and i","indigo","mood indigo",
          "sonder","kryptonite","tobacconist","mull","snippid","z ","dinos'mores",
          "ausflug","uitwaaien","damocles","jitterbug","almond leather","smash"]
COOL = re.compile(r"menthol|ws-?23|uncool|not cool|no cooling|cooling|chilly|ice cold|freez|cold (splash|blast|tingle|feel)|cool (splash|blast|tingle)", re.I)
rows=[]
for f in sorted(glob.glob('/home/hatch/workspace/sotd/sotd_*_full.json')):
    d=json.load(open(f))
    for r in d:
        af=(r.get('aftershave') or '')
        if 'mammoth' not in af.lower(): continue
        notes=r.get('notes') or ''
        if not COOL.search(notes): continue
        rows.append(r)
print('candidate rows:', len(rows))
def scent_of(af):
    a=af.lower()
    for s in SCENTS:
        if s.strip() in a: return s.strip()
    return '??'
from collections import defaultdict
by=defaultdict(list)
for r in rows:
    by[scent_of(r.get('aftershave') or '')].append(r)
for s in sorted(by):
    rs=sorted(by[s], key=lambda r: r['thread_date'])
    print(f"\n=== {s}: {len(rs)} rows, {rs[0]['thread_date']} -> {rs[-1]['thread_date']}")
    for r in rs:
        n=(r.get('notes') or '').replace('\n',' ')
        m=COOL.search(n)
        print(f"  {r['thread_date']} {r['author']}: ...{n[max(0,m.start()-60):m.end()+80]}...")
