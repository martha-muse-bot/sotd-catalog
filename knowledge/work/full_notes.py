import json, glob, sys
targets = [
 ("FredBikes9876","2025-02-24"),("FredBikes9876","2025-03-19"),("FredBikes9876","2025-06-14"),
 ("Marquis90","2026-05-30"),("Marquis90","2025-05-26"),("Marquis90","2025-05-19"),
 ("tsrblke","2024-11-05"),("ashbeowulf_returns","2025-04-21"),("partyman97_3","2025-06-11"),
 ("schontzm","2025-05-10"),("loudmusicboy","2025-06-25"),("tsrblke","2023-11-29"),
]
want = {(a,d) for a,d in targets}
for f in sorted(glob.glob('/home/hatch/workspace/sotd/sotd_*_full.json')):
    d=json.load(open(f))
    for r in d:
        if (r.get('author'), r.get('thread_date')) in want:
            print('='*100)
            print(r['thread_date'], r['author'], '| razor:', r.get('razor'), '| soap:', r.get('soap'), '| AS:', r.get('aftershave'))
            print((r.get('notes') or '')[:3000])
