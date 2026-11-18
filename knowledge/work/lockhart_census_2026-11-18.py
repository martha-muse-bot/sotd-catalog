#!/usr/bin/env python3
"""Lockhart's / B&M x Lockhart census, 2026-11-18 learner run.
Reproduces: Lockhart rows by field, Terror Again rows, Reborn rows.
Input: ~/workspace/sotd/sotd_*_full.json (241,364 rows, max thread_date 2026-11-16).
"""
import json, glob

total = 0
lockhart = []
terror = []
for f in sorted(glob.glob('/home/hatch/workspace/sotd/sotd_*_full.json')):
    data = json.load(open(f))
    total += len(data)
    for r in data:
        blob = json.dumps(r).lower()
        if 'lockhart' in blob:
            lockhart.append(r)
        fields = ' | '.join(str(r.get(k) or '') for k in
                            ['soap', 'aftershave', 'fragrance', 'notes'])
        if 'terror again' in fields.lower():
            terror.append(r)

def has(r, field, needle='lockhart'):
    v = r.get(field)
    return isinstance(v, str) and needle in v.lower()

print(f"rows: {total}  lockhart rows: {len(lockhart)}")
print("soap-field:", sum(1 for r in lockhart if has(r, 'soap')),
      "| aftershave-field:", sum(1 for r in lockhart if has(r, 'aftershave')),
      "| fragrance-field:", sum(1 for r in lockhart if has(r, 'fragrance')))
print("--- Lockhart soap/aftershave-field rows ---")
for r in sorted(lockhart, key=lambda x: x.get('thread_date') or ''):
    if has(r, 'soap') or has(r, 'aftershave'):
        print(r.get('thread_date'), r.get('author'),
              '| soap:', (r.get('soap') or '')[:90],
              '| as:', (r.get('aftershave') or '')[:90])
print(f"--- 'terror again' rows (all fields): {len(terror)} ---")
for r in sorted(terror, key=lambda x: x.get('thread_date') or ''):
    print(r.get('thread_date'), r.get('author'),
          '| soap:', (r.get('soap') or '')[:80],
          '| as:', (r.get('aftershave') or '')[:80])
