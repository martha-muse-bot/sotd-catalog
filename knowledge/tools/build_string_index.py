#!/usr/bin/env python3
"""Build once: exact-string -> [(author, notes)] index over matched_*.json.
Slow (~minutes); run in background. Cache lives in knowledge/tools/."""
import json, glob, pickle
idx = {}
FIELDS = ['razor','blade','brush','soap','aftershave','bowl','fragrance','preshave']
for f in sorted(glob.glob('/home/hatch/workspace/sotd/matched_*.json')):
    for post in json.load(open(f)):
        a = post.get('author') or '?'
        n = post.get('notes') or ''
        for fld in FIELDS:
            s = post.get(fld)
            if s and isinstance(s, str):
                idx.setdefault(s, []).append((a, n))
pickle.dump(idx, open('/home/hatch/workspace/sotd/knowledge/tools/string_index.pkl','wb'),
            protocol=4)
print('indexed strings:', len(idx))
