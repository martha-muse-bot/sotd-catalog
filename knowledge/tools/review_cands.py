#!/usr/bin/env python3
"""Review helper (fast): dump candidate rows with per-row author + note
samples, using the prebuilt string_index.pkl. Usage:
  review_cands.py <cands.json> <start> <end>
"""
import json, pickle, sys

FILE = sys.argv[1] if len(sys.argv) > 1 else \
    '/home/hatch/workspace/sotd/knowledge/tools/misspelling_cands_artisan_2026-11-04.json'
rows = json.load(open(FILE))
start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
end = int(sys.argv[3]) if len(sys.argv) > 3 else start + 50
idx = pickle.load(open('/home/hatch/workspace/sotd/knowledge/tools/string_index.pkl','rb'))

for i in range(start, min(end, len(rows))):
    r = rows[i]
    print(f"[{i}] {r['uses']}u/{r['authors']}a {','.join(r['fields'])} "
          f"d={r['dist']} | {r['typed']!r} -> {r['entry']} ({r['entry_id']})")
    for au, note in idx.get(r['typed'], [])[:3]:
        n = note.replace('\n',' ')[:150]
        print(f"      @{au}: {n}")
    print()
print(f'shown {start}..{min(end,len(rows))} of {len(rows)}')
