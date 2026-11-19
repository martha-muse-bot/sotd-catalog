# How SOTD posters write brush strings: handle vs knot

**Date:** 2026-11-18
**Analyst:** subagent (read-only analysis for the handle-guard design)
**Dataset:** `~/workspace/sotd/sotd_*_full.json`, 11 files, **241,408 rows**
scanned (2016–2026). Brush field only.
**Catalog:** `catalog/catalog_merged/*.json` as loaded by `match_all.py`
(the matcher's own source of truth). No files, database, or precedents
were modified. Census script:
`~/workspace/scratch/handle_guard/census.py` (+ `enumerate.py`).

## 0. Headline findings

- **The 49-row class has a clean separator.** In 48 of the 49
  certain-but-wrong Hybrid rows, "Dogwood" and "Hybrid" sit in
  **different segments** of the string, split by `/`, `w/` or `with` —
  the handle is named in one segment, the knot (a Briar/badger-boar
  hybrid) in another. A segment rule (H1) voids 48/49 and keeps
  **596/596** correct dogwood-attached rows and **all 108** non-Hybrid
  gains (Acrylic 92, Sandy Pearl 15, Sky Blue 1).
- **One row has no separator and needs a second rule.** `Dogwood
  Handcrafts Briar Brushworks Badger Boar Hybrid 26mm` names the
  handle and the knot in a single unseparated run; the token-adjacency
  rule (H2 — a knot noun between the handle alias's tokens) catches
  it, and only it.
- **The 52 "unclear" rows split cleanly under the same two rules,
  and the split matches a hand reading of every distinct string.**
  The 24 the segment rule keeps (9 distinct strings) are all
  handle-attached — colorway/drop + Hybrid in the handle segment
  (Malachor, Valley of Ashes, Purple, Ossus, Seascape, "Hybrid B3").
  The 28 it voids (7 distinct strings) are all knot-attached
  (Briar Brushworks Hybrid, DG B14/B7 Hybrid knots, SilkSmoke
  Flat Top Hybrid). No hand-read row contradicts the rules.
- **"Hybrid" is a knot word first, a handle model second.** 2,003
  brush rows contain "hybrid" (all years). Only the Dogwood Hybrid
  is a handle model; everywhere else "hybrid" describes a knot
  (badger/boar hybrid, FlatTop/Fan hybrid, Nexus/Tribble hybrid
  synthetics, bulb/fan hybrid shapes). Any rule that treats "Hybrid"
  as a free-floating token will mis-attach it to the handle.
- **Predicted guard yield: 728 of 805 gains kept (90.4%), 77 voided,
  0 certain-but-wrong left in the 49-row class.** The voided rows
  return to exactly their pre-handle outcomes (verified in the A/B,
  not assumed — the guard only ever removes handle entries from the
  candidate set, so a voided row's selection is the pre-handle
  selection by construction).
- **Bare-brand handles stay unresolved by design.** "Dogwood handle"
  (94 rows) and "Maggard handle" (918 rows, A/B years) name a brand,
  not a model. They mostly already resolve to something — a complete
  brush or a knot — with the handle half unattributed. A brand-level
  handle entry would be a catalog decision, not a matcher fix, and
  P-26 as written does not authorize it. See §5.

## 1. Method

### 1.1 Census

`census.py`: for every row and brush string, test structure predicates
(separators, "handle"/"knot"/"hybrid"/"briar", size tokens, knot
descriptor words); classify every "hybrid" row with the tradeoff
script's regexes (dogwood-attached / knot-attached / unclear); then
simulate the segment rule on the 805 handle-gain rows from the
builder's A/B (`~/workspace/scratch/handle_ab/pre|post`), using the
matcher's own normalization `N()` per segment and the live handle
aliases from `catalog/catalog_merged/handle.json`.

Definitions (the exact predicates matter):

- **Segment:** the raw string split on `/`, ` with `, ` w/ `, ` in `,
  ` + `, ` | `, ` then `. `" - "` is deliberately NOT a separator
  (it is used inside handle names: "Dogwood Handcrafts - Malachor
  Hybrid"); comma is deliberately NOT one (annotation/scent-list
  trap). `w/` is matched before bare `/` so "w/20mm" is a `w/` join,
  not a `/` join.
- **Segment-satisfiable (H1):** every token of the handle alias lies
  in a single segment's token set (each segment normalized with the
  matcher's `N()`).
- **Knot noun (H2):** one of {briar, badger, boar, knot}. The minimal
  set the data actually needs; see §3.3 for why it is not larger.

### 1.2 Hand classification

All 9 distinct seg-ok unclear strings and all 7 distinct seg-SPLIT
unclear strings were read individually (§4). The single seg-ok
knot-attached row was read individually (§3.2).

## 2. Census: how posters write brush strings

219,464 non-empty brush strings; 36,747 distinct.

| structure | rows |
|---|---|
| contains a size (`Nmm`) | 113,514 |
| contains a knot descriptor word (shd/fan/bulb/silvertip/badger/boar/…) | 105,181 |
| contains `/` | 34,136 |
| contains `w/` | 14,739 |
| contains `knot` | 12,276 |
| contains `handle` | 11,206 |
| contains ` with ` | 8,123 |
| contains ` in ` | 2,938 |
| contains `hybrid` | 2,003 |
| contains `\|` | 1,699 |
| contains ` + ` | 1,354 |
| contains `briar` | 288 |

### 2.1 The `/` join

Of 34,136 `/` rows (note: this count includes the `/` inside `w/`):

- 8,645 handle-brand left + knot-word right — the classic
  composite shape (`Dogwood/Briar Hybrid`, `Maggard 26mm SHD /
  …`). This is the shape that produces the 49-row class.
- 235 knot-word left + handle-brand right (reversed).
- 9,916 a handle brand present, no knot word on the other side.
- 15,340 neither side names a handle brand — mostly `w/` joins
  (`Ever-Ready 100T w/20mm Envy White`), usernames (`/u/…`),
  and prose.

### 2.2 `with` / `w/` joins

22,853 rows contain ` with ` or `w/`:

- 8,815 handle-brand first + knot-word second
  (`Dogwood w/ DG B14 Hybrid 2 Band Badger`).
- 87 knot-word first + handle-brand second (reversed).
- 13,951 other (two products, annotations, prose).

### 2.3 The ` in ` join

2,938 rows contain ` in `:

- 416 a handle brand after "in" (`32mm Silvertip in Dogwood
  handle`, `28mm LotusTip in Maggard Razors Handle`).
- 2,522 no handle brand after "in" (prose, "set in", "in a …").

` in ` is the most explicit handle/knot join in the data — the knot
is named first, the handle second — but it is also the rarest of the
three joins.

### 2.4 "Hybrid" in the dataset

2,003 rows contain "hybrid" (all years):

- 1,154 dogwood-attached (`Dogwood [Handcrafts] [Custom] Hybrid`
  as a contiguous phrase).
- 118 knot-attached (tradeoff regexes: `briar hybrid`,
  `badger/boar hybrid`, `hybrid knot`, `hybrid badger`, …).
- 731 unclear — mostly non-Dogwood hybrids: AP Shave Co.
  SilkSmoke FlatTop/Fan Hybrid knots, PAA Nexus/Tribble/Roswell
  Hybrid synthetics, Rick Montalvo black wolf hybrid fan knots,
  bulb/fan hybrid shapes, and the Dogwood colorway/drop hybrids
  of §4. Only Dogwood Hybrid is a handle model; "hybrid" is a
  knot word everywhere else.

## 3. The 49-row class, precisely

The 49 rows are the post-handle Hybrid attributions where "Hybrid"
describes the knot, not the handle. Worked examples:

- `Declaration Grooming - B13** Dogwood/Briar Hybrid 28mm`
- `Dogwood Handcrafts/Briar Brushworks / 26mm Badger/Boar Hybrid`
- `Dogwood Handcrafts/Briar Brushworks Hybrid/ 26mm Boar/Badger`
- `Briar Brushworks/Dogwood Handcrafts / 26mm Maggard Boar/Badger Hybrid.`

### 3.1 What the matcher does today

The Hybrid entry's aliases are token sets (`{dogwood, hybrid}`,
`{dogwood, handcrafts, hybrid}`, …). `contained_match` /
`match_with_index` are token-subset matches: they ask only whether
the alias tokens are present *somewhere* in the string. In
`Dogwood/Briar Hybrid`, `{dogwood, hybrid}` is present — so the
handle wins, even though "Hybrid" is attached to "Briar" (the knot
maker) and the handle type is unstated. The knot side has no
counter-claim: no catalog knot entry is named "Briar Hybrid", so
nothing outranks the handle. The failure is a missing signal, not
a wrong ranking: subset matching cannot see word *attachment*.

### 3.2 What separates the 49 from the 596 correct rows

Token immediately before "hybrid" (Hybrid gain rows):

| class | token before "hybrid" |
|---|---|
| dogwood-attached (596) | handcrafts 325, dogwood 271 |
| knot-attached (49) | briar 46, boar 2, badger 1 |
| unclear (52) | brushworks 10, top 9, purple 14, handcrafts 6, works 5, b14 2, ossus 2, ashes 2, malachor 1, seascape 1 |

Between "dogwood" and "hybrid" in the 49: `[briar]` in 46;
`[handcrafts / briar / brushworks / 26mm / badger / boar]` in 1;
`[handcrafts / briar / brushworks / badger / boar]` in 1;
`[handcrafts / 26mm / maggard / boar / badger]` in 1.
In the 596, nothing but `handcrafts` / `custom` / nothing sits
between "dogwood" and "hybrid".

Segment simulation on the 805 gains:

| handle | seg-ok (kept) | seg-SPLIT (voided) |
|---|---|---|
| Dogwood Hybrid (697) | 621 | 76 |
| Dogwood Acrylic (92) | 92 | 0 |
| Maggard Sandy Pearl (15) | 15 | 0 |
| Maggard Sky Blue (1) | 1 | 0 |

By class within Hybrid: dogwood-attached 596/596 seg-ok;
knot-attached 48/49 seg-SPLIT; unclear 24 seg-ok / 28 seg-SPLIT.

The single knot-attached row the segment rule misses:

- `Dogwood Handcrafts Briar Brushworks Badger Boar Hybrid 26mm`
  (2022, pre-run: tier-2 ambiguous). No separator anywhere in
  the string; "Hybrid" is the knot (a Briar Brushworks
  badger/boar hybrid knot in a Dogwood handle). H2 catches it:
  between the alias's extreme tokens (`dogwood` … `hybrid`) sit
  `briar`, `brushworks`, `badger`, `boar` — three knot nouns.

### 3.3 Why the knot-noun set is {briar, badger, boar, knot}

H2 voids when a knot noun intervenes between the handle alias's
first and last token. The four words are the ones that actually
intervene in the wrong rows, and none of them intervenes in any
keep-row (§4): the keep-rows' intervening words are `handcrafts`,
`malachor`, `28mm`, `valley`, `of`, `ashes`, `purple`, `ossus`,
`w`, `seascape`, `handle`, `from`. A larger set (adding `fan`,
`bulb`, `shd`, `silvertip`, `white`, `black`, `top`, …) would buy
nothing on the measured data and risks voiding a future handle
colorway named e.g. "White" or "Fan". "Briar" is the one
judgment call: briar wood is a real handle material, so a future
`Dogwood Briar Hybrid` (briar-wood Hybrid handle) would be a safe
miss under H2 — it falls to tier-2 ambiguous, it is not
mis-attributed. In the data, "Briar" in brush strings means Briar
Brushworks (the knot maker) in every measured case.

## 4. The 52 unclear, hand-classified

### 4.1 The 24 the segment rule keeps (9 distinct strings) — all handle-attached

- `Dogwood Handcrafts - Malachor Hybrid - 26mm Fan (Silvertip Badger)`
  — Malachor is a colorway; Hybrid is the handle type; the knot is
  the 26mm Fan Silvertip.
- `Dogwood Handcrafts 28mm Valley of Ashes hybrid with timberwolf synth`
  — Valley of Ashes is a drop colorway; hybrid is the handle.
- `Dogwood Handcrafts Purple Hybrid 28mm Declaration Grooming B7 Knot`
  (and the `… B7 Badger Knot` / `#COMPOSITE #SHD` variants) — Purple
  is a colorway; Hybrid is the handle; the knot is the DG B7.
- `Dogwood purple hybrid - 28mm B8` — same shape.
- `Dogwood Handcrafts Ossus Hybrid` — Ossus is a colorway; Hybrid
  is the handle.
- `Doglaration, w Seascape hybrid handle from Dogwood and 27mm B4 badger
  knot from Declaration` — explicit "hybrid handle from Dogwood".
- `Dogwood Handcrafts - Hybrid B3` — Hybrid is the handle; B3 is the knot.

Keeping these is correct under P-17: a drop colorway is an attribute
of the model entry, not a separate product. Note the mirror pair
that proves the segment signal is the right one: `Dogwood Handcrafts
Purple Hybrid 28mm DG B7 Knot` (no separator — "Purple Hybrid" is
in the Dogwood segment, keep) vs `Dogwood Handcrafts/Declaration
Grooming Purple Hybrid 28mm B7 Knot` (separator — "Purple Hybrid"
is in the DG/knot segment, void, §4.2). Same words, opposite
attachment; only the separator distinguishes them.

### 4.2 The 28 the segment rule voids (7 distinct strings) — all knot-attached

- `Dogwood Handcrafts/Briar Brushworks Hybrid/ 26mm Boar/Badger`,
  `…/Briarwood Brushworks Hybrid / 26mm B15`,
  `…/Briar Brushworks Hybrid  Declaration Grooming B15 Badger`,
  `Dogwood Handcrafts / Briar Brush Works Hybrid B15 SHD  Badger`
  — Briar (Brushworks) Hybrid knots in Dogwood handles.
- `Dogwood Handcrafts/Declaration Grooming Purple Hybrid 28mm B7 Knot`
  — the DG Purple Hybrid B7 knot (see the mirror pair above).
- `Dogwood w/ DG B14 Hybrid  2 Band Badger` — the DG B14 Hybrid knot.
- `Dogwood Hancrafts -Black/Blue/Grey-APSCO 26mm SilkSmoke Fan/Flat Top
  Hybrid` — the AP Shave Co. SilkSmoke Flat Top Hybrid knot.

### 4.3 Pre-run state of the 76 seg-SPLIT rows

47 knot-attached tier-2 ambiguous, 1 knot-attached tier-2 complete,
18 unclear tier-2 ambiguous, 1 unclear unverified complete,
9 unclear tier-1 knot_only. Voiding returns each to exactly that
state (the 9 knot_only rows return to a knot attribution — the
knot entry that claimed them pre-handle re-claims them once the
handle is out of the candidate set).

## 5. The bare-brand class — decided, not dangled

"Dogwood handle" (94 rows) and "Maggard handle" (918 rows) in the
A/B years name a brand, not a model, and resolve to nothing as a
handle. Their current outcomes (post-handle run): Maggard 623
tier-1 complete (a complete Maggard brush entry claims the whole
string), 229 tier-1 knot_only, 45 tier-2 complete; Dogwood 55
tier-1 knot_only, 16 unverified complete, 13 tier-2 ambiguous.
In other words they mostly already resolve to *something* — a
complete brush or a knot — with the handle half unattributed.
That is the honest state.

**Decision: the matcher leaves them unresolved.** A brand-level
handle entry ("Maggard handle", "Dogwood handle") would be a
catalog decision — it would have to be scoped like any other
entry (is Maggard's standard handle one product with color
attributes, per P-17? is "Dogwood handle" a meaningful product
or a bucket for every Dogwood handle ever made?). P-26 as written
authorizes model/shape entries only. Creating such entries to
soak up 1,012 rows would be exactly the arbitrary bucketing Jim
ruled against. If Jim later wants brand-level handle entries,
that is a separate catalog scoping task with its own evidence;
the guard is written so it does not preclude it (a brand-level
entry's alias, e.g. `{maggard, handle}`, would be judged by the
same H1/H2 attachment test).

## 6. The design: guard rules H1 + H2

Applies in the brush path only (`_match_brush_primary`), to
**handle entries only**, at both the whole-string match and the
contained-match calls. The asymmetry is deliberate: handle aliases
are short model names (`{dogwood, hybrid}`) that must be written
contiguously in one part of the string; knot and brush aliases are
often full poster strings (`Chisel & Hound RC Zebra w/ 26mm
Fanchurian Badger`) that legitimately span separators. Applying
H1 to knots would break knot matching outright.

### H1 — segment attachment

Split the raw string on `/`, ` with `, ` w/ `, ` in `, ` + `,
` | `, ` then `. A handle alias counts only if **all** its tokens
lie in a single segment (each segment normalized with the
matcher's `N()`). The alias judged is the entry's **largest
contained alias** — the same evidence the matcher selected the
entry on. (For subset-rev wins, the tokens of the winning alias
that are present in the string are judged the same way.)

Separators NOT used: `" - "` (inside handle names), comma
(annotation trap). `w/` is matched before bare `/`.

### H2 — knot-noun intervention

Inside the segment H1 found, take the first occurrences of the
alias's tokens; no knot noun ({briar, badger, boar, knot}) may sit
strictly between them (alias tokens themselves excluded). Catches
the one row H1 misses (§3.2). Judging the *first* occurrence
inside the passing segment is deliberate: a later repeat of a
brand token in prose/annotations must not stretch the window
across the knot's own words. Worked case found during the build:
`Dogwood hybrid brush with 30mm black synth knot | I know it's
from Dogwood, and I think …` — a real Dogwood Hybrid handle
whose second "Dogwood" (in the prose after `|`) would have
pulled the knot's own word "knot" into a whole-string window
and voided a correct attribution. First-occurrence keeps it;
a whole-string min/max window does not. A knot noun *after* the
descriptor (`Dogwood Hybrid Badger knot`) does not void — the
descriptor is already attached to the handle.

### H0 — what the guard does not judge

- Exact / normalized whole-string handle wins: the string IS the
  handle name (31 of the 805 gains). They pass H1/H2 by
  construction (no separators in handle aliases, no knot nouns in
  them) and the guard leaves them alone.
- Non-handle entries: brush and knot winners are never filtered.
- Non-brush fields: untouched.

### Predicted yield

| outcome | rows |
|---|---|
| gains kept (H1+H2 pass) | 728 / 805 (90.4%) |
| gains voided, return to pre-handle outcome | 77 (48 knot-attached + 28 unclear-knot + 1 H2 row) |
| certain-but-wrong remaining in the 49 class | 0 |
| non-brush changes | 0 |
| regressions vs pre-handle baseline | 0 (to be verified, not assumed) |

Retention by entry: Hybrid 620/697, Acrylic 92/92, Sandy Pearl
15/15, Sky Blue 1/1 (Cast Object and TRBR have no rows in the
A/B years). The 77 voided rows are all Hybrid.

### Flag and blast radius

Module flag `HANDLE_GUARD_ENABLED` (default on after A/B
verification). The guard only ever *removes* handle entries from
a candidate set, so a voided row's selection is the pre-handle
selection by construction; a kept row's selection is the
post-handle selection. The A/B must still verify both
equivalences row-by-row. No catalog entry, alias, or DB write.
No change to the P-25/comma code paths. No shared-function
signature changes: the guard lives in brush-local wrappers
around the existing index calls.

## 7. Open questions

1. **Brand-level handle entries** (§5) — a catalog decision for
   Jim/validators, not a matcher question. Evidence: 94 Dogwood +
   918 Maggard bare-brand rows (A/B years).
2. **Drop colorways as handle attributes** — the §4.1 keeps rest
   on P-17 (colorway = attribute). If a future ruling says drop
   colorways are distinct products, the keep-set changes — but the
   guard itself does not: it only judges attachment, not identity.
3. **Subset-rev handle wins** — zero in the A/B years. The guard
   handles them (present-tokens check), but they are unmeasured.
   A bare `Hybrid` string would subset-rev-win the Dogwood Hybrid
   entry today; whether that is wrong enough to guard is a
   separate question with no dataset rows behind it yet.
4. **H2's "briar" judgment** (§3.3) — a future briar-wood Dogwood
   Hybrid handle string would be a safe miss under H2. If such a
   product is ever cataloged, H2's noun set needs revisiting.
5. **The 9 knot_only tier-1 rows in the void set** (§4.3) —
   expected to return to knot_only; the A/B confirms it.

## 8. A/B verification (2026-11-18, this build)

Two runs from the current catalog (2022/2024/2025/2026, 91,053
rows): guard ON vs guard OFF, outputs in
`~/workspace/scratch/handle_guard/guard/` and `noguard/`
(driver `run_ab.py`, diff `diff_guard.py`). Live matched files
were never touched (byte-identical before/after).

| check | predicted | actual |
|---|---|---|
| guard-vs-noguard changed rows | 77 | **77**, all brush-field, **0 non-brush** |
| gains kept | 728 / 805 (90.4%) | **728** (Hybrid 620, Acrylic 92, Sandy Pearl 15, Sky Blue 1) |
| gains voided | 77, all Hybrid | **77, all Hybrid** |
| knot-attached rows still crediting Hybrid | 0 | **0** |
| kind transitions (noguard → guard) | — | handle_only → ambiguous 66, handle_only → complete 2, composite → knot_only 9 |
| guard-vs-pre rows not explained by noguard-vs-pre | 0 | **0** (zero regressions) |
| guard-vs-noguard rows with no handle_id either side | 0 | **0** (blast radius is exactly the handle rows) |
| noguard-vs-builder-POST brush drift | 0 | **0** (88 non-brush rows, all the sweep's soap promotions) |

Worked strings in the guard run: `32mm Silvertip in Dogwood
handle` → unverified cluster (unchanged, bare-brand); `28mm
LotusTip in Maggard Razors Handle` → tier-2 Maggard cluster
(unchanged); `Dogwood Handcrafts Hybrid / Maggard Boar 28mm` →
ambiguous (unchanged from post-handle); the H2 row →
tier-2 ambiguous (voided); Malachor Hybrid → handle_only Hybrid
(kept).

Two defects found and fixed during the build, both caught by the
A/B / unit tests before the final run:

1. **Method label**: the first version of the guard wrapper
   returned `'norm'` instead of `'normalized'` for normalized
   wins (1,824 brush rows relabeled vs the builder's outputs).
   Fixed to `'normalized'`; brush drift vs builder POST is now 0.
2. **H2 window**: the first H2 used whole-string min/max token
   positions, which let a later repeat of a brand token in
   prose/annotations stretch the window across the knot's own
   words and void one correct row (`Dogwood hybrid brush with
   30mm black synth knot | I know it's from Dogwood …`).
   H2 now judges first occurrences inside the segment H1 found.
   The fixed guard voids exactly the predicted 77 (simulation
   and real guard agree on all 805 gain rows, 0 disagreements).

Scope note: the A/B covers the builder's four years
(2022/2024/2025/2026). 2017/2018/2023 were not re-run; the
guard's per-row behavior was verified directly on all 805 gain
strings (year-independent), and the next routine matcher run
will cover the remaining years.
