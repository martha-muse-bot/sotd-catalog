#!/usr/bin/env python3
"""Generalized matcher over the sharded catalog (catalog/catalog_merged/<category>.json).

Fields blade/razor/soap/aftershave/fragrance: exact alias -> normalized ->
token-subset (most specific alias wins; ties across entries = ambiguous,
never forced), plus a reverse-subset phase for aliases carrying spec tokens
the poster omitted. Brush resolves via the brush-parts contract:
  {kind: complete|composite|knot_only|handle_only|series|ambiguous|unmatched,
   brush_id, handle_id, knot_id, series_id, specs_source, method}
Generation-scoped knot entries match before series-level ones (exact and
normalized phases hit their specific aliases first; the subset phase picks
the largest alias token set). Bare knot-type names with no seller named
match nothing -- no catalog entry carries such an alias.

Three resolution tiers (P-13, user ruling 2026-10-21): tier-1 =
verified/needs-review, tier-2 = attested/corroborated (their own middle
tier), tier-3 = unverified clusters. Precedence tier-1 > tier-2 >
unverified; a hit OR an ambiguity at a tier is final. Every stored match
records its tier; tier-2 hits report method "tier-2" (mirroring the
unverified tier's method "unverified").

Loose aliases (P-15, user ruling 2026-10-21): an entry may carry
`loose_aliases`, separate from its certain `aliases`. Each record names
an ambiguous string, the target entry (the entry carrying the record),
and a `basis_share` -- the target's share among identified uses of the
family. A declared loose alias governs its exact string unless an
explicit exact/normalized ASSERTED alias uniquely identifies that same
string; synthesized keys (the canonical brand+product key, the bare
product-name key) do not count as explicit and do not outrank a
declared loose alias (2026-10-28 fix). It takes precedence over subset/reverse-subset inference and
over ambiguities (e.g. "Shark (Egypt)" must not be captured by the bare
"Shark" cluster's subset hit). The loose-alias index itself matches
exact, then normalized. A
loose resolution reports method "loose-alias", `probabilistic: true`,
the matched `loose_alias`, and its `basis_share`. It retains the target
entry's tier for provenance, but coverage counts it in a separate
probable sub-line, never in the certain tier counts. A loose record may
carry `format_context` (e.g. "AC"): such a record is scoped to posts
whose paired razor/blade is in that format, is excluded from the
context-free loose index, and is consulted only by the hard format
filter below (bare "Feather" in an AC-razor post -> AC Professional).

Author-scoped aliases (§B4, user ruling 2026-10-21): an entry may carry
`author_scoped_aliases` -- records {alias, author, basis} declaring that
ONE named author's use of an ambiguous string is documentary-proven to
mean this entry (e.g. the author's own string history settles it). The
rule is a per-post contextual layer, like P-14: it fires only for posts
by that author, and only when the certain match is ambiguous or a clean
miss -- it never overrides a certain hit, and it is NOT probabilistic
(the proof is documentary, so resolutions count in their certain tier).
Stored matches report method "author-scoped" with `author_alias` and
`scoped_author`. Every other author's use of the same string is
untouched (the §B4 residue stays ambiguous, per the P-15 boundary).

Format agreement (P-14, user ruling 2026-10-21): blade and format must
agree within a post. When a blade string is ambiguous across formats, the
format of the razor matched in the same post narrows the candidates;
symmetrically, an ambiguous razor string is narrowed by the post's blade
format. A bare brand string (just the brand, e.g. "Kai", "Personna") for
a brand with entries in more than one format is NOT blanket-aliased:
the paired razor's format selects the format first, then the P-07
popularity default picks within that format (bare-alias holder, then the
format-generic product, then a single candidate, then a dominant
footprint). With no razor signal the context-free result stands (which
is where P-07 lives). Razor format comes from the razor entry's `type`
when it names a blade format, else from a format map derived in a
pre-pass from the same run's unambiguous razor<->specific-blade pairings
(>=3 posts, >=90% purity). P-14 resolutions carry method suffix
"+razor-format" / "+blade-format" (or bare "razor-format" when the
context-free pass had no hit).

Hard format constraint on defaults (P-14, user ruling 2026-10-21): no
default of any kind -- popularity default, P-15 loose alias, bare-brand
blanket hit, or a hit whose only identification basis is the bare-brand
alias (a "bare-decisive" subset capture, e.g. "Kai Captain Sharpblade"
landing on the DE Kai via its bare "Kai" record) -- may resolve a blade
against the format of the razor matched in the same post, or a razor
against the post's blade format. Certain evidence-based matches are
untouched; the constraint governs defaults only. Where the filter voids
a default, the fallback order is: (1) a within-format loose alias
recorded for that format context (scoped loose aliases); (2) the
certain match recomputed within the paired format (which may narrow to
a hit or to an ambiguity inside that format); (3) an ambiguity among
the brand's entries in that format; (4) unresolved. Relatedly, a
bare-decisive context-free hit yields to a specific identification of
the same string at a lower tier (the bare record is the weakest
identification in the system; a lower-tier entry whose own aliases
specifically match the string outranks it).

Composite split (P-25, user ruling 2026-11-16): a field string joining
two or more products splits at match time so each part matches its own
entry (dataset rows untouched; each matched part counts as one use of
its product). Per-field separator table + guard G0-G6 per
catalog/multi_item_field_analysis_2026-11-16.md §5/§8; nothing splits
in brush. A row failing any guard clause stays whole. Set
SPLIT_ENABLED = False to disable splitting without an edit.

Comma carve-out (variant (e), user ruling 2026-11-17): paren-aware
comma-joined strings split under the strict discipline of
catalog/comma_carveout_scoping_2026-11-17.md run 4 -- parts resolve via
exact/normalized ONLY, plus the alum fallback (O2, P-24-compliant) and
the weak-only P5 paren rule. Fields: aftershave, blade, razor,
fragrance; soap is held. Runs only when the P-25 split did not fire.
Set COMMA_SPLIT_ENABLED = False to disable the carve-out without an
edit.

Usage: python3 match_all.py [years...]  (default 2026 2025 2024 2022)
Writes ~/workspace/sotd/matched_<year>.json and catalog/coverage_report.md.
"""
import glob, html, json, re, sys
from collections import Counter, defaultdict

SOTD = '/home/hatch/workspace/sotd/'
CAT = SOTD + 'catalog/'

def N(s):
    """Normalization identical to match_blades.py v1."""
    if not s: return ''
    s = s.lower()
    s = re.sub(r'https?://\S+', ' ', s)
    s = re.sub(r'\(\d[^)]*\)', ' ', s)
    s = re.sub(r'\[\d+\]', ' ', s)
    s = re.sub(r'\b(double edge|de)\s*$', ' ', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def T(s):
    return frozenset(N(s).split())

# ---------------- catalog + indexes ----------------
# Sharded catalog (2026-11-18): one file per category under
# catalog/catalog_merged/<category>.json; concatenated in deterministic
# sorted-filename order. The single catalog_merged.json is retired.
merged = []
for _f in sorted(glob.glob(CAT + 'catalog_merged/*.json')):
    merged.extend(json.load(open(_f))['entries'])
BY_ID = {e['id']: e for e in merged}
SIMPLE_FIELDS = {'blade': 'blade', 'razor': 'razor', 'soap': 'soap',
                 'aftershave': 'aftershave', 'fragrance': 'fragrance'}
BRUSH_CATS = ('brush', 'handle', 'knot')

PRIMARY_STATUSES = {'verified', 'needs-review'}
MID_STATUSES = {'attested', 'corroborated', 'anecdotal'}

def build_index(cats, statuses=None):
    exact = defaultdict(set)
    norm = defaultdict(set)
    explicit_norm = defaultdict(set)
    records = []            # (tokens, entry_id)
    by_token = defaultdict(set)
    def add_record(alias, eid):
        t = T(alias)
        if not t: return
        idx = len(records)
        records.append((t, eid))
        for tok in t: by_token[tok].add(idx)
    for e in merged:
        if e['category'] not in cats: continue
        if statuses and e.get('status') not in statuses: continue
        eid = e['id']
        for a in e['aliases']:
            exact[a].add(eid)
            norm[N(a)].add(eid)
            explicit_norm[N(a)].add(eid)
            add_record(a, eid)
        if e.get('brand') and e.get('product'):
            canon = f"{e['brand']} {e['product']}"
            norm[N(canon)].add(eid)
            add_record(canon, eid)
    # unique product-only normalized keys
    prod = defaultdict(set)
    for e in merged:
        if e['category'] in cats and not (statuses and e.get('status') not in statuses):
            prod[(e['category'], N(e['product']))].add(e['id'])
    for (cat, key), ids in prod.items():
        if len(ids) == 1 and key:
            norm[key].add(next(iter(ids)))
    return {'exact': exact, 'norm': norm, 'explicit_norm': explicit_norm, 'records': records, 'by_token': by_token}

def add_to_index(idx, alias, eid):
    idx['norm'][N(alias)].add(eid)
    idx['explicit_norm'][N(alias)].add(eid)
    t = T(alias)
    if t:
        ri = len(idx['records'])
        idx['records'].append((t, eid))
        for tok in t: idx['by_token'][tok].add(ri)

# series-level entries: within a series group, the entry whose id prefixes
# the generation-scoped siblings' ids (e.g. knot/chisel-and-hound-fanchurian
# vs ...-v21) is the series-level entry; bare series strings land there.
_series_groups = defaultdict(list)
for e in merged:
    if e.get('series'): _series_groups[e['series']].append(e)
SERIES_IDS = set()
for sname, es in _series_groups.items():
    if len(es) > 1:
        for e in es:
            if any(o['id'].startswith(e['id'] + '-') for o in es if o is not e):
                SERIES_IDS.add(e['id'])

INDEXES = {f: build_index((c,), PRIMARY_STATUSES) for f, c in SIMPLE_FIELDS.items()}
MID_INDEXES = {f: build_index((c,), MID_STATUSES) for f, c in SIMPLE_FIELDS.items()}
UV_INDEXES = {f: build_index((c,), {'unverified'}) for f, c in SIMPLE_FIELDS.items()}

# ---------------- P-15: loose (probabilistic) aliases ----------------
def _loose_alias_record(raw):
    """Normalize a loose-alias declaration to a dict, or None."""
    if isinstance(raw, str) and raw:
        return {'alias': raw}
    if isinstance(raw, dict) and raw.get('alias'):
        return raw
    return None

def build_loose_index(cat):
    """Exact/normalized index of `loose_aliases` for one category.

    Loose aliases live on their TARGET entry, separate from `aliases`, so
    the certain indexes above never see them. Values are (entry_id,
    record) pairs; the record carries at least `alias` and, when known,
    `basis_share` and `basis`.
    """
    exact = defaultdict(list)
    norm = defaultdict(list)
    for e in merged:
        if e['category'] != cat: continue
        for raw in e.get('loose_aliases') or []:
            rec = _loose_alias_record(raw)
            if not rec: continue
            if rec.get('format_context'):
                # Scoped to a paired-format context; consulted only by
                # the hard format filter, never context-free.
                continue
            item = (e['id'], rec)
            exact[rec['alias']].append(item)
            norm[N(rec['alias'])].append(item)
    return {'exact': exact, 'norm': norm}

LOOSE_INDEXES = {f: build_loose_index(c) for f, c in SIMPLE_FIELDS.items()}

def loose_match(s, idx):
    """Resolve `s` through the loose-alias index, or None.

    Exact form first, then normalized. A string declared for more than
    one target is not forced -- it stays unresolved probabilistically.
    """
    if not s: return None
    for key, table in ((s, idx['exact']), (N(s), idx['norm'])):
        items = table.get(key)
        if not items: continue
        ids = {eid for eid, _rec in items}
        if len(ids) != 1: return None
        eid = next(iter(ids))
        rec = next(rec for i, rec in items if i == eid)
        return {'id': eid, 'method': 'loose-alias',
                'tier': tier_of(eid), 'probabilistic': True,
                'loose_alias': rec['alias'],
                'basis_share': rec.get('basis_share')}
    return None

def explicit_certain_id(s, field):
    """The entry uniquely identified by an EXACT or NORMALIZED ASSERTED
    alias for `s` across the three tier indexes, or None.

    "Asserted" is the operative word: only aliases the catalog actually
    declares count here. Synthesized keys -- the canonical brand+product
    key and the bare product-name key -- do NOT count as explicit, even
    though they live in the same norm dict for ordinary matching: a
    declared P-15 loose alias outranks them (2026-10-28 Wilkinson /
    Feather Pro fix: without this, bare "Wilkinson Sword" resolved
    certain to Gillette via its product-name key, and "Feather Pro" to
    a typo cluster via its canonical key, despite ruled loose aliases).
    Subset/reverse-subset hits are inference, not explicit
    identification, and do not count here: a declared P-15 loose alias
    for the string outranks them. An explicit key shared by several
    entries is an ambiguity, which a loose alias may also resolve.
    """
    if not s: return None
    for idx in (INDEXES[field], MID_INDEXES[field], UV_INDEXES[field]):
        ids = idx['exact'].get(s) or idx['explicit_norm'].get(N(s))
        if ids:
            return next(iter(ids)) if len(ids) == 1 else None
    return None

# ---------------- author-scoped aliases (§B4) ----------------
def _author_alias_record(raw):
    """Normalize an author-scoped alias declaration to a dict, or None."""
    if isinstance(raw, dict) and raw.get('alias') and raw.get('author'):
        return raw
    return None

def build_author_index(cat):
    """Author-scoped alias index for one category.

    Scoped aliases live on their TARGET entry as `author_scoped_aliases`,
    separate from `aliases`, so the certain indexes never see them.
    Keys are (author.lower(), alias) in both exact and normalized form;
    values are (entry_id, record). Author comparison is case-insensitive
    (Reddit usernames are); the declaration records the dataset form.
    """
    exact = {}
    norm = {}
    for e in merged:
        if e['category'] != cat: continue
        for raw in e.get('author_scoped_aliases') or []:
            rec = _author_alias_record(raw)
            if not rec: continue
            item = (e['id'], rec)
            akey = str(rec['author']).lower()
            exact.setdefault((akey, rec['alias']), item)
            norm.setdefault((akey, N(rec['alias'])), item)
    return {'exact': exact, 'norm': norm}

AUTHOR_INDEXES = {f: build_author_index(c) for f, c in SIMPLE_FIELDS.items()}

def author_scoped_match(field, s, author, base):
    """Resolve through an author-scoped alias declared for this post's
    author, or None. Fires only when the certain result `base` is an
    ambiguity or a clean miss -- a certain hit always stands."""
    if not s or not author: return None
    if base and 'id' in base: return None
    idx = AUTHOR_INDEXES[field]
    akey = str(author).lower()
    item = idx['exact'].get((akey, s)) or idx['norm'].get((akey, N(s)))
    if not item: return None
    eid, rec = item
    return {'id': eid, 'method': 'author-scoped', 'tier': tier_of(eid),
            'author_alias': rec['alias'], 'scoped_author': rec['author']}

BRUSH_INDEX = build_index(BRUSH_CATS, PRIMARY_STATUSES)
BRUSH_MID_INDEX = build_index(('brush',), MID_STATUSES)
BRUSH_UV_INDEX = build_index(('brush',), {'unverified'})
# bare series strings resolve to the series-level entry
_last_words = defaultdict(set)
for eid in SERIES_IDS:
    _last_words[N(BY_ID[eid].get('series') or BY_ID[eid]['product']).split()[-1]].add(eid)
for eid in SERIES_IDS:
    sname = BY_ID[eid].get('series') or BY_ID[eid]['product']
    add_to_index(BRUSH_INDEX, sname, eid)
    last = N(sname).split()[-1]
    if len(_last_words[last]) == 1:
        add_to_index(BRUSH_INDEX, last, eid)

# ---------------- P-14: razor<->blade format agreement ----------------
def _fmt_norm(f):
    """Normalize a format name for comparison ('Half-DE' == 'Half DE')."""
    if not f: return None
    return re.sub(r'[^a-z0-9]', '', str(f).lower()) or None

def entry_format(e):
    """Blade format of a catalog entry: the `format` field, else the
    <Format>/ id prefix of a settled entry. None when unknown."""
    if e.get('format'): return _fmt_norm(e['format'])
    eid = e['id']
    if '/' in eid and not eid.startswith('unverified/'):
        return _fmt_norm(eid.split('/')[0])
    return None

def tier_of(eid):
    s = BY_ID[eid].get('status')
    if s in PRIMARY_STATUSES: return 'tier-1'
    if s in MID_STATUSES: return 'tier-2'
    return 'unverified'

# razor `type` values that name a blade format directly. 'Shavette',
# 'Straight' and 'SE' do not (a shavette may take AC, Half-DE or
# Hair Shaper blades) -- those razors get their format from the
# derived map below, or give no signal.
RAZOR_TYPE_FORMAT = {'de': 'de', 'ac': 'ac', 'gem': 'gem',
                     'injector': 'injector', 'cartridge': 'cartridge',
                     'fhs': 'fhs', 'a77': 'a77', 'halfde': 'halfde',
                     'hairshaper': 'hairshaper',
                     'durhamduplex': 'durhamduplex'}

# Derived razor-format map {razor entry id: normalized blade format},
# built by build_derived_razor_formats() from the current run's data.
DERIVED_RAZOR_FORMAT = {}

def razor_format_of_entry(eid):
    e = BY_ID.get(eid)
    if not e: return None
    t = _fmt_norm(e.get('type'))
    if t in RAZOR_TYPE_FORMAT: return RAZOR_TYPE_FORMAT[t]
    return DERIVED_RAZOR_FORMAT.get(eid)

def _footprint(e):
    return len(e.get('aliases') or []) + len(e.get('clusters') or [])

# products that ARE the format-generic product of their brand+format
# (e.g. Personna "Injector Blades" in Injector format): product tokens
# must all be format-descriptor words.
_GENERIC_PRODUCT_TOKENS = {
    'injector': {'injector', 'blade', 'blades'},
    'hairshaper': {'hair', 'shaper', 'blade', 'blades'},
    'de': {'de', 'double', 'edge', 'blade', 'blades'},
    'ac': {'ac', 'artist', 'club', 'blade', 'blades'},
    'gem': {'gem', 'single', 'edge', 'blade', 'blades'},
    'cartridge': {'cartridge', 'blade', 'blades'},
    'halfde': {'half', 'de', 'blade', 'blades'},
    'fhs': {'fhs', 'blade', 'blades'},
}

def _is_format_generic(e, fmt):
    toks = set(N(e.get('product') or '').split())
    allowed = _GENERIC_PRODUCT_TOKENS.get(fmt, {'blade', 'blades'})
    return bool(toks) and toks <= allowed

# Bare-brand detection: brands (normalized, single token) whose formatted
# blade entries span more than one format. A blade string that is just
# such a brand (optionally + "blade"/"blades") is a P-14 bare string.
BARE_BRAND_ENTRIES = {}
_brand_formats = defaultdict(set)
for e in merged:
    if e['category'] == 'blade' and e.get('brand'):
        f = entry_format(e)
        if f: _brand_formats[N(e['brand'])].add(f)
for e in merged:
    if e['category'] == 'blade' and e.get('brand'):
        key = N(e['brand'])
        if ' ' not in key and len(_brand_formats.get(key, ())) > 1:
            BARE_BRAND_ENTRIES.setdefault(key, []).append(e)

def bare_brand_key(s):
    """The bare-brand key of a blade string, or None. 'Kai' -> 'kai';
    'Personna Blades' -> 'personna'; 'Kai Stainless' -> None."""
    if not s: return None
    toks = [t for t in N(s).split() if t not in ('blade', 'blades')]
    if len(toks) == 1 and toks[0] in BARE_BRAND_ENTRIES: return toks[0]
    return None

def pick_bare_candidate(brand_key, fmt):
    """P-07 within the P-14-decided format: among the brand's formatted
    entries in `fmt`, take the highest tier present, then prefer (a) the
    entry holding the bare brand string as an alias, (b) the
    format-generic product, (c) a single candidate, (d) a dominant
    footprint (>=10 and >=3x the runner-up). None when no rule fires."""
    cands = [e for e in BARE_BRAND_ENTRIES[brand_key]
             if entry_format(e) == fmt]
    if not cands: return None
    for statuses in (PRIMARY_STATUSES, MID_STATUSES, {'unverified'}):
        tc = [e for e in cands if e.get('status') in statuses]
        if not tc: continue
        holders = [e for e in tc
                   if any(N(a) == brand_key for a in e.get('aliases') or ())]
        if len(holders) == 1: return holders[0]['id']
        if len(holders) > 1: return None
        gen = [e for e in tc if _is_format_generic(e, fmt)]
        if len(gen) == 1: return gen[0]['id']
        if len(gen) > 1: return None
        if len(tc) == 1: return tc[0]['id']
        fps = sorted(tc, key=_footprint, reverse=True)
        if _footprint(fps[0]) >= 10 and _footprint(fps[0]) >= 3 * _footprint(fps[1]):
            return fps[0]['id']
        return None
    return None

def _result_format(result, kind):
    """The format a match result speaks for: a hit's entry format, or
    the unanimous format of an ambiguity's candidates (every candidate's
    format known and identical). None otherwise."""
    if not result: return None
    if 'id' in result:
        e = BY_ID[result['id']]
        return entry_format(e) if kind == 'blade' else razor_format_of_entry(result['id'])
    if 'ambiguous' in result:
        get = (lambda eid: entry_format(BY_ID[eid])) if kind == 'blade' \
            else razor_format_of_entry
        fmts = [get(eid) for eid in result['ambiguous']]
        if fmts and all(fmts) and len(set(fmts)) == 1: return fmts[0]
    return None

def _p14_blade(s, base, razor_fmt, counter):
    """Apply P-14 to a blade result given the paired razor's format."""
    if not s or not razor_fmt: return base
    # bare brand first: it can override even a (wrong-format) hit, since
    # the hit typically comes from a blanket bare alias (P-07 artifact).
    bk = bare_brand_key(s)
    if bk:
        plain_fmt = entry_format(BY_ID[base['id']]) if base and 'id' in base else None
        if plain_fmt != razor_fmt:
            pick = pick_bare_candidate(bk, razor_fmt)
            if pick:
                counter['blade'] += 1
                return {'id': pick, 'method': 'razor-format',
                        'tier': tier_of(pick)}
    # ambiguity across formats: narrow by the razor's format.
    if base and 'ambiguous' in base:
        cands = base['ambiguous']
        fmts = {eid: entry_format(BY_ID[eid]) for eid in cands}
        if all(fmts.values()) and len(set(fmts.values())) > 1:
            keep = [eid for eid in cands if fmts[eid] == razor_fmt]
            if len(keep) == 1:
                counter['blade'] += 1
                return {'id': keep[0],
                        'method': (base.get('method') or 'ambiguous') + '+razor-format',
                        'tier': tier_of(keep[0])}
            if keep:
                return {'ambiguous': keep, 'method': base.get('method'),
                        'tier': base.get('tier')}
    return base

def _p14_razor(s, base, blade_fmt, counter):
    """Apply P-14 to a razor result given the paired blade's format:
    narrow a cross-format ambiguity to the agreeing candidate."""
    if not s or not blade_fmt or not base or 'ambiguous' not in base:
        return base
    cands = base['ambiguous']
    fmts = {eid: razor_format_of_entry(eid) for eid in cands}
    if all(fmts.values()) and len(set(fmts.values())) > 1:
        keep = [eid for eid in cands if fmts[eid] == blade_fmt]
        if len(keep) == 1:
            counter['razor'] += 1
            return {'id': keep[0],
                    'method': (base.get('method') or 'ambiguous') + '+blade-format',
                    'tier': tier_of(keep[0])}
        if keep:
            return {'ambiguous': keep, 'method': base.get('method'),
                    'tier': base.get('tier')}
    return base

# ---------------- hard format filter on defaults (P-14 constraint) ----
def _field_format(field, eid):
    """The format a match on `eid` speaks for, per field."""
    e = BY_ID.get(eid)
    if not e: return None
    return entry_format(e) if field == 'blade' else razor_format_of_entry(eid)

# Format-scoped loose aliases (records with `format_context`, excluded
# from the context-free loose index): consulted only by the filter,
# when the paired entry's format selects the record's context.
SCOPED_LOOSE_INDEXES = {}
for _f, _c in SIMPLE_FIELDS.items():
    _ex, _nm = {}, {}
    for e in merged:
        if e['category'] != _c: continue
        for raw in e.get('loose_aliases') or []:
            rec = _loose_alias_record(raw)
            if not rec or not rec.get('format_context'): continue
            item = (_fmt_norm(rec['format_context']), e['id'], rec)
            _ex.setdefault(rec['alias'], []).append(item)
            _nm.setdefault(N(rec['alias']), []).append(item)
    SCOPED_LOOSE_INDEXES[_f] = {'exact': _ex, 'norm': _nm}

def _scoped_loose_hit(field, s, fmt):
    """Fallback (1): a format-scoped loose alias for `s` whose context
    is `fmt` and whose target entry is itself in `fmt`, or None."""
    if not s or not fmt: return None
    idx = SCOPED_LOOSE_INDEXES[field]
    for key, table in ((s, idx['exact']), (N(s), idx['norm'])):
        items = [it for it in table.get(key, ()) if it[0] == fmt]
        ids = {eid for _cf, eid, _r in items}
        if len(ids) != 1: continue
        eid = next(iter(ids))
        if _field_format(field, eid) != fmt: continue
        rec = next(r for _cf, i, r in items if i == eid)
        return {'id': eid, 'method': 'loose-alias', 'tier': tier_of(eid),
                'probabilistic': True, 'loose_alias': rec['alias'],
                'basis_share': rec.get('basis_share')}
    return None

def _has_specific_basis(s, e, brand_key):
    """True when entry `e` identifies string `s` through something more
    specific than its bare-brand alias: a non-bare alias (exact,
    normalized, subset, or reverse-subset), the canonical
    brand+product, or the product-only key."""
    ts = T(s)
    if not ts: return False
    ns = N(s)
    for a in e.get('aliases') or ():
        if N(a) == brand_key or T(a) == {brand_key}: continue
        ta = T(a)
        if a == s or N(a) == ns or (ta and ta <= ts) or \
                (len(ts) >= 2 and ts <= ta):
            return True
    if e.get('brand') and e.get('product'):
        canon = f"{e['brand']} {e['product']}"
        tc = T(canon)
        # Guard: a canon whose tokens collapse to the bare brand alone
        # (e.g. product "DE" normalizes away, leaving {brand}) is the
        # bare alias again, not a specific basis.
        if N(canon) == ns or (tc and tc != {brand_key} and
                              (tc <= ts or (len(ts) >= 2 and ts <= tc))):
            return True
    if e.get('product') and N(e['product']) == ns:
        return True
    return False

_BARE_DECISIVE_CACHE = {}
def _bare_decisive(field, s, eid):
    """True when the hit on `eid` for string `s` rests solely on the
    bare-brand alias of a multi-format blade brand -- the weakest
    identification in the system, hence a default, not evidence
    (e.g. "Kai Captain Sharpblade" captured by the bare "Kai" record
    of the DE Kai entry, shadowing the AC Sharpblade entry)."""
    if field != 'blade' or not s: return False
    key = (s, eid)
    if key not in _BARE_DECISIVE_CACHE:
        e = BY_ID.get(eid)
        bk = N(e.get('brand') or '') if e else ''
        _BARE_DECISIVE_CACHE[key] = bool(
            e and bk in BARE_BRAND_ENTRIES
            and not _has_specific_basis(s, e, bk))
    return _BARE_DECISIVE_CACHE[key]

def _certain_within_format(field, s, fmt):
    """Fallback (2): the certain match for `s` recomputed under the
    format constraint. Walk the tiers in precedence order; at each,
    take that tier's winning candidate pool (its hit, or its ambiguity
    set) and keep only entries in `fmt`. The first tier with an
    in-format candidate decides: a hit if one remains, an ambiguity
    if several."""
    for idx, label in ((INDEXES[field], 'tier-1'),
                       (MID_INDEXES[field], 'tier-2'),
                       (UV_INDEXES[field], 'unverified')):
        eid, method, amb = _match_with_index(s, idx)
        pool = [eid] if eid else list(amb or ())
        keep = [i for i in pool if _field_format(field, i) == fmt]
        if not keep: continue
        m = method if label == 'tier-1' else label
        if len(keep) == 1:
            return {'id': keep[0], 'method': m, 'tier': label}
        return {'ambiguous': sorted(keep), 'method': m, 'tier': label}
    return None

RAZOR_BRAND_ENTRIES = defaultdict(list)
for e in merged:
    if e['category'] == 'razor' and e.get('brand'):
        RAZOR_BRAND_ENTRIES[N(e['brand'])].append(e)

_MF_RAZOR_BRANDS = None
def _multi_fmt_razor_brands():
    """Razor brands whose entries span more than one format (formats
    resolved lazily: the derived razor-format map is built per run)."""
    global _MF_RAZOR_BRANDS
    if _MF_RAZOR_BRANDS is None:
        _MF_RAZOR_BRANDS = {
            b for b, es in RAZOR_BRAND_ENTRIES.items()
            if len({razor_format_of_entry(e['id']) for e in es} - {None}) > 1}
    return _MF_RAZOR_BRANDS

def _brand_pool_within_format(field, s, hit_entry, fmt):
    """Fallback (3): the brand's entries in `fmt`, highest tier present
    -- an ambiguity if several, the single entry as a hit if one."""
    if field == 'blade':
        bk = bare_brand_key(s)
        if not bk: return None
        pool = [e for e in BARE_BRAND_ENTRIES[bk] if entry_format(e) == fmt]
    else:
        pool = [e for e in RAZOR_BRAND_ENTRIES.get(N(hit_entry.get('brand') or ''), ())
                if razor_format_of_entry(e['id']) == fmt]
    if not pool: return None
    for statuses, label in ((PRIMARY_STATUSES, 'tier-1'),
                            (MID_STATUSES, 'tier-2'),
                            ({'unverified'}, 'unverified')):
        tp = sorted(e['id'] for e in pool if e.get('status') in statuses)
        if not tp: continue
        if len(tp) == 1:
            return {'id': tp[0],
                    'method': 'razor-format' if field == 'blade' else 'blade-format',
                    'tier': label}
        return {'ambiguous': tp, 'method': 'ambiguous', 'tier': label}
    return None

def _is_default_hit(field, s, result):
    """Whether a hit is a DEFAULT resolution, governed by the hard
    format constraint, rather than a certain evidence-based match:
    a P-15 loose pick; a bare-brand string's hit; a bare-decisive hit;
    or (razor field) a bare brand string landing on a brand-generic
    entry of a multi-format razor brand."""
    if result.get('probabilistic') or result.get('method') == 'loose-alias':
        return True
    e = BY_ID[result['id']]
    if field == 'blade':
        if bare_brand_key(s): return True
        return _bare_decisive(field, s, result['id'])
    brand = N(e.get('brand') or '')
    if brand and N(s or '') == brand and brand in _multi_fmt_razor_brands():
        prod = N(e.get('product') or '')
        if prod in ('', brand, 'unspecified') or e.get('status') == 'unverified':
            return True
    return False

def _format_filter(field, s, result, other_fmt, counter):
    """Hard P-14 constraint: a DEFAULT hit may not resolve against the
    paired entry's format. Void it and fall back in the ruled order:
    (1) within-format (scoped) loose alias, (2) certain match
    recomputed within the format, (3) brand-pool ambiguity in the
    format, (4) unresolved. Certain matches are returned untouched."""
    if not s or not result or 'id' not in result or not other_fmt:
        return result
    fmt = _field_format(field, result['id'])
    if not fmt or fmt == other_fmt: return result
    if not _is_default_hit(field, s, result): return result
    counter[field] += 1
    scoped = _scoped_loose_hit(field, s, other_fmt)
    if scoped: return scoped
    within = _certain_within_format(field, s, other_fmt)
    if within: return within
    pool = _brand_pool_within_format(field, s, BY_ID[result['id']], other_fmt)
    if pool: return pool
    return None

def subset_candidates(idx, tokens):
    """Alias records whose token set is a subset of the string tokens,
    grouped by entry, keeping each entry's largest alias size."""
    if not tokens: return {}
    cand = None
    for tok in tokens:
        hits = idx['by_token'].get(tok, set())
        cand = set(hits) if cand is None else cand | hits
    best = {}
    for ri in cand or ():
        t, eid = idx['records'][ri]
        if t and t <= tokens:
            if eid not in best or len(t) > best[eid]: best[eid] = len(t)
    return best

def _match_with_index(s, idx):
    """-> (entry_id|None, method|None, ambiguous_ids|None)"""
    if not s: return (None, None, None)
    ids = idx['exact'].get(s)
    if ids:
        if len(ids) == 1: return (next(iter(ids)), 'exact', None)
        return (None, 'exact', sorted(ids))
    ids = idx['norm'].get(N(s))
    if ids:
        if len(ids) == 1: return (next(iter(ids)), 'normalized', None)
        return (None, 'normalized', sorted(ids))
    best = subset_candidates(idx, T(s))
    if best:
        top = max(best.values())
        winners = sorted(e for e, n in best.items() if n == top)
        if len(winners) == 1: return (winners[0], 'subset', None)
        return (None, 'subset', winners)
    # reverse subset: the string's tokens are all inside an alias (aliases
    # often carry spec tokens the poster omitted). Smallest such alias wins.
    tokens = T(s)
    if len(tokens) >= 2:
        cand = None
        for tok in tokens:
            hits = idx['by_token'].get(tok, set())
            cand = set(hits) if cand is None else cand & hits
        rev = {}
        for ri in cand or ():
            t, eid = idx['records'][ri]
            if tokens <= t and (eid not in rev or len(t) < rev[eid]):
                rev[eid] = len(t)
        if rev:
            low = min(rev.values())
            winners = sorted(e for e, n in rev.items() if n == low)
            if len(winners) == 1: return (winners[0], 'subset-rev', None)
            return (None, 'subset-rev', winners)
    return (None, None, None)

def match_with_index(s, idx):
    return _match_with_index(s, idx)

def match_field(s, idx, mid_idx, uv_idx):
    """Three-tier field match (P-13). The tier-1 (verified/needs-review)
    index decides first -- a hit OR an ambiguity there is final. A clean
    miss falls through to the tier-2 index (attested/corroborated), whose
    hits report method 'tier-2'; only another clean miss falls through to
    the unverified-tier index (method 'unverified'). Ambiguities surface
    with their tier's method. Returns (entry_id, method, ambiguous_ids,
    tier) with tier in {'tier-1', 'tier-2', 'unverified', None}."""
    eid, method, amb = _match_with_index(s, idx)
    if eid: return (eid, method, None, 'tier-1')
    if amb: return (None, method, amb, 'tier-1')
    eid, method, amb = _match_with_index(s, mid_idx)
    if eid: return (eid, 'tier-2', None, 'tier-2')
    if amb: return (None, 'tier-2', amb, 'tier-2')
    eid, method, amb = _match_with_index(s, uv_idx)
    if eid: return (eid, 'unverified', None, 'unverified')
    if amb: return (None, 'unverified', amb, 'unverified')
    return (None, None, None, None)

def contained_match(s, idx, cats):
    """Best entry of the given categories whose alias appears inside the
    string (normalized containment or token-subset). For composite parts."""
    ns = N(s); tokens = T(s)
    best = {}
    for t, eid in idx['records']:
        if BY_ID[eid]['category'] not in cats or not t: continue
        na = ' '.join(sorted(t))  # not used for containment; token path below
        if t <= tokens:
            if eid not in best or len(t) > best[eid]: best[eid] = len(t)
    if not best: return None
    top = max(best.values())
    winners = [e for e, n in best.items() if n == top]
    return winners[0] if len(winners) == 1 else None

DIM_RE = re.compile(r'\d{2}(?:\.\d+)?\s*(?:mm|×|x)\s*\d{2}|\b\d{2}(?:\.\d+)?\s*mm\b')

def specs_source(s, primary_entry):
    if s and DIM_RE.search(s): return 'poster'
    if primary_entry and primary_entry.get('specs'): return 'catalog'
    return None

def same_product_forms(ids):
    """True when ids are the same brand+product sold in multiple forms."""
    stems = {((BY_ID[i].get('brand') or '').lower(),
              (BY_ID[i].get('product') or BY_ID[i].get('label') or '').lower())
             for i in ids}
    return len(stems) == 1

def _match_brush_primary(s):
    empty = {'kind': 'unmatched', 'brush_id': None, 'handle_id': None,
             'knot_id': None, 'series_id': None, 'specs_source': None, 'method': None}
    if not s: return empty
    eid, method, amb = match_with_index(s, BRUSH_INDEX)
    if amb:
        if same_product_forms(amb):
            # same product sold as complete brush and as loose knot (e.g.
            # Maggard Black and White): resolve by the form named, default
            # to the complete brush.
            want = 'knot' if 'knot' in N(s) else 'brush'
            pick = [i for i in amb if BY_ID[i]['category'] == want]
            if len(pick) == 1:
                eid, method = pick[0], method + '+form-default'
                amb = None
        if amb:
            out = dict(empty); out['kind'] = 'ambiguous'; out['method'] = method
            out['ambiguous'] = amb
            return out
    if eid:
        e = BY_ID[eid]
        if eid in SERIES_IDS:
            return {'kind': 'series', 'brush_id': None, 'handle_id': None,
                    'knot_id': None, 'series_id': eid,
                    'specs_source': specs_source(s, e), 'method': method}
        if e['category'] == 'brush':
            return {'kind': 'complete', 'brush_id': eid, 'handle_id': None,
                    'knot_id': None, 'series_id': None,
                    'specs_source': specs_source(s, e), 'method': method}
        if e['category'] == 'knot':
            hid = contained_match(s, BRUSH_INDEX, ('handle',))
            return {'kind': 'composite' if hid else 'knot_only',
                    'brush_id': None, 'handle_id': hid, 'knot_id': eid,
                    'series_id': None, 'specs_source': specs_source(s, e),
                    'method': method}
        if e['category'] == 'handle':
            kid = contained_match(s, BRUSH_INDEX, ('knot',))
            pe = BY_ID[kid] if kid else e
            return {'kind': 'composite' if kid else 'handle_only',
                    'brush_id': None, 'handle_id': eid, 'knot_id': kid,
                    'series_id': None, 'specs_source': specs_source(s, pe),
                    'method': method}
    # no full-string match: try part containment (composite / part-only)
    kid = contained_match(s, BRUSH_INDEX, ('knot',))
    hid = contained_match(s, BRUSH_INDEX, ('handle',))
    if kid and kid in SERIES_IDS:
        return {'kind': 'series', 'brush_id': None, 'handle_id': hid,
                'knot_id': None, 'series_id': kid,
                'specs_source': specs_source(s, BY_ID[kid]), 'method': 'contained'}
    if kid or hid:
        pe = BY_ID[kid] if kid else BY_ID[hid]
        return {'kind': 'composite' if (kid and hid) else ('knot_only' if kid else 'handle_only'),
                'brush_id': None, 'handle_id': hid, 'knot_id': kid,
                'series_id': None, 'specs_source': specs_source(s, pe),
                'method': 'contained'}
    return empty

def match_brush(s):
    """Three-tier brush resolution (P-13). Primary brush-parts resolution
    (tier-1) first; a clean 'unmatched' falls through to the tier-2 brush
    entries (attested/corroborated, all complete brushes), then to the
    unverified-tier brush entries. Every result carries its 'tier'."""
    r = _match_brush_primary(s)
    r['tier'] = 'tier-1' if r['kind'] != 'unmatched' else None
    if r['kind'] != 'unmatched' or not s: return r
    eid, method, amb = _match_with_index(s, BRUSH_MID_INDEX)
    if eid:
        return {'kind': 'complete', 'brush_id': eid, 'handle_id': None,
                'knot_id': None, 'series_id': None,
                'specs_source': specs_source(s, BY_ID[eid]),
                'method': 'tier-2', 'tier': 'tier-2'}
    if amb:
        out = dict(r); out['kind'] = 'ambiguous'; out['method'] = 'tier-2'
        out['tier'] = 'tier-2'
        out['ambiguous'] = amb
        return out
    eid, method, amb = _match_with_index(s, BRUSH_UV_INDEX)
    if eid:
        return {'kind': 'complete', 'brush_id': eid, 'handle_id': None,
                'knot_id': None, 'series_id': None,
                'specs_source': specs_source(s, BY_ID[eid]),
                'method': 'unverified', 'tier': 'unverified'}
    if amb:
        out = dict(r); out['kind'] = 'ambiguous'; out['method'] = 'unverified'
        out['tier'] = 'unverified'
        out['ambiguous'] = amb
        return out
    return r

# ---------------- run ----------------
CACHES = {f: {} for f in SIMPLE_FIELDS}
BRUSH_CACHE = {}

def _tier_outcomes(f, v):
    """Per-tier certain outcomes for `v` in precedence order, using
    match_field's labeling conventions: a list of result dicts (hit or
    ambiguity) or None per tier [tier-1, tier-2, unverified]. Each
    outcome also carries 'inner' (the raw _match_with_index method:
    exact/normalized/subset/subset-rev) so the caller can order by
    match strength; 'inner' is stripped before anything is cached or
    reported, so output labels are unchanged."""
    out = []
    for idx, label in ((INDEXES[f], 'tier-1'), (MID_INDEXES[f], 'tier-2'),
                       (UV_INDEXES[f], 'unverified')):
        eid, method, amb = _match_with_index(v, idx)
        m = method if label == 'tier-1' else label
        if eid: out.append({'id': eid, 'method': m, 'tier': label,
                            'inner': method})
        elif amb: out.append({'ambiguous': amb, 'method': m, 'tier': label,
                              'inner': method})
        else: out.append(None)
    return out

def _base_result(f, v):
    """Context-free (string-only) match result for a simple field,
    cached per string: {'id', 'method', 'tier'} | {'ambiguous', ...} |
    None."""
    if v not in CACHES[f]:
        outcomes = _tier_outcomes(f, v)
        # Strong-first selection (exact-across-tiers fix, 2026-10-28):
        # an exact/normalized claim at ANY tier beats a subset/
        # reverse-subset claim at a HIGHER tier -- but ONLY when the
        # strong claim is on a REAL (curated) entry. Clusters (ids
        # starting 'unverified/') are unprocessed harvest artifacts:
        # their verbatim strings must NOT outrank a higher-tier real
        # inference. The unrefined version of this rule (any strong
        # claim) was A/B'd the same day and REJECTED: 24,698 changed
        # resolutions, 23,359 of them demoting verified products to
        # their own clusters (e.g. verified Sea Spice Lime losing to
        # its cluster). Within a strength group, tier order still
        # decides, so same-method tier precedence (verified >
        # attested > unverified) is untouched. A strong ambiguity
        # counts only when every candidate is real.
        def _real_strong(r):
            if not r or r.get('inner') not in ('exact', 'normalized'):
                return False
            ids = [r['id']] if 'id' in r else (r.get('ambiguous') or [])
            return bool(ids) and all(
                not i.startswith('unverified/') for i in ids)
        base_idx = next((i for i, r in enumerate(outcomes)
                         if _real_strong(r)), None)
        if base_idx is None:
            base_idx = next((i for i, r in enumerate(outcomes) if r), None)
        base = outcomes[base_idx] if base_idx is not None else None
        eid = base.get('id') if base else None
        if eid and explicit_certain_id(v, f) == eid:
            # Explicit exact/normalized identification: certain, final.
            result = base
        else:
            # P-15: a declared loose alias governs its string over
            # subset/reverse-subset inference, ambiguities, and misses.
            # Only an explicit certain identification (handled above)
            # outranks it.
            loose = loose_match(v, LOOSE_INDEXES[f])
            if loose: result = loose
            elif eid and _bare_decisive(f, v, eid):
                # Bare-decisive capture: the winning hit rests solely
                # on a bare-brand record. A specific identification of
                # the same string at a lower tier outranks it (the
                # tier-1 subset pre-emption behind "Kai Captain
                # Sharpblade" landing on the DE Kai entry). A specific
                # lower-tier HIT outranks a lower-tier ambiguity (the
                # "Sapphoo Red" strings: a tier-2 Kai-cluster ambiguity
                # must not shadow the Sapphoo cluster's own record).
                # The rescue scans tiers BELOW the selected base (not
                # merely positions after the first outcome): a weak
                # higher-tier outcome the new selection already passed
                # over must not rescue against the strong base.
                better = None
                held_amb = None
                for r in outcomes[base_idx + 1:]:
                    if not r: continue
                    if 'id' in r:
                        if _bare_decisive(f, v, r['id']): continue
                        better = r
                        break
                    # An ambiguity counts only if at least one
                    # candidate identifies the string specifically;
                    # an ambiguity composed solely of bare-brand
                    # records (e.g. the two Kai clusters' {kai} tie)
                    # is the same bare capture wearing a tie.
                    if held_amb is None and any(
                            not _bare_decisive(f, v, c)
                            for c in r['ambiguous']):
                        held_amb = r
                result = better if better is not None else \
                    (held_amb if held_amb is not None else base)
            elif base: result = base
            else: result = None
        # Strip the selection-only 'inner' key: output schema unchanged.
        CACHES[f][v] = ({k: val for k, val in result.items()
                         if k != 'inner'} if result else None)
    return CACHES[f][v]

# ---------------- P-25: composite split ----------------
# A field string joining two or more products ("Alum block; B&M
# Paganini's Violin", "Snake Bite; Stirling Unscented Balm") splits at
# match time so each part matches its own entry; dataset rows are never
# modified and each matched part counts as one use of its product.
# Separator set + guard G0-G6 per
# catalog/multi_item_field_analysis_2026-11-16.md §5/§8 (user-approved
# revised design, 2026-11-16). Nothing splits in brush. A row failing
# any guard clause stays whole (safe miss) and keeps its ordinary
# whole-string result. Set SPLIT_ENABLED = False to disable splitting
# without an edit.
SPLIT_ENABLED = True

SPLIT_SEPARATORS = {
    # Per field, in try order: '|' and ';' are the cleanest joins (rarely
    # inside a product name); ' / ' and ' + ' occur inside brand/product
    # names (Barrister + Mann, Tallow + Steel, collab 'A / B'); ' then '
    # last. A value is split on ONE separator at a time -- splitting on
    # all of them at once would cut brand names apart ('Barrister + Mann
    # ... | ...' split on '+' yields the non-product part 'Barrister').
    # Among separators that pass the guard, the split with the most
    # resolved parts wins, then the strongest weakest method.
    'razor': [r'\|', r';', r'\s+then\s+'],
    'blade': [r'\|', r';', r'\s/\s', r'\s\+\s', r'\s+then\s+'],
    'soap': [r'\s/\s', r'\s\+\s'],
    'aftershave': [r'\|', r';', r'\s/\s', r'\s\+\s'],
    'fragrance': [r';', r'\s\+\s'],
}

_MD_LINK_RE = re.compile(r'\[([^\]]*)\]\([^)]*\)')
_URL_RE = re.compile(r'https?://\S+')
_STRIKE_RE = re.compile(r'~~.*?~~')

def _p25_preprocess(s):
    """Guard preprocessing, before any splitting: HTML-unescape, strip
    ~~strikethrough~~ segments (a retraction, not a product), reduce
    markdown links to their text, strip bare URLs (they carry / and //)."""
    if not s: return ''
    s = html.unescape(s)
    s = _STRIKE_RE.sub(' ', s)
    s = _MD_LINK_RE.sub(r'\1', s)
    s = _URL_RE.sub(' ', s)
    return re.sub(r'\s+', ' ', s).strip()

# G0b: trailing format words posters append from trythatsoap link text.
_G0B_FORMAT_WORDS = ('aftershave splash', 'aftershave balm', 'shaving soap',
                     'eau de toilette', 'eau de parfum', 'eau de cologne',
                     'shave soap', 'shaving cream', 'post shave',
                     'aftershave', 'soap', 'splash', 'balm', 'cologne',
                     'edt', 'edp', 'edc', 'cream', 'lotion', 'tonic',
                     'serum', 'oil', 'gel', 'milk', 'fragrance', 'parfum',
                     'perfume', 'toner')
_G0B_RE = re.compile(
    r'\s+-\s+(' + '|'.join(sorted(_G0B_FORMAT_WORDS, key=len, reverse=True)) +
    r')\s*$', re.IGNORECASE)

_P25_G0_CACHE = {}

def _p25_whole_is_product(f, s):
    """G0/G0b: the unsplit value exact- or normalized-matches a tier-1
    or tier-2 entry (hit or ambiguity), as-is or with a trailing format
    word stripped. True -> do not split."""
    key = (f, s)
    if key in _P25_G0_CACHE: return _P25_G0_CACHE[key]
    hit = False
    for cand in (s, _G0B_RE.sub('', s).strip()):
        if not cand: continue
        outcomes = _tier_outcomes(f, cand)
        for out in outcomes[:2]:
            if out and out.get('inner') in ('exact', 'normalized'):
                hit = True
                break
        if hit: break
    _P25_G0_CACHE[key] = hit
    return hit

# G5 routine-phrase junk (dropped, not counted as products) and G6
# additive junk. Normalized comparison; bare sizes (6/8) are junk too
# (a size fragment, never a product on its own).
_P25_JUNK = {
    'cold water rinse', 'cold water splash', 'cold rinse', 'cold water',
    'warm water rinse', 'hot water rinse', 'water rinse', 'rinse',
    'leftover lather', 'extra lather',
    'first pass', 'second pass', 'third pass', 'fourth pass',
    'touchup', 'touch up', 'cleanup', 'clean up',
    'pass 1', 'pass 2', 'pass 3', 'pass 4',
}
_P25_SIZE_RE = re.compile(r'^\d+/\d+$')
_P25_ADDITIVE_RE = re.compile(r'frost drops?|terrorade', re.IGNORECASE)

def _p25_is_junk(part):
    if not part: return True
    if _P25_ADDITIVE_RE.search(part): return True
    if _P25_SIZE_RE.match(part.strip()): return True
    return N(part) in _P25_JUNK

_P25_PART_CACHE = {}

def _p25_rev_via_composite(f, eid, var):
    """True when a part's subset-rev resolution on `eid` rests on a
    composite alias: the smallest alias/canonical key of the entry
    containing the part's tokens itself carries a separator. Composite
    aliases are harvested whole field strings (analysis §9); a part's
    tokens sitting inside one is not evidence the part IS that product
    (e.g. 'PAA - Tea Party 508 balm' reverse-matches the Spearhead
    Heather entry through its harvested alias 'Spearhead - Heather AS;
    PAA - Tea Party 508 balm'). Comma is NOT in the list: it is a
    legitimate product-name character ('Stirling - I, Rich Moose')."""
    toks = T(var)
    if not toks: return False
    e = BY_ID[eid]
    cands = list(e.get('aliases') or ())
    if e.get('brand') and e.get('product'):
        cands.append(f"{e['brand']} {e['product']}")
    best = None
    for a in cands:
        ta = T(a)
        if toks <= ta:
            if best is None or len(ta) < len(T(best)):
                best = a
    if best is None: return False
    return any(s in best for s in (';', '|', ' + ', ' / ', ' then '))

def _p25_resolve_part(f, part):
    """Resolve one split part through the tier-1/2 walk (match_field
    semantics: a tier-1 hit-or-ambiguity is final, else tier-2; no loose
    aliases, no P-14). Tries the part as-is, then with trailing
    parenthetical groups removed, then truncated at the first ' ('.
    Returns {'id','method','tier'} or None. G3: a part whose winning
    resolution is reverse-subset only needs >=3 tokens."""
    key = (f, part)
    if key in _P25_PART_CACHE: return _P25_PART_CACHE[key]
    result = None
    p = part.strip()
    variants = [p]
    no_paren = re.sub(r'\s*\([^)]*\)\s*$', '', p).strip()
    if no_paren and no_paren != p: variants.append(no_paren)
    trunc = p.split(' (', 1)[0].strip()
    if trunc and trunc != p and trunc not in variants: variants.append(trunc)
    for var in variants:
        for idx, label in ((INDEXES[f], 'tier-1'), (MID_INDEXES[f], 'tier-2')):
            eid, method, amb = _match_with_index(var, idx)
            if eid:
                if method == 'subset-rev' and (
                        len(T(var)) < 3 or _p25_rev_via_composite(f, eid, var)):
                    # G3 token floor, or the rev hit rests on a
                    # composite alias (§9): try the next variant.
                    break
                result = {'id': eid, 'method': method, 'tier': label}
                break
            if amb:
                break  # ambiguity at this tier is final for this variant
        if result: break
    _P25_PART_CACHE[key] = result
    return result

def _p25_try_split(f, v, whole):
    """P-25 composite split for field `f`, value `v`. `whole` is the
    whole-string result already computed (or None). Returns a split
    result {'split': [{'id','method','tier','part'}, ...],
    'method': 'composite-split', 'tier': best part tier} or None.
    Guard G0-G6 in order; any failure leaves the string whole."""
    if not SPLIT_ENABLED or f not in SPLIT_SEPARATORS or not v:
        return None
    if whole and whole.get('method') in ('loose-alias', 'author-scoped'):
        return None  # whole string already identified as one product
    pv = _p25_preprocess(v)
    if _p25_whole_is_product(f, pv):  # G0/G0b
        return None
    # Try one separator at a time (a separator inside a brand name must
    # not cut the string -- see SPLIT_SEPARATORS). Among the separators
    # that pass the guard, prefer the most resolved parts, then the
    # strongest weakest method, then try order.
    strength = {'exact': 4, 'normalized': 3, 'subset': 2, 'subset-rev': 1}
    best = None
    for sep_pat in SPLIT_SEPARATORS[f]:
        if not re.search(sep_pat, pv, re.IGNORECASE):
            continue
        parts = [p.strip() for p in re.split(sep_pat, pv, flags=re.IGNORECASE)]
        parts = [p for p in parts if p]
        if len(parts) < 2:
            continue
        resolved = []
        ok = True
        for part in parts:
            if _p25_is_junk(part):  # G5/G6: dropped, not a product
                continue
            if len(part) > 80:  # G4: prose cap
                ok = False
                break
            r = _p25_resolve_part(f, part)  # G1 + G3
            if not r:
                ok = False
                break
            r = dict(r)
            r['part'] = part
            resolved.append(r)
        if not ok or len(resolved) < 2:
            continue
        ids = [r['id'] for r in resolved]
        if len(set(ids)) != len(ids):  # G2: all entries distinct
            continue
        rank = (len(resolved),
                min(strength[r['method']] for r in resolved))
        if best is None or rank > best[0]:
            tier = 'tier-1' if any(r['tier'] == 'tier-1' for r in resolved) \
                else 'tier-2'
            best = (rank, {'split': resolved, 'method': 'composite-split',
                           'tier': tier})
    return best[1] if best else None

# ---------------- Comma carve-out (variant (e)) ----------------
# Comma-joined field strings split under the strict discipline of
# catalog/comma_carveout_scoping_2026-11-17.md, run 4 (user-approved
# 2026-11-17): parts resolve via exact/normalized ONLY, plus two narrow
# exemptions -- the alum fallback (O2, P-24-compliant) and the weak-only
# P5 paren rule. Fields: aftershave, blade, razor, fragrance. SOAP IS
# HELD (needs a descriptor guard first). The P-25 path is untouched: the
# carve-out runs only when _p25_try_split returns None (incremental rows
# only), and the alum fallback is NOT ported into the P-25 path (Q006734
# is a separate follow-on). Set COMMA_SPLIT_ENABLED = False to disable
# the carve-out without an edit; SPLIT_ENABLED = False disables all
# splitting. Ported from catalog/work/comma_carveout_harness.py run-4
# semantics (resolve_variant / resolve_part / comma_split); names are
# _comma_-prefixed so the two split paths never share state.
COMMA_SPLIT_ENABLED = True
COMMA_FIELDS = {'aftershave', 'blade', 'razor', 'fragrance'}
_COMMA_ALLOWED = {'exact', 'normalized'}
_GENERIC_ALUM = 'unverified/aftershave/alum'
_COMMA_PART_CACHE = {}

def _comma_split_comma(s):
    """Split on commas at paren depth 0 only (a comma inside '(Green
    Tea, Oatmeal)' never splits)."""
    parts, cur, depth = [], [], 0
    for ch in s:
        if ch == '(':
            depth += 1
            cur.append(ch)
        elif ch == ')':
            depth = max(0, depth - 1)
            cur.append(ch)
        elif ch == ',' and depth == 0:
            parts.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    parts.append(''.join(cur).strip())
    return [p for p in parts if p]

def _comma_part_variants(p):
    """Part variants in order: as-is, paren-stripped (trailing group
    only), truncated at the first ' ('."""
    p = p.strip()
    vs = [p]
    no_paren = re.sub(r'\s*\([^)]*\)\s*$', '', p).strip()
    if no_paren and no_paren != p:
        vs.append(no_paren)
    trunc = p.split(' (', 1)[0].strip()
    if trunc and trunc != p and trunc not in vs:
        vs.append(trunc)
    return vs

def _comma_is_alum_block_entry(eid):
    e = BY_ID.get(eid) or {}
    return 'alum' in (e.get('product') or '').lower()

def _comma_paren_tokens(part):
    """Tokens appearing only inside (...) in the part."""
    inside = ' '.join(re.findall(r'\(([^)]*)\)', part))
    outside = re.sub(r'\([^)]*\)', ' ', part)
    ti, to = set(T(inside)), set(T(outside))
    return ti - to

def _comma_match_depends_on_parens(f, eid, var, part):
    """True when the entry's matching witness uses a token that appears
    in the part only inside a parenthetical."""
    e = BY_ID.get(eid)
    if not e:
        return False
    cands = list(e.get('aliases') or ())
    if e.get('brand') and e.get('product'):
        cands.append(f"{e['brand']} {e['product']}")
    tv, pt = set(T(var)), _comma_paren_tokens(part)
    if not pt:
        return False
    best = None
    for a in cands:
        ta = set(T(a))
        if ta <= tv or tv <= ta:  # subset or subset-rev witness
            if best is None or len(ta) < len(best):
                best = ta
    if best is None:
        return False
    return bool(best & pt)

def _comma_strip_exempt(r):
    if r is None:
        return None
    r = dict(r)
    r.pop('exempt', None)
    return r

def _comma_resolve_variant(f, var, allowed, alum_fallback,
                           exempt_fallback=False):
    """Resolve one variant string through the tier-1/2 walk. Returns the
    raw {'id','method','tier'} or None; NO method filtering here (the
    caller applies the variant's allowed set). Mirrors _p25_resolve_part
    otherwise: G3 floor + rev-via-composite rejection, tier-1 ambiguity
    final (unless the alum fallback applies). The alum fallback fires
    when the tier-2 method is in `allowed` or exempt_fallback is set;
    its result carries 'exempt': True so the caller can let it through
    the method filter (justified by the P-24 rule, not by match
    strength)."""
    for idx, label in ((INDEXES[f], 'tier-1'), (MID_INDEXES[f], 'tier-2')):
        eid, method, amb = _match_with_index(var, idx)
        if eid:
            if method == 'subset-rev' and (
                    len(T(var)) < 3 or _p25_rev_via_composite(f, eid, var)):
                return None  # G3: try next variant (caller handles)
            return {'id': eid, 'method': method, 'tier': label}
        if amb:
            if label == 'tier-1' and alum_fallback:
                if all(_comma_is_alum_block_entry(a) for a in amb) \
                        and 'alum' in T(var):
                    eid2, m2, amb2 = _match_with_index(var, MID_INDEXES[f])
                    if eid2 == _GENERIC_ALUM and (m2 in allowed or exempt_fallback):
                        return {'id': eid2, 'method': m2, 'tier': 'tier-2',
                                'exempt': True}
            return None  # ambiguity final for this variant
    return None

def _comma_resolve_part(f, part):
    """Resolve one split part under variant (e): allowed =
    {exact, normalized}, alum fallback on, weak-only P5 paren rule on,
    both exemptions let through the method filter. P5 is weak-only: it
    overrides the as-is resolution only when that resolution is
    subset/subset-rev (a strong as-is hit is never overridden).
    exempt_paren applies ONLY to the P5 override return below -- never
    to the stripped fallback after it (run-4 fix; the run-3 leak let any
    paren-bearing part whose stripped form resolved by a disallowed
    method through, e.g. 'Gillette Silver Blue (N)' in the razor field
    resolving subset-rev to Tatara Masamune via a composite alias).
    A variant resolving via a disallowed method is skipped and the next
    variant tried; results carrying 'exempt' (the alum fallback) pass
    the method filter."""
    key = (f, part)
    if key in _COMMA_PART_CACHE: return _COMMA_PART_CACHE[key]
    result = None
    vs = _comma_part_variants(part)
    if len(vs) > 1:
        r0 = _comma_resolve_variant(f, vs[0], _COMMA_ALLOWED, True, True)
        r1 = None
        for v in vs[1:]:
            r1 = _comma_resolve_variant(f, v, _COMMA_ALLOWED, True, True)
            if r1:
                break
        if (r0 and r1 and r0['id'] != r1['id']
                and r0['method'] in ('subset', 'subset-rev')
                and _comma_match_depends_on_parens(f, r0['id'], vs[0], part)):
            # P5 override fires: the stripped resolution wins. Under
            # (e) exempt_paren is True, so the override returns r1
            # even when its method is outside `allowed` (justified by
            # the paren analysis, not by match strength).
            result = _comma_strip_exempt(r1)
            _COMMA_PART_CACHE[key] = result
            return result
        if r0 and (r0['method'] in _COMMA_ALLOWED or r0.get('exempt')):
            result = _comma_strip_exempt(r0)
        elif r1 and (r1['method'] in _COMMA_ALLOWED or r1.get('exempt')):
            result = _comma_strip_exempt(r1)
        _COMMA_PART_CACHE[key] = result
        return result
    for v in vs:
        r = _comma_resolve_variant(f, v, _COMMA_ALLOWED, True, True)
        if r and (r['method'] in _COMMA_ALLOWED or r.get('exempt')):
            result = _comma_strip_exempt(r)
            break
    _COMMA_PART_CACHE[key] = result
    return result

def _comma_try_split(f, v, whole):
    """Comma carve-out (variant (e), user-approved 2026-11-17): a field
    string joining two or more products with paren-aware commas splits
    so each part matches its own entry. Runs only when the P-25 split
    did not fire (incremental rows only). Parts resolve via
    exact/normalized ONLY, plus the alum fallback (O2) and the weak-only
    P5 paren rule (both exempt from the method filter). Soap is held.
    A part matching nothing keeps the string whole (safe miss). Output
    schema is the same as P-25."""
    if not SPLIT_ENABLED or not COMMA_SPLIT_ENABLED or f not in COMMA_FIELDS or not v:
        return None
    if whole and whole.get('method') in ('loose-alias', 'author-scoped'):
        return None  # whole string already identified as one product
    pv = _p25_preprocess(v)
    if _p25_whole_is_product(f, pv):  # G0/G0b
        return None
    parts = _comma_split_comma(pv)
    if len(parts) < 2:
        return None
    resolved = []
    for part in parts:
        if _p25_is_junk(part):  # G5/G6: dropped, not a product
            continue
        if len(part) > 80:  # G4: prose cap
            return None
        r = _comma_resolve_part(f, part)  # G1 + G3
        if not r:
            return None
        r = dict(r)
        r['part'] = part
        resolved.append(r)
    if len(resolved) < 2:
        return None
    ids = [r['id'] for r in resolved]
    if len(set(ids)) != len(ids):  # G2: all entries distinct
        return None
    tier = 'tier-1' if any(r['tier'] == 'tier-1' for r in resolved) else 'tier-2'
    return {'split': resolved, 'method': 'composite-split', 'tier': tier}

def build_derived_razor_formats(years):
    """Phase 0 for P-14: derive each razor entry's blade format from
    this run's unambiguous pairings with specific (non-bare) blade
    strings. A razor entry earns a format with >=3 tally posts and
    >=90% purity. Populates DERIVED_RAZOR_FORMAT."""
    tally = defaultdict(Counter)
    for year in years:
        try:
            data = json.load(open(f'{SOTD}sotd_{year}_full.json'))
        except FileNotFoundError:
            continue
        for e in data:
            rv, bv = e.get('razor'), e.get('blade')
            if not rv or not bv: continue
            rb = _base_result('razor', rv)
            bb = _base_result('blade', bv)
            if not rb or 'id' not in rb or not bb or 'id' not in bb: continue
            if bb.get('probabilistic'): continue  # P-15 picks are not format evidence
            if bare_brand_key(bv): continue
            be = BY_ID[bb['id']]
            if (be.get('product') or '') == 'Unspecified': continue
            f = entry_format(be)
            if f: tally[rb['id']][f] += 1
    DERIVED_RAZOR_FORMAT.clear()
    for rid, c in tally.items():
        top, n = c.most_common(1)[0]
        tot = sum(c.values())
        if n >= 3 and tot >= 3 and n >= 0.9 * tot:
            DERIVED_RAZOR_FORMAT[rid] = top
    print(f'derived razor formats: {len(DERIVED_RAZOR_FORMAT)} razor entries')

def run_year(year):
    data = json.load(open(f'{SOTD}sotd_{year}_full.json'))
    stats = {}
    p14_counter = {'blade': 0, 'razor': 0}
    ffilter_counter = {'blade': 0, 'razor': 0}
    for e in data:
        m = {}
        # P-14: contextual blade/razor resolution for this post.
        finals = {}
        if e.get('blade') or e.get('razor'):
            rb = _base_result('razor', e['razor']) if e.get('razor') else None
            bb = _base_result('blade', e['blade']) if e.get('blade') else None
            r_fmt = _result_format(rb, 'razor')
            # A P-15 loose blade pick is probabilistic; do not use it as
            # a format signal for resolving the paired razor.
            b_fmt = None if (bb and bb.get('probabilistic')) else \
                _result_format(bb, 'blade')
            bf = _p14_blade(e.get('blade'), bb, r_fmt, p14_counter) \
                if e.get('blade') else None
            # Hard P-14 constraint: void a default blade hit that
            # resolves against the razor's format (fallback chain
            # inside). The blade format signal for the razor pass is
            # then taken from the filtered result.
            bf = _format_filter('blade', e.get('blade'), bf, r_fmt,
                                ffilter_counter)
            b_fmt = _result_format(bf, 'blade')
            rf = _p14_razor(e.get('razor'), rb, b_fmt, p14_counter) \
                if e.get('razor') else None
            # Symmetrically, void a default razor hit that resolves
            # against the (filtered) blade format.
            rf = _format_filter('razor', e.get('razor'), rf, b_fmt,
                                ffilter_counter)
            finals = {'blade': bf, 'razor': rf}
        for f in SIMPLE_FIELDS:
            v = e.get(f)
            st = stats.setdefault(f, {'fields': 0, 'matched': 0, 'ambiguous': 0,
                                      'matched_t1': 0, 'matched_t2': 0,
                                      'matched_uv': 0, 'matched_loose': 0,
                                      'split_rows': 0, 'split_parts': 0,
                                      'unmatched': Counter()})
            if v:
                st['fields'] += 1
                r = finals[f] if f in finals else _base_result(f, v)
                # §B4: author-scoped aliases apply per post, after the
                # string-only and P-14 contextual passes, and only to an
                # ambiguous/missed result (checked inside).
                scoped = author_scoped_match(f, v, e.get('author'), r)
                if scoped: r = scoped
                # P-25: composite split -- a field string joining two or
                # more products splits so each part matches its own
                # entry. Failing any guard clause leaves the
                # whole-string result untouched.
                split = _p25_try_split(f, v, r)
                if not split:
                    # Comma carve-out (variant (e), 2026-11-17): paren-
                    # aware comma splits, strict exact/normalized-only
                    # part resolution + alum fallback + weak-only P5.
                    # Runs only when P-25 did not fire (incremental
                    # rows only); soap is held.
                    split = _comma_try_split(f, v, r)
                if split: r = split
                if r and 'split' in r:
                    # A split row counts once in coverage (best part
                    # tier); each part is one use of its product in
                    # the stored match. Split rows/parts are tallied
                    # separately below.
                    st['matched'] += 1
                    if r['tier'] == 'tier-2':
                        st['matched_t2'] += 1
                    else:
                        st['matched_t1'] += 1
                    st['split_rows'] += 1
                    st['split_parts'] += len(r['split'])
                elif r and 'id' in r:
                    st['matched'] += 1
                    if r.get('probabilistic') or r.get('method') == 'loose-alias':
                        # P-15: resolved, but probable -- its own sub-line,
                        # never folded into the certain tier counts.
                        st['matched_loose'] += 1
                    elif r.get('tier') == 'tier-2':
                        st['matched_t2'] += 1
                    elif r.get('tier') == 'unverified':
                        st['matched_uv'] += 1
                    else:
                        st['matched_t1'] += 1
                elif r and 'ambiguous' in r: st['ambiguous'] += 1
                else: st['unmatched'][v] += 1
                m[f] = r
            else:
                m[f] = None
        v = e.get('brush')
        st = stats.setdefault('brush', {'fields': 0, 'matched': 0, 'ambiguous': 0,
                                        'matched_t1': 0, 'matched_t2': 0,
                                        'matched_uv': 0, 'matched_loose': 0,
                                        'unmatched': Counter(), 'kinds': Counter()})
        if v:
            st['fields'] += 1
            if v not in BRUSH_CACHE: BRUSH_CACHE[v] = match_brush(v)
            r = BRUSH_CACHE[v]
            st['kinds'][r['kind']] += 1
            if r['kind'] == 'ambiguous': st['ambiguous'] += 1
            elif r['kind'] == 'unmatched': st['unmatched'][v] += 1
            else:
                st['matched'] += 1
                if r.get('tier') == 'tier-2':
                    st['matched_t2'] += 1
                elif r.get('tier') == 'unverified':
                    st['matched_uv'] += 1
                else:
                    st['matched_t1'] += 1
            m['brush'] = r
        else:
            m['brush'] = None
        e['matches'] = m
    for f in ('blade', 'razor'):
        st = stats.setdefault(f, {'fields': 0, 'matched': 0, 'ambiguous': 0,
                                  'matched_t1': 0, 'matched_t2': 0,
                                  'matched_uv': 0, 'matched_loose': 0,
                                  'unmatched': Counter()})
        st['p14'] = p14_counter[f]
        st['ffilter'] = ffilter_counter[f]
    with open(f'{SOTD}matched_{year}.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    return stats

def main():
    years = [int(x) for x in sys.argv[1:]] or [2026, 2025, 2024, 2022]
    build_derived_razor_formats(years)
    all_stats = {}
    for y in years:
        all_stats[y] = run_year(y)
        print('done', y)
    n_uv = sum(1 for e in merged if e.get('status') == 'unverified')
    n_mid = sum(1 for e in merged if e.get('status') in MID_STATUSES)
    lines = ['# Coverage report — central merge matcher (match_all.py)',
             f'Catalog: catalog_merged/ shards ({len(merged)} entries, of which {n_mid} tier-2 '
             f'(attested/corroborated) and {n_uv} unverified-tier). '
             'Match order: exact alias -> normalized -> token-subset -> reverse-subset; ambiguous never forced.',
             'Three tiers (P-13): tier-1 = matched to a verified or needs-review entry; tier-2 = matched to an '
             'attested or corroborated entry (match_method "tier-2"); unverified = matched to an '
             'unverified-tier entry (match_method "unverified"); addressable = tier-1 + tier-2 + unverified + probable. '
             'Resolution precedence is tier-1 > tier-2 > unverified, and every stored match records its tier. '
             'Probable (P-15): a declared loose alias governs its string unless an explicit exact/normalized '
             'certain alias uniquely identifies it; subset inference, ambiguities, and misses all yield to it. '
             'Its stored match has method "loose-alias", probabilistic=true, and the alias basis_share. '
             'Author-scoped (§B4): a declared author_scoped_alias resolves an ambiguous/missed string for '
             'that one author only, on documentary proof (method "author-scoped"); it counts in its certain tier. '
             'Probable counts form their own sub-line and are included in addressable, but never in certain tier-1/tier-2/unverified counts. '
             'Format agreement (P-14): cross-format blade/razor ambiguities and bare multi-format brand strings '
             'are decided by the paired razor/blade format in the same post (method suffix "+razor-format" / '
             '"+blade-format", or method "razor-format" for bare-brand picks). '
             'Hard constraint (P-14): no default (popularity, P-15 loose, bare-brand, or bare-decisive subset '
             'capture) resolves a blade against the paired razor\'s format, or a razor against the paired blade\'s '
             'format; voided defaults fall back to a format-scoped loose alias, the certain match within the '
             'format, a brand-pool ambiguity in the format, or unresolved. '
             'Still-unmatched strings are documented non-products/parser artifacts and parked candidate-alias clusters.',
             'Brush kinds: complete / composite / knot_only / handle_only / series all count as matched. '
             'P-25 composite splits: a field string joining two or more products (per-field separators; guard G0-G6) '
             'splits at match time so each part matches its own entry; each part counts as one use of its product. '
             'Split rows count once in the coverage table (best part tier); the per-year P-25 line gives rows split '
             'and part attributions.', '']
    tot = {}
    for y in years:
        lines.append(f'## {y}')
        lines.append('| category | fields | tier-1 | tier-2 | unverified | probable | ambiguous | unmatched | % tier-1 | % tier-2 | % probable | % addressable |')
        lines.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
        for f in ['blade', 'razor', 'soap', 'aftershave', 'fragrance', 'brush']:
            st = all_stats[y][f]
            p1 = 100.0 * st['matched_t1'] / st['fields'] if st['fields'] else 0
            p2 = 100.0 * st['matched_t2'] / st['fields'] if st['fields'] else 0
            pp = 100.0 * st['matched_loose'] / st['fields'] if st['fields'] else 0
            pa = 100.0 * st['matched'] / st['fields'] if st['fields'] else 0
            lines.append(f"| {f} | {st['fields']} | {st['matched_t1']} | {st['matched_t2']} | {st['matched_uv']} | {st['matched_loose']} | {st['ambiguous']} | "
                         f"{sum(st['unmatched'].values())} | {p1:.1f}% | {p2:.1f}% | {pp:.1f}% | {pa:.1f}% |")
            t = tot.setdefault(f, {'fields': 0, 'matched': 0, 'matched_t1': 0,
                                   'matched_t2': 0, 'matched_loose': 0,
                                   'matched_uv': 0, 'ambiguous': 0, 'unmatched': 0,
                                   'split_rows': 0, 'split_parts': 0})
            t['fields'] += st['fields']; t['matched'] += st['matched']
            t['matched_t1'] += st['matched_t1']; t['matched_t2'] += st['matched_t2']
            t['matched_uv'] += st['matched_uv']; t['matched_loose'] += st['matched_loose']
            t['ambiguous'] += st['ambiguous']; t['unmatched'] += sum(st['unmatched'].values())
            t['split_rows'] += st.get('split_rows', 0); t['split_parts'] += st.get('split_parts', 0)
        bk = all_stats[y]['brush'].get('kinds', {})
        if bk:
            lines.append('')
            lines.append('Brush kinds: ' + ', '.join(f'{k} {v}' for k, v in sorted(bk.items())))
        p14b = all_stats[y]['blade'].get('p14', 0)
        p14r = all_stats[y]['razor'].get('p14', 0)
        if p14b or p14r:
            lines.append(f'P-14 format-agreement resolutions: blade {p14b} (decided by razor format), razor {p14r} (decided by blade format).')
        ffb = all_stats[y]['blade'].get('ffilter', 0)
        ffr = all_stats[y]['razor'].get('ffilter', 0)
        if ffb or ffr:
            lines.append(f'P-14 hard filter: defaults voided by the paired format — blade {ffb}, razor {ffr} (fallback: scoped loose alias, certain match within format, brand-pool ambiguity, unresolved).')
        srows = {f: (all_stats[y][f].get('split_rows', 0), all_stats[y][f].get('split_parts', 0))
                 for f in ['blade', 'razor', 'soap', 'aftershave', 'fragrance']}
        if any(n for n, _p in srows.values()):
            lines.append('P-25 composite splits (rows split / part attributions): ' +
                         ', '.join(f'{f} {n}/{p}' for f, (n, p) in srows.items() if n) + '.')
        lines.append('')
    lines.append('## All years combined')
    lines.append('| category | fields | tier-1 | tier-2 | unverified | probable | ambiguous | unmatched | % tier-1 | % tier-2 | % probable | % addressable |')
    lines.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for f in ['blade', 'razor', 'soap', 'aftershave', 'fragrance', 'brush']:
        t = tot[f]
        p1 = 100.0 * t['matched_t1'] / t['fields'] if t['fields'] else 0
        p2 = 100.0 * t['matched_t2'] / t['fields'] if t['fields'] else 0
        pp = 100.0 * t['matched_loose'] / t['fields'] if t['fields'] else 0
        pa = 100.0 * t['matched'] / t['fields'] if t['fields'] else 0
        lines.append(f"| {f} | {t['fields']} | {t['matched_t1']} | {t['matched_t2']} | {t['matched_uv']} | {t['matched_loose']} | {t['ambiguous']} | {t['unmatched']} | {p1:.1f}% | {p2:.1f}% | {pp:.1f}% | {pa:.1f}% |")
    if any(tot[f].get('split_rows', 0) for f in tot):
        lines.append('P-25 composite splits, all years (rows split / part attributions): ' +
                     ', '.join(f"{f} {tot[f]['split_rows']}/{tot[f]['split_parts']}"
                               for f in ['blade', 'razor', 'soap', 'aftershave', 'fragrance']
                               if tot[f].get('split_rows', 0)) + '.')
    lines.append('')
    for y in years:
        for f in ['blade', 'razor', 'soap', 'aftershave', 'fragrance', 'brush']:
            st = all_stats[y][f]
            lines.append(f'## Top unmatched — {y} {f}')
            for s, n in st['unmatched'].most_common(20):
                lines.append(f'- ({n}) {s}')
            lines.append('')
    with open(CAT + 'coverage_report.md', 'w') as f:
        f.write('\n'.join(lines))
    print('wrote coverage_report.md')

if __name__ == '__main__':
    main()
