#!/usr/bin/env python3
"""DG brush-line census for the learner run 2026-11-04.
Collect brush-field strings and notes mentions of Declaration Grooming /
DG / L&L brush components (knots, handles)."""
import json, glob, re, collections

FILES = sorted(glob.glob('/home/hatch/workspace/sotd/sotd_*_full.json'))

BRUSH_HIT = re.compile(r'declaration grooming|declaration|l&l grooming|l&l\b|\bdg\b', re.I)
# notes pattern: DG knots/handles discussed outside structured fields
NOTE_HIT = re.compile(r'\bdg\b.*(?:knot|brush|handle)|(?:knot|brush|handle).*\bdg\b|declaration grooming.*(?:knot|brush|handle)', re.I)

brush_strings = collections.Counter()
brush_authors = collections.defaultdict(set)
brush_years = collections.defaultdict(lambda: [3000, 0])
note_hits = collections.Counter()
note_examples = {}

for fp in FILES:
    year = fp.split('sotd_')[1][:4]
    with open(fp) as f:
        data = json.load(f)
    for r in data:
        b = (r.get('brush') or '')
        a = r.get('author', '')
        if BRUSH_HIT.search(b):
            brush_strings[b] += 1
            brush_authors[b].add(a)
            lo, hi = brush_years[b]
            y = int(year)
            brush_years[b] = [min(lo, y), max(hi, y)]
        n = r.get('notes') or ''
        if NOTE_HIT.search(n):
            hkey = (b, a, year)
            note_hits[hkey] += 1
            if hkey not in note_examples:
                # store a snippet of the notes around the hit
                m = NOTE_HIT.search(n)
                s = max(0, m.start() - 160); e = min(len(n), m.end() + 160)
                note_examples[hkey] = (fp, n[s:e].replace('\n', ' | '))

print('=== BRUSH-FIELD STRINGS (distinct) ===')
print('distinct strings:', len(brush_strings))
print('total uses:', sum(brush_strings.values()))
print()
for s, c in brush_strings.most_common():
    lo, hi = brush_years[s]
    print(f'{c:5d} uses  {len(brush_authors[s]):3d} authors  {lo}-{hi}  | {s}')
print()
print('=== NOTES MENTIONS (DG + knot/brush/handle) ===')
print('distinct (brushstring,author,year) rows:', len(note_hits))
print()
# aggregate note snippets by author+year, show top
shown = 0
for (b, a, y), c in note_hits.most_common(60):
    fp, snippet = note_examples[(b, a, y)]
    print(f'[{y}] {a} (brush field: {b[:60]!r}) x{c}')
    print(f'     ...{snippet[:300]}')
    shown += 1
