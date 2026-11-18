# How SOTD posters put multiple items into one field

**Date:** 2026-11-16
**Analyst:** subagent (read-only analysis for the P-25 split design)
**Dataset:** `~/workspace/sotd/sotd_*_full.json`, 11 files, **241,319 rows** scanned
(2016–2026; the parent's count was 241,282 — 37 more rows, presumably a
later pull). Fields: razor, blade, soap, aftershave, fragrance, brush.
There is **no `knot` field in the dataset** (knot is catalog-only), so the
P-25 knot scope has nothing to analyse here; handle/knot constructions are
covered under brush.
**Catalog:** `catalog_merged.json` as loaded by `match_all.py` (the matcher's
own source of truth). No files, database, or precedents were modified.

## 0. Headline findings

- **The user was right: `;` and `+` are not the only delimiters — and `|` is
  bigger than both.** `|` appears in 59,746 rows and is the dominant
  multi-product separator (49,013 of them in aftershave). `;` (entity-cleaned)
  is only 3,091 rows; spaced `+` is 7,503. The parent's earlier 13,183
  semicolon count was inflated by HTML entities (`&mdash;`, `&#39;`).
- **Naive separator counting would flag half the dataset.** 115,853 rows
  (48.0%) contain at least one of the 10 tested separators in some field.
  Most of those are *not* multi-product joins: the same characters are
  brand names, part-joins, annotations, scent lists, and prose.
- **Under the recommended set + strengthened guard, 22,943 rows (9.51%)
  would actually split** (exact full-dataset count, not an estimate). A
  further ~35,700 rows contain a recommended separator but are declined by
  the guard (safe misses — they stay whole, status quo).
- **The "both parts must match a real entry" guard, on its own, is NOT
  sufficient.** Three failure modes, each demonstrated with worked examples
  in §6, let false splits through at rates up to ~90% in the worst cell
  (`+` in blade: naive both-match 35/39, of which most are the single blade
  "Crystal Super + Platinum" split into two wrong entries). The guard needs
  five strengthenings (§6) before it is safe to ship.
- **Separators are field-specific.** There is no single separator set that
  works in all fields: `|` is genuine in aftershave and blade but is
  handle/knot or prose in brush and soap; `,` is a real routine-list
  separator in aftershave and a scent-list trap everywhere else; `w/` and
  `with` are handle+knot constructions in brush and additive notes in soap.
  The recommendation is therefore a **per-field** table (§8), not a global
  list.
- **`','` is excluded entirely**, despite being the second-most-common
  genuine join in aftershave: only ~5 of 9 strict passes in the fully
  verified aftershave sample were clean splits; the rest were scent-name
  commas, product names containing commas ("I, Rich Moose"), and alias
  pollution (§7.4).
- **Two catalog-hygiene findings fell out of the work** (§9): (a) composite
  field strings harvested as aliases poison reverse-subset matching — the
  alias `"Cold" Water Rinse | Chiseled Face Ghost Town Barber Aftershave
  Splash` on the Ghost Town Barber entry makes the routine phrase "Cold
  water rinse" resolve to that product; (b) the attested entry
  `unverified/aftershave/leftover-lather` ("Leftover Lather") is a joke
  string, not a product.

## 1. Method

### 1.1 Census (Stage 1)

`sep_count.py`: for every row and field, test each candidate separator.
Definitions (the exact predicates matter — see §3 notes):

| key | predicate |
|---|---|
| `semicolon_any` | `;` present |
| `semicolon_join` | `;\s` after stripping HTML entities |
| `plus_any` / `plus_spaced` | `+` present / `\s\+\s` |
| `slash_any` / `slash_spaced` | `/` present / `\s/\s` |
| `pipe` | `\|` present |
| `comma` | `,` present |
| `and_word` | `\sand\s` (case-insensitive) |
| `amp_any` / `amp_spaced` | `&` present / `\s&\s` after entity-strip |
| `w_slash` | `\bw/` |
| `with_word` | `\swith\s` |
| `then_word` | `\sthen\s` |
| `vs_word` | `\svs\.?\s` |
| `paren` | `(` present |
| `newline` | `\n` present |
| `double_slash` | `//` present |
| `emdash` | `\s[—–]\s` |
| `x_word` | `\sx\s` |
| `tilde` | `~` present |
| `colon` | `:` present (includes URLs — see §3) |
| `dash_spaced` | `\s-\s` |

### 1.2 Sampling and manual classification (Stage 2)

`sep_sample.py`: deterministic sample (seed 20261116), 25 rows per
separator per field where the pool allowed (fewer where sparse), 2,623
sample lines in total — **every line was read and classified** by hand into:
(a) genuine multi-product join, (b) brand-name artifact, (c) prose/note
pasted into the field, (d) HTML entity / encoding artifact, (e) single
product whose name legitimately contains the separator, (f) other
(part-whole: head/handle, plate/pass, handle/knot; comparison; collab;
additive; strikethrough correction).

Separator discovery: the 200 longest field strings (`long_strings.txt`)
were also read in full. No separator beyond the tested set emerged. The
longest strings are pipe-joined aftershave mega-lists (up to 15 products,
e.g. BVsaPike's 2021-06-08 Lather Games list), prose pasted after a pipe,
and USS-SpongeBob's razor comparison essays. Two label patterns surfaced
there: `H: X / F: Y` (head/face) and `Pass 1: X; Pass 2-3: Y`.

### 1.3 Precision test (Stage 3)

The question the test answers: *for sampled rows containing a separator,
does EACH part independently resolve to a real catalog entry?* The test
uses the matcher's own core — `match_all.match_field` /
`match_all.match_brush` over the three-tier indexes (tier-1 verified /
needs-review, tier-2 attested / corroborated / anecdotal, unverified tier
counted separately as weak) — on each split part, with part cleaning that
mirrors what a split implementation would do: HTML-unescape, strip
`~~...~~` strikethrough segments, strip markdown links to their text,
strip bare URLs, then try the part as-is, with trailing parenthetical
groups removed, and truncated at the first ` (` (use-count / colour /
sample annotations).

Sample: seed 20261117, 40 rows per separator per field (all rows where the
pool is smaller). Three runs were made because the first run's headline
numbers were wrong in instructive ways:

- **Run 1 (naive guard):** all parts tier-1/2 only. Produced absurd rates
  (`;`/razor 78%, `+`/blade 90%) — see §6 for why.
- **Run 2 (distinct + rev-floor):** added "all resolved entries must be
  distinct" and "a subset-rev-only resolution needs ≥3 tokens".
- **Run 3 (full guard G0–G6):** added G0 whole-string-first, G4
  >80-char prose parts cannot match, G5 routine-phrase junk, G6
  additive-part junk. Two bugs were found and fixed along the way:
  (i) G0 originally applied part-variants (paren-strip/truncate) to the
  *whole* value, so a prefix like `Kai` blocked splitting
  `Kai (DE) | Kai Captain Titan Mild (AC)` — G0 now tests the whole value
  as-is only (plus a trailing format-word strip, G0b); (ii) Run 2's
  `some_match` column double-counted `all_match` rows (tally bug, no
  effect on the strict counts).

Final strict-split rates are reported two ways: the **sampled** rate
(strict passes / sampled rows) and the **exact full-dataset count**
(applying the guard to every row of the pool). Where the two disagree
(e.g. `+`/soap: sampled 8/40 vs exact 94/1,293 = 7.3%), the exact count
governs — the 40-row samples are small and noisy once whole-matches are
removed from the denominator.

Caveat: the test is a *lower bound* on true matchability in one direction
(it does not apply P-15 loose aliases or P-14 format resolution, so some
genuine parts like bare `Astra` fail to resolve) and an *upper bound* in
another (subset/reverse-subset matching resolves annotation fragments to
entries — the guard's G2/G3 exist to contain exactly that). Precision
claims below rest on manual verification of the strict-pass examples, not
on the rates alone.

## 2. Census: per-separator per-field counts (241,319 rows)

| separator | razor | blade | soap | aftershave | fragrance | brush | TOTAL |
|---|---:|---:|---:|---:|---:|---:|---:|
| `;` any | 1,925 | 2,508 | 5,826 | 6,894 | 1,831 | 4,657 | 23,641 |
| `;` + space (entity-cleaned) | 632 | 31 | 76 | 2,211 | 67 | 74 | **3,091** |
| `+` any | 3,063 | 203 | 1,981 | 4,614 | 206 | 2,206 | 12,273 |
| ` + ` spaced | 959 | 46 | 1,293 | 3,781 | 70 | 1,354 | **7,503** |
| `/` any | 24,548 | 2,588 | 64,385 | 63,239 | 21,147 | 34,126 | 210,033 |
| ` / ` spaced | 2,406 | 197 | 912 | 867 | 184 | 4,986 | **9,552** |
| `\|` | 2,007 | 1,649 | 4,319 | 49,013 | 1,059 | 1,699 | **59,746** |
| `,` | 8,248 | 2,699 | 3,905 | 10,931 | 1,995 | 6,159 | **33,937** |
| ` and ` | 1,376 | 450 | 24,657 | 25,816 | 6,813 | 6,004 | 65,116 |
| `&` any | 3,092 | 2,925 | 24,657 | 22,101 | 4,838 | 15,541 | 73,154 |
| ` & ` spaced | 1,511 | 54 | 10,388 | 10,391 | 2,320 | 7,919 | **32,583** |
| `w/` | 4,812 | 13 | 159 | 656 | 0 | 14,730 | 20,370 |
| ` with ` | 4,745 | 257 | 980 | 2,355 | 756 | 8,116 | 17,209 |
| ` then ` | 78 | 47 | 56 | 247 | 51 | 22 | 501 |
| ` vs ` | 29 | 4 | 9 | 3 | 1 | 18 | 64 |
| `(` paren | 29,727 | 16,308 | 69,248 | 62,867 | 21,650 | 17,888 | 217,688 |
| newline | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| `//` | 5,705 | 1,025 | 59,438 | 56,935 | 19,823 | 6,999 | 149,925 |
| em/en dash spaced | 2,164 | 1,004 | 9,849 | 10,038 | 4,419 | 1,350 | 28,824 |
| ` x ` | 201 | 29 | 488 | 270 | 61 | 2,262 | 3,311 |
| `~` | 70 | 46 | 155 | 116 | 76 | 82 | 545 |
| `:` (any; incl. URLs) | 6,125 | 1,149 | 60,013 | 57,239 | 20,007 | 7,162 | 151,695 |
| ` - ` spaced | 20,392 | 11,844 | 134,654 | 125,967 | 52,877 | 22,877 | 368,611 |

Notes on the counts:

- **`;`:** the 13,183 figure from the quick measurement counts every `;`,
  including the ones inside HTML entities (`&mdash;`, `&#39;`, `&quot;`,
  `&amp;`). Entity-cleaned `;\s` gives 3,091. The raw `;` count is 23,641.
- **`/`:** 210,033 rows contain a slash, but almost all are URLs
  (`https://…`) or sizes (`6/8`, `1/2`). Spaced ` / ` is the join form:
  9,552 rows.
- **`//`:** 149,925 rows — URLs only, not a separator. (Every
  trythatsoap / imgur / fragrantica link.)
- **newline:** zero rows contain `\n` in any field. Newlines are not a
  separator in this dataset.
- **`:`:** the census counts `:` anywhere, which is dominated by URLs.
  The sampler's definition (`: ` excluding `://`) gives 1,430 rows total
  (razor 292, blade 44, soap 516, aftershave 272, fragrance 162,
  brush 144) — that is the meaningful colon count.
- **` - `:** 368,611 rows — it is *the* brand–product delimiter
  (`Gillette - Fat Boy`, `Barrister and Mann - Seville`), never a join.
- **paren:** 217,688 rows contain `(` — annotations, not joins (§4).

## 3. What each separator actually means (manual classification)

Sample sizes: 25 rows per separator per field (seed 20261116), all read.
Shares below are the manual-sample reads, rounded — they describe the
sample, not a second census.

### 3.1 Semicolon `;` — 3,091 rows

| field | pool | dominant reading |
|---|---:|---|
| razor | 632 | **One razor + plate/pass annotation.** GroundbreakingRole45's repeated `Karve CB SS SB (D Plate, First Pass; B Plate, Second Pass)` dominates the pool. Genuine two-razor `;` rows exist (`Pass 1: Feather SS; Pass 2, 3 - Rockwell 6s (plate 3)`) but are a minority. Also `Rockwell 6C; R2 for all passes` (one razor, plate note). |
| blade | 31 | Mixed. Genuine two-blade (`Voskhod (face); Ladas (head)`; `Personna GEM PTFE; KAI Captain Titan Mild Protouch MG`) vs annotations (`Astra SP (7; RIP)` — the `;` is inside a paren). Tiny pool. |
| soap | 76 | Mostly annotations. wallygator88's `Mikes Natural - Hungarian Lavender; Vetiver (N)` pattern is ambiguous (second soap or note?). No strict split fired in the 40-row precision sample. |
| aftershave | 2,211 | **Mostly genuine multi-product**: splash+balm, alum+splash, including 3-product strings (`Zingari Man - The Magician recovery splash; PAA - Tea Party 508 balm`; `Snake Bite; Stirling Unscented Balm`). |
| fragrance | 67 | Mostly genuine two-fragrance (wallygator88's `Chatillon Lux - 33 Chestnut Street; Chatillon Lux- Lavande Poivre`). |
| brush | 74 | Mostly handle+knot = one brush, esp. Aresmsu's `Handle; with Knot` pattern. One sampled strict pass was a joke (`anbbas synthetic tuxedo (initially); Hands (finally)` — "Hands" is not a brush). |

### 3.2 Plus ` + ` — 7,503 rows

| field | pool | dominant reading |
|---|---:|---|
| razor | 959 | **Almost never two razors.** Razor+blade (`Maggard MR8 + V3 + GSB` is cross-field), razor+handle, head+plate. One sampled strict pass was head+handle (`Gillette NEW De Luxe Head + Rockwell 6S Handle (Black)`) — one frankenrazor, falsely split. |
| blade | 46 | Mixed, tiny pool. The dominant pattern is a **single blade name containing `+`**: `Crystal Super + Platinum` (one blade — Personna Crystal; the catalog entry is `DE/crystal-super-plus`). Genuine two-blade joins exist (`Astra SP + Personna Twin Pivot Plus`; `Ted Pella Injector + Feather Professional`). Cross-field pastes exist (`Rockwell 6S (R3) + Gillette 7 O'Clock Super Stainless` — a razor name in the blade field). |
| soap | 1,293 | **Brand names dominate** (`Tallow + Steel`, `Barrister + Mann`). Genuine joins are mostly soap + non-soap (`Dr. Jon's - Classic - Soap + CFG Cryogen`; `+ Proraso Green`) or **additives** (`+ Stirling Frost Drops`, `+ Terrorade` — see §7.3). |
| aftershave | 3,781 | **Mostly genuine two-product** (splash+balm/serum: `Barrister and Mann *Nocturne* splash + Zingari Man Rescue Potion`; `Stirling Soap Co Unscented Aftershave Splash + B&M Cheshire After Shave Balm`). B&M brand-spelling confound (`Barrister + Mann – Leviathan`). Note: half the examined strict passes are wyze0ne routine strings where each side is itself a comma-list — genuine-sided but partial (§6.4). |
| fragrance | 70 | ~Half genuine two-fragrance layering (`Armaf Club de nuit intense man + Executive man`; `Creed Royal Oud 2 sprays + 1 spray creed original Santal`), half single scent names containing `+` (`Vetiver + Oakmoss`, `Whiskey + Ginger`) or brand spelling (`Barrister + Mann – Electric Mayhem`). |
| brush | 1,354 | **Overwhelmingly handle+knot = one brush** (`Sawdust Custom + 28mm SynBad`). All three sampled strict passes were the same false pattern (`Carnavis & Richardson Industry + Elite Manchurian [White]` — one brush). |

### 3.3 Slash ` / ` — 9,552 rows

| field | pool | dominant reading |
|---|---:|---|
| razor | 2,406 | Razor+blade/handle/plate; some genuine two-razor; some same-product-two-names (`Slim Twist / Knack`; `Wolfman WR2-DC 0.95 SB / 1.25 OC` — one razor, two gaps). The only sampled strict pass was false (a Stirling razor's `Austin Handle / ST plate` resolving to Gillette Slim via a composite alias). |
| blade | 197 | **Mostly genuine two-blade** (`Vokshod, DE / Treet Classic, DE`; `Gillette 7 O'Clock Super Platinum / Dorco ST 301`; `Feather FHS-10 (1) / Feather HS` — two formats). One prose hazard: a long Malthus paragraph containing `/` whose second half subset-matches a blade name. |
| soap | 912 | rmic_'s `(H) X / (F) Y` head-vs-face two-soap joins (genuine) **plus** collab-maker joins = one product (`Chatillon Lux / Declaration Grooming - TSM Fougère`). The guard blocks the collabs (whole-match, 25/40 sampled). |
| aftershave | 867 | **Mostly genuine** (`Nivea Sensitive Balm / Stirling Christmas Eve AS`; `Thayer's Witch Hazel / Stirling Barbershop Alcohol Splash`). |
| fragrance | 184 | **Heavily collab-maker joins = one product** (Cerberus three makers). The one sampled strict pass was false (`Azzaro pour Homme Silver Black / Onyx` — bare `Onyx` resolved to the wrong maker's Onyx). |
| brush | 4,986 | **Overwhelmingly handle/knot = one brush** (`Chisel & Hound "Root Beer Float" / 26mm Maggard Razors premium boar`). All three sampled strict passes were one-brush false splits. |

### 3.4 Pipe `|` — 59,746 rows

| field | pool | dominant reading |
|---|---:|---|
| razor | 2,007 | Mixed genuine two/three-razor (`Gillette 'The Knack' Slim Twist \| Feather AS-D2`; `Feather AS-D2 \| Timeless .95 SB`) + annotations/prose (USS-SpongeBob's comparison essays use `\|` between review sections). |
| blade | 1,649 | Mixed. kind_simian's `Blade (N) \| Other blade` two-blade tests are genuine (`Feather - Hi Stainless (3) \| Personna - "Lab Blue"`; `Kai (DE) \| Kai Captain Titan Mild (AC)` — two formats); Malthus's prose-after-pipe is not. |
| soap | 4,319 | Mostly note/count/duplicate, occasional genuine multi. Two sampled strict passes: one genuine (`Chatillon Lux - La Petite Prairie \| Chatillon Lux - Confluence`), one duplicate listing of the same soap twice (`Chatillon Lux Vide Poche \| [Chatillon Lux/Declaration Grooming - Vide Poche - Soap (LE)]`). |
| aftershave | 49,013 | **The dominant multi-product separator in the dataset.** Splash \| balm \| moisturizer routines. Manual sample ~24/25 genuine. The 15-product BVsaPike list is all `\|`. |
| fragrance | 1,059 | Mostly note/count/prose. The one sampled strict pass was a duplicate (`Mäurer & Wirtz Tabac Original \| #MäurerUndWirtz Tabac Original` — same product twice, hashtag repeat). |
| brush | 1,699 | Mixed handle\|knot (one brush) vs genuine multi-brush. Zero strict passes in the 40-row sample. |

### 3.5 Comma `,` — 33,937 rows

| field | pool | dominant reading |
|---|---:|---|
| razor | 8,248 | Specs/annotations (`Blackland Blackbird - SB, SS, 85mm`); occasionally genuine two-razor (`Facon kamisori shavette, 1955 Gillette Super Speed`). |
| blade | 2,699 | Format/origin/annotation (`Astra Superior Platinum, DE`; `Wilkinson Sword, Germany`); `then`-sequenced pairs hide behind commas (`Blue Star, then Personna GEM PTFE`). |
| soap | 3,905 | **One product**: scent-name lists (`Barrister and Mann - Lime, Lavender, and Cedarwood`), base annotations (`WK Monaco Royale, DM Formula`), maker+product. |
| aftershave | 10,931 | **The exception: comma-joined multi-product lists ARE common** (`Thayers, Zingari Rescue Potion, Zingari Unscented Balm, Noble Otter Hamami A/S` — four products; `Alum, Extra Lather, Witch Hazel, L'Occitane Cade Balm` — a routine list). But the same field carries the scent-name trap and routine-phrase traps — see §7.4 for why comma is still excluded. |
| fragrance | 1,995 | One product: scent-note lists (`Chatillon Lux - Yuzu, Rose, Patchouli`), brand+product (`Armani, Acqua Di Gio`). |
| brush | 6,159 | Specs (`CaYuen Workshop, Diablo Split 26mm Timberwolf Synthetic`; `Maggard Razors - [Maggard Blue Swirl, Timberwolf Synthetic, 24mm]`). |

### 3.6 ` and ` / ` & ` — 65,116 / 32,583 rows

Dominated by brand names in every field: `Barrister and Mann` (soap
24,657 / aftershave 25,816), `Wade and Butcher`, `Chisel and Hound`,
`Viktor and Rolf`, `Morris & Forndran`, `Mäurer & Wirtz`, `Tallow & Steel`.
Genuine joins exist but are rare (`Weck razor (h) and Weck Hair shaper
(f)`; `Alumigoose and Brass General`; `Wizamet DE and Schick Yellow
Injector`; `Personna blue & Voskhod`; `Astra Superior Stainless [blue],
Gillette 7 O'Clock Sharpedge, & Gillette Nacet` — three blades). Both
are excluded as separators; the `&` blade cases (54 rows) are too few
and too confounded by maker names to be worth a carve-out.

### 3.7 `w/` — 20,370 rows; ` with ` — 17,209 rows

| construction | reading |
|---|---|
| brush `w/` (14,730) / `with` (8,116) | **Handle-with-knot = one brush**, near-universally (`Rubberset 400-3 with unbleached 26 mm Zenith knot`; `Chisel and Hound Sakura with v21 Fanchurian`). This is the canonical brush construction in the dataset. |
| razor `w/` (4,812) / `with` (4,745) | Head+plate/handle (one razor: `Karve CB with OC C plate`; `Maggard MR-18 with V3 head`) or razor+blade (`59 fatboy w/Rapira SS` — cross-field). |
| soap `w/` (159) / `with` (980) | **Additives** (`Stirling Hot Apple Cider w/ frost drops`; `Catie's Bubbles Waterlyptus with Permafrost`; `Wholly Kaw Fern Concerto w/ Tallow & Synthetic Menthol`) or collab credits (`West Coast Shaving collab. w/ Oleo Soapworks`). Rare genuine two-soap (`TOBS Grapefruit shaving cream w/Williams Mug shaving soap`). |
| aftershave `w/` (656) / `with` (2,355) | Annotations (`Thayers Witch Hazel w/ alcohol`; `Stirling Unscented with Menthol - Balm` — one product). One genuine pattern: `Chiseled Face Trade Winds Balm mixed with Nivea Post Shave Balm` (two balms mixed). |
| fragrance `with` (756) | Prose after `\|`; one genuine layering (`B&M Leviathan EdT layered with Bvlgari Black`). |
| blade `w/` (13) | Cross-field / annotations only. |

Both excluded. The `w/` and `with` strict-pass rates look deceptively
passable in places (e.g. `w/`/soap 7/40) because annotation fragments
reverse-subset-match to entries; manual verification shows the passes are
mostly additive traps (§6).

### 3.8 ` then ` — 501 rows

| field | pool | dominant reading |
|---|---:|---|
| razor | 78 | ~Half genuine sequential two-razor (`Teardrop "77" Shavette, then Lupo`; `Gillette Black Beauty, then Gillette Tech`), half same-razor setting changes (`Merkur Futur first pass 1, then 1.5, then 2`; `Rockwell 6S R3 then R5`). The guard blocks the settings cases (whole-match). |
| blade | 47 | **Mostly genuine sequential two-blade** (`Tiger then Shark`; `Crystal Super Stainless, then Feather, then Astra` — three blades; USS-SpongeBob's shave-numbered pairs `Cloud 62x16mm (shave #3) then Rapira Platinum Lux (shave #17)`). |
| soap | 56 | Mostly prose; one genuine (`Palmolive Stick, then NSS Lavender`). |
| aftershave | 247 | Mostly genuine sequential two-product in wording (`Kraken splash then Kraken milk`; `Lucky Tiger then Proraso Green`; `Alum block then Old Spice Classic`) — but usually embedded in prose routines where the `then`-split mis-attributes (§7.4: `Alum block followed by Nivea then Old Spice Classic` attributes `Alum block followed by Nivea` to alum alone, dropping Nivea). |
| fragrance | 51 | All prose (`and then the talc/powder is easily discerned…`). |
| brush | 22 | Two genuine (`Semogue 1305 then DSC 24mm White Synthetic`), rest prose. |

### 3.9 ` vs ` — 64 rows; parens; em-dash; `x`; tilde; colon; ` - `

- **`vs` (64 rows): comparisons, not uses.** `Karve vs. Merkur 37c`,
  `Leaf Twig vs Leaf Thorn`, `RazoRock SS Lupo 72 vs Game Changer 84`,
  `Arko vs. La Toja - FIGHT!`. Both sides are real products (the guard
  passes 6/29 razor rows), but the poster compared them; splitting would
  credit both with a use. Excluded on semantics — no guard can
  distinguish a comparison from a two-product shave.
- **Parentheses (217,688 rows): annotations, never a second product.**
  Use counts `(6)`, settings `(setting 7)`, materials `(Stainless
  Steel)`, dates `(1948-50)`, colours `(green)`, sizes `(26mm)`,
  `(sample)`, markdown links `(https://…)`, and product-name parens
  (`You & I (Will Die)`). The `+` in `Rockwell 6S (R5) + Rapira Platinum
  Lux (8)` does the joining; the parens are annotations.
- **Em/en dash (28,824 rows): brand–product separator** in all fields
  (`Barrister and Mann – Seville`; `House of Mammoth – Hygge`;
  `7 O'Clock – Sharpedge (Yellow)`). Never a join.
- **`x` (3,311 rows): head×handle or collab = one product** (`Wolfman -
  WR2 0.75 DC x WRH2`; `House of Mammoth x Barrister and Mann – Smash`;
  `Southern Witchcrafts x Australian Private Reserve - Gravefruit`).
  Blade `x` is counts/dimensions (`GSB x 2 use`; `Cloud 62mm x 16mm`) or
  the single product `Gillette x Wilkinson Sword`. One exception class:
  soap **sample mash-ups** (`Southern Witchcrafts Fougère Nemeta x Los
  Jabones de Joserra Spanish Fern (sample mash-up)` — two soaps mixed),
  too rare and too confounded by collabs to split on.
- **Tilde `~` (545 rows): strikethrough corrections.** `~~Feather AS-D2~~
  Rockwell 6s #4`, `~~Col. Conk - Lime - Soap~~ Chiseled Face - Pine Tar -
  Soap`, `~~Gillette - Slim Adjustable M1~~ Ever-Ready - Streamline` —
  the struck item was NOT used; the un-struck item is the real one. Also
  `~$77` (price), `~1930` (approx. date), `1960~1970` (range). `~` is
  not a separator; `~~...~~` segments should be **stripped before
  matching** (guard preprocessing), not split on.
- **Colon (1,430 meaningful rows): brand:product / series labels**
  (`Declaration Grooming: Convergence`; `The Four Horsemen: War`;
  `EldrormR Industries - GEM Division: MM24`). Not a join. The `H:
  Schick Grip / F: Universal Shavette` and `Pass 1: Wolfman Spider;
  Pass 2-3: RR Wunderbar Slant` patterns are genuine two-product joins,
  but the operative separators there are `/` and `;`, with the labels as
  a bonus signal.
- **` - ` (368,611 rows): the brand–product separator.** Never a join.

## 4. Precision test results

### 4.1 The naive guard fails — worked examples

"Both parts must match a real entry" (tier-1/2, via the matcher's own
`match_field`) gives these sampled both-match rates — and they are
**wrong** in the worst cells:

| cell | naive both-match | what it actually is |
|---|---:|---|
| `;` / razor | 31/40 (78%) | One razor, two plates/passes. `Karve CB SS SB (D Plate, first pass; B Plate, second pass)` — both parts resolve to the **same** entry `razor/karve-christopher-bradley` (the `B Plate, second pass` fragment reverse-subset-matches the Karve aliases). |
| `+` / blade | 35/39 (90%) | One blade, split wrong. `Crystal Super + Platinum` → `DE/crystal-super-plus` + `DE/gillette-platinum`. Plus cross-field pastes (`Rockwell 6S (R3)` → the *blade* `DE/rockwell-swedish-stainless` via the bare alias `Rockwell`). |
| `w/` / razor | 22/40 (55%) | `Rockwell 6S (6) w/ Silver Blue` — `Silver Blue` reverse-subset-matches **`razor/tatara-masamune`** (see §6.2). `Karve SB w/ C-Plate` — both parts → Karve CB. |
| `with` / razor | 20/40 (50%) | `Karve CB with OC C plate` — both parts → Karve CB. `Wolfman WR1 with Gillette Platinum (1)` — `Gillette Platinum` → `razor/razorock-lupo` (token accident). |
| `vs` / razor | 18/29 (62%) | Real distinct razors — but **comparisons** (`Karve vs. Rockwell 6c`). The guard cannot see intent. |

Three failure modes, each needing its own guard clause (§5):

1. **Same-entry double resolution.** Plate/pass/knot fragments resolve
   to the same entry as the product part. Killed by distinctness (G2).
2. **Reverse-subset on short fragments.** A 2-token fragment resolves to
   an unrelated entry because its tokens sit inside some (often
   composite) alias. Killed by the ≥3-token floor on subset-rev (G3) —
   and the worked cases are in §6.2.
3. **The whole string is itself a product.** `Crystal Super + Platinum`,
   `Tallow + Steel`, `Barrister + Mann - Seville` all match whole. The
   split must never run on a string that is already a product. Killed by
   whole-string-first (G0).

### 4.2 Strict-guard results (G0–G6) — sampled rates and exact counts

Strict = splits into ≥2 non-junk parts, every part tier-1/2, all resolved
entries distinct, no <3-token subset-rev, no >80-char prose part, whole
string not itself a product. Sampled n = 40/field (all rows where pool
smaller). Exact = full-dataset count under the same guard.

| sep | field | pool | sampled strict | exact splits |
|---|---:|---:|---:|---:|
| `;` | razor | 632 | 2/40 | **9** |
| `;` | blade | 31 | 6/31 | **6** |
| `;` | aftershave | 2,211 | 6/40 | **372** |
| `;` | fragrance | 67 | 3/40 | **4** |
| `;` | soap | 76 | 0/40 | 1 (not enabled) |
| `;` | brush | 74 | 1/40 (false — `Hands`) | 4 (not enabled) |
| `+` | blade | 46 | 10/40 | **12** |
| `+` | aftershave | 3,781 | 8/40 | **958** |
| `+` | fragrance | 70 | 7/40 | **10** |
| `+` | soap | 1,293 | 8/40 | **94** |
| `+` | razor | 959 | 1/40 (false — head+handle) | — (excluded) |
| `+` | brush | 1,354 | 3/40 (all false — handle+knot) | — (excluded) |
| `/` | blade | 197 | 10/40 | **52** |
| `/` | aftershave | 867 | 8/40 | **141** |
| `/` | soap | 912 | 2/40 | **88** |
| `/` | razor | 2,406 | 1/40 (false) | — (excluded) |
| `/` | fragrance | 184 | 1/40 (false — wrong `Onyx`) | — (excluded) |
| `/` | brush | 4,986 | 3/40 (all false — handle/knot) | — (excluded) |
| `\|` | aftershave | 49,013 | 21/40 | **20,433** |
| `\|` | blade | 1,649 | 21/40 | **808** |
| `\|` | razor | 2,007 | 2/40 | **197** |
| `\|` | soap | 4,319 | 2/40 (1 genuine, 1 duplicate) | — (excluded) |
| `\|` | fragrance | 1,059 | 1/40 (duplicate) | — (excluded) |
| `\|` | brush | 1,699 | 0/40 | — (excluded) |
| `,` | aftershave | 10,931 | 9/40 (only ~5/9 clean — see §7.4) | — (excluded) |
| `,` | other fields | — | 0–3/40, all annotation/scent-list | — (excluded) |
| `then` | blade | 47 | 20/40 | **22** |
| `then` | razor | 78 | 3/40 | **7** |
| `then` | aftershave | 247 | 7/40 (messy prose routines) | — (excluded) |
| `then` | soap/frag/brush | 56/51/22 | 1/0/0 | — (excluded) |
| `&` | all fields | 54–10,391 | 0–6/40 | — (excluded) |
| `vs` | razor | 29 | 6/29 (comparisons) | — (excluded) |
| `w/` | all fields | 0–14,730 | 2–7/40 (additive/handle traps) | — (excluded) |
| `with` | all fields | 257–8,116 | 0–5/40 | — (excluded) |

**Totals under the recommended set: 22,943 rows (9.51%) would split**
(exact full-dataset count; per-cell counts sum to 23,213 because 270
rows split on two or more recommended separators). For scale: 58,649
rows (24.3%) contain at least one recommended separator in a recommended
field — the guard declines the other ~35,700 (safe misses).

### 4.3 Precision for `;` and `+` specifically (as requested)

**Semicolon.** Sampled strict rates are low because most `;` rows are
one product + annotations — but the splits that fire are clean. Manual
verification of every strict pass in the sampled cells: razor 2/2
genuine (`Pass 1: Feather SS; Pass 2, 3 - Rockwell 6s`; `Puma 5/8;
Rockwell 6c`), blade 4/4 shown genuine (`Voskhod (face); Ladas (head)`;
`Personna GEM PTFE; KAI Captain Titan Mild Protouch MG`), aftershave
mostly genuine (`Zingari Man - The Magician recovery splash; PAA - Tea
Party 508 balm`; `Snake Bite; Stirling Unscented Balm`), fragrance 3/3
genuine. The naive 78% razor rate collapses to 5% (2/40) once
distinctness is required — 29 of 40 sampled razor `;` rows are the
single Karve CB pattern, blocked by whole-string-first. Full-dataset
`;` splits: **391 rows** (372 aftershave, 9 razor, 6 blade, 4 fragrance).

**Plus.** The naive 90% blade rate is the Crystal trap: 25 of 40 sampled
blade `+` rows are whole-product matches (`Crystal Super + Platinum`),
blocked by G0. After G0, 10 of the remaining 14 sampled rows split
strictly; manual verification: 3 of 4 examined were genuine two-blade
joins (`Astra SP + Personna Twin Pivot Plus`; `Ted Pella Injector +
Feather Professional`; `Derby + PSI`), 1 was a cross-field paste
(`Rockwell 6S (R3) + Gillette 7 O'Clock Super Stainless` — a razor name
in the blade field, resolved to the Rockwell *blade* via the bare alias
`Rockwell`; ~2–3 such rows dataset-wide). Aftershave `+`: all 8 sampled
strict passes were genuine-sided splash+balm/serum joins, though 4 were
wyze0ne routine strings where each side is itself a comma-list (partial
splits — real attributions, under-counted, §6.4). Fragrance `+`: all 7
sampled strict passes genuine layering. Full-dataset `+` splits in
enabled fields: **1,074 rows** (958 aftershave, 94 soap, 12 blade,
10 fragrance).

## 5. The guard (G0–G6) — what the split needs, in order

Applied in order; a row that fails any clause stays whole (safe miss).

- **G0 — whole-string-first.** If the unsplit value (after unescape /
  strikethrough-strip / link-strip / URL-strip) exact- or
  normalized-matches a tier-1/2 entry, do not split. Kills `Crystal Super
  + Platinum`, `Tallow + Steel`, `Barrister + Mann – Leviathan`, collab
  names (`Chatillon Lux / Declaration Grooming - TSM Fougère`), and
  same-product-two-names (`Slim Twist / Knack`). **G0b:** also try with a
  trailing format word stripped (` - Aftershave`, ` - Soap`, ` - Splash`,
  ` - Balm`, …) — posters append the format word from trythatsoap link
  text, which breaks the exact match. (Caveat: G0b did *not* save the
  B&M scent-name comma case, §7.4.)
- **G1 — every non-junk part must resolve tier-1/2.** A part resolving
  only to the unverified tier does not count. (Unverified-tier hits are
  common for routine items — alum, Thayers variants, Nivea — and for
  cluster ids; counting them would inflate splits with weak evidence.)
- **G2 — all resolved entries distinct.** Kills plate/pass/knot
  fragments resolving to the same entry as the product part (§4.1,
  failure mode 1). Also correctly blocks same-model pairs the catalog
  treats as one entry (P-17): `Gillette Flare Tip, then Gillette 1940s
  Super Speed` — both parts → `razor/gillette-super-speed`.
- **G3 — subset-rev floor.** A part whose *only* resolution is
  reverse-subset must have ≥3 tokens. Kills 2-token annotation fragments
  (`B Plate`, `Silver Blue` → Tatara, `A plate` → Razorock Hawk). Cost:
  genuine short parts that only match via rev (`Osma Alum`, `Nivea balm`)
  are also blocked — accepted; they stay whole, which is the safe
  direction.
- **G4 — prose cap.** A part longer than 80 chars after cleaning cannot
  match. Kills long prose paragraphs that subset-match a blade name
  (Malthus's `/`-in-a-sentence case, §3.3).
- **G5 — routine-phrase junk.** Parts that are exactly a routine step are
  junk, not products: `cold water rinse`, `cold water splash`, `cold
  rinse`, `cold water`, `warm/hot water rinse`, `water rinse`, `rinse`,
  `leftover lather`, `extra lather`. (Without G5, `Cold water rinse`
  reverse-subset-matches Ghost Town Barber — §9. G5 turns those rows
  into correct partial splits: the routine part is dropped, the real
  products still count.)
- **G6 — additive-part junk.** A part matching `/frost drops?|terrorade/i`
  is an additive, not a product. Kills the systematic `+ Frost Drops`
  false split (`Stirling Frost Drops` → DG Unscented). 30 soap `+` rows
  carry these (26 Frost Drops, 4 Terrorade).

Preprocessing (before any splitting): HTML-unescape; strip `~~...~~`
strikethrough segments (a retraction, not a product); reduce markdown
links to their text; strip bare URLs (they contain `/` and `//`).

**Guard assessment.** The naive guard ("both parts match") is **not
sufficient** — §4.1 shows it passing false splits at 50–90% in the worst
cells. The strengthened guard G0–G6 is necessary, and on the verified
cells its strict passes are overwhelmingly genuine (the exceptions are
catalogued in §6.4 and §7.4). It is still not airtight: residual risks
are (a) cross-field pastes (razor name in the blade field, ~2–3 rows for
`+`/blade); (b) `vs`-style semantics, handled by excluding the separator
rather than by the guard; (c) alias pollution (§9) — a part can match
the *wrong* entry confidently when the alias corpus contains composite
strings; (d) partial splits of wyze0ne-style routine strings (real
attributions, under-counted). None of these is a reason to hold the
build; all are bounded (tens of rows, not thousands) except alias
pollution, which is a catalog-hygiene follow-up, not a split-design
problem.

## 6. How the guard's clauses were earned (worked false splits)

### 6.1 Same-entry (G2)

`Karve CB SS SB (D Plate, first pass; B Plate, second pass)` — parts
`Karve CB SS SB (D Plate, first pass` and `B Plate, second pass)` both
resolve to `razor/karve-christopher-bradley`. Without G2, the naive
guard counts this as a successful two-razor split 31 times in a 40-row
sample. Same pattern for `Karve CB with OC C plate`, `Karve SB w/
C-Plate`, and pipe duplicates (`Gillette Red-Tip | Gillette Blue-Tip`
→ both `razor/gillette-super-speed`).

### 6.2 Reverse-subset on short fragments (G3)

- `Rockwell 6S (6) w/ Silver Blue` — `Silver Blue` → **`razor/tatara-
  masamune`** (subset-rev). Mechanism: some poster's razor field was
  `Tatara Masamune - Gillette Silver Blue (1)`, harvested verbatim as an
  alias on the Tatara entry; the 2-token fragment's tokens sit inside
  that alias.
- `Karve Christopher Bradley w/ A plate` — `A plate` → **`razor/
  razorock-hawk`** (subset-rev; the Hawk has A plates).
- `B Plate, Second Pass` → Karve CB (subset-rev; also same-entry).
- `OC C plate` → Karve CB (subset-rev; also same-entry).

### 6.3 Whole-string-is-a-product (G0)

- `Crystal Super + Platinum` → whole matches `DE/crystal-super-plus`
  (normalized). Split would produce `DE/crystal-super-plus` +
  `DE/gillette-platinum` — two wrong attributions for one blade.
- `Tallow + Steel - Madagascar`, `Barrister + Mann – Leviathan`,
  `London Razors + Summer Break Soaps - Mountain Laurel - Eau de Parfum`
  — all whole-matched (25/40 sampled blade `+` rows, 24–25/40 soap `+`
  rows were whole-matches).
- `Stirling - I, Rich Moose AS; Nivea balm` — whole-matched via a
  composite alias; this one is a *false negative* (the string really is
  two products) caused by the same alias pollution — safe direction, but
  see §9.

### 6.4 Partial splits (accepted)

wyze0ne's aftershave routine strings, e.g. `Osma alum, Thayers Rose
Petal toner, Declaration Grooming *Revenant* aftershave + Zingari Man
Rescue Potion, Zingari Man *The Stargazer* aftershave serum` — the `+`
split yields parts that each contain several products; each side matches
one entry (Thayers Rose Petal; Stargazer serum) and the rest are dropped.
The split attributes only products that are actually in the string, so
it is a net improvement over the status quo (0 attributions), but it
under-counts. Splitting on `,` as well would complete these — and is
rejected for the reasons in §7.4.

## 7. Tricky patterns, explicitly

### 7.1 "Touchup" / "2nd pass" / "also used" annotations

The second item is usually **not** a second product. `Merkur Futur
first pass 1, then 1.5, then 2` (one razor, settings); `Rockwell 6S R3
then R5` (one razor, plates); `Gillette Slim (5, 6, then 7)` (one
razor, settings); `Polsilver (8) | Pol holding up nicely. 2 pass +
touchup for BBS today` (prose). Genuine exceptions are labelled by
pass/zone: `Voskhod (face); Ladas (head)` (two blades, head/face);
`Pass 1: Feather SS; Pass 2, 3 - Rockwell 6s` (two razors, by pass);
`H: Schick Grip / F: Universal Shavette` (two razors, head/face). The
guard handles both cases: setting-change rows whole-match or fail
distinctness; labelled pairs pass strictly. Annotation fragments
(`(N)`, `(2)`, `first pass`, `touchup`, `cleanup`) are in the junk list
(G5/G1 preprocessing).

### 7.2 Parenthetical second items

Parentheses are annotations, never a second product (§3.9). The one
apparent exception — `(H) X / (F) Y` — is a `/` join with parenthetical
*labels*, and the guard treats the labels as part of the product part
(`(H) Barrister and Mann Promises` resolves via subset).

### 7.3 `w/` constructions

Three distinct meanings, all one product except the rare genuine case:
(1) handle-with-knot in brush (canonical, 14,730 rows); (2) head+plate/
handle or razor+blade in razor; (3) **additives in soap** (`w/ frost
drops`, `w/ Terrorade`, `with Permafrost`, `w/ 6+ drops Terrorade`) —
one soap plus menthol drops, not two soaps. Genuine two-soap `w/` exists
(`TOBS Grapefruit shaving cream w/Williams Mug shaving soap`) but is
rare and not separable from the additive pattern by any guard, so `w/`
is excluded. The additive names are instead excluded as *parts* (G6)
for the `+` separator, where genuine two-soap joins are common enough
to keep.

### 7.4 Commas inside scent lists — why `,` is excluded anyway

The comma case was the closest call. Comma-joined routine lists in
aftershave are real and common (§3.5). But full verification of all 11
strict passes in the aftershave sample found only ~5 clean:

- **Scent-name commas (systematic).** `Barrister and Mann - Lime,
  Lavender, and Cedarwood - Aftershave` splits into `Barrister and Mann
  - Lime` → B&M Lime, `Lavender` → B&M Lavender, `and Cedarwood -
  Aftershave` → `Captain Nemo's Castillo` (subset-rev token accident).
  One scent, three wrong attributions. G0/G0b do not block it: the whole
  string does not exact-match any entry (the scent entry apparently
  lacks that exact alias), and `Lime`/`Lavender` are themselves real
  B&M scents.
- **Product names containing commas.** `Stirling - I, Rich Moose` and
  `Barrister and Mann - O, DELIGHT!` — a comma-split cuts a product
  name in half. (`Sir Irisch Moos - Sir Irisch Moos Aftershave |
  Stirling Soap Co. - I, Rich Moose Balm | …` — the comma inside `I,
  Rich Moose` mis-splits a pipe-joined 3-product string.)
- **Alias pollution.** `Thayer's Facial Toner, Lily of the Desert Aloe
  Vera Gelly` — `Lily of the Desert Aloe Vera Gelly` (a real but
  uncatalogued product) reverse-subset-matches the Dickinson's witch
  hazel entry via a composite alias.
- **Routine phrases.** `Cold water rinse, …` / `Cold water splash, …`
  (3 rows) — G5 now junks these, and the remaining parts still split
  correctly; but the other failure modes above are not fixable by a
  junk list.
- **Joke entries.** `Leftover lather, L&L Mayflower splash` — `Leftover
  lather` is an attested catalog entry (§9) for a joke string; G5 junks
  it now.

Net: ~5/9 clean in the verified sample, with the failures systematic
rather than random. The genuine comma yield (~1,250 splits dataset-wide
under the guard) is not worth ~40% false splits. **Exclude `,`.** The
cost is that genuine aftershave routine lists stay whole (status quo) —
they are largely recoverable anyway through their `|`/`+` siblings in
the same strings.

### 7.5 Slashes in sizes and names; `x` in dimensions

`6/8`, `1/2`, `5/8"` (razor sizes), `62mm x 16mm`, `24mm x 51mm`
(dimensions), `Gillette x Wilkinson Sword` (one blade), `Catie's
Bubbles - X` (a product named X), `VS Finest` (a knot grade, not `vs`).
The spaced-`/` and spaced-`x` predicates already exclude most of these
(sizes are unspaced); the junk list catches bare size parts (`6/8`).
`6/8` as a *part* after a spaced-`/` split is junked by the size rule.

## 8. Recommended separator set

**Per-field table** — a separator is enabled only in the listed fields.
Anything not listed is excluded. The guard G0–G6 applies everywhere
below.

| separator | razor | blade | soap | aftershave | fragrance | brush |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `;` | ✓ | ✓ | — | ✓ | ✓ | — |
| `\|` | ✓ | ✓ | — | ✓ | — | — |
| ` / ` | — | ✓ | ✓ | ✓ | — | — |
| ` + ` | — | ✓ | ✓ | ✓ | ✓ | — |
| ` then ` | ✓ | ✓ | — | — | — | — |
| `,` | — | — | — | — | — | — |

Exact full-dataset splits under this set + G0–G6: **22,943 rows (9.51%)**
— `|`/aftershave 20,433; `|`/blade 808; `+`/aftershave 958; `;`/
aftershave 372; `|`/razor 197; `/`/aftershave 141; `+`/soap 94;
`/`/soap 88; `/`/blade 52; `then`/blade 22; `+`/blade 12;
`+`/fragrance 10; `;`/razor 9; `then`/razor 7; `;`/blade 6;
`;`/fragrance 4.

### Excluded, with reasons

| separator | reason |
|---|---|
| `,` (all fields) | §7.4: scent-name commas, product names containing commas, alias pollution; only ~5/9 clean strict passes in aftershave. |
| ` and `, ` & ` | Brand names (`Barrister and Mann`, `Chisel and Hound`, `Wade and Butcher`, `Morris & Forndran`); genuine joins rare and mostly phrased as comparisons/tests, not clean joins. |
| `w/`, `with` | Handle+knot (brush), head+plate/handle (razor), additives (soap), one-product menthol variants (aftershave). The strict passes are mostly additive/handle traps. |
| `vs` | Comparisons, not uses — the guard passes them (6/29 razor) and no guard can tell a comparison from a two-product shave. |
| `x` | Head×handle / collab = one product; counts/dimensions in blade; soap mash-ups too rare and too confounded by collabs. |
| em/en dash, ` - `, `:` | Brand–product / label separators, never joins. (` - ` is *the* brand–product delimiter: 368,611 rows.) |
| parens | Annotations only (counts, settings, materials, dates, sizes, links). |
| `~` | Strikethrough corrections — strip `~~...~~` before matching; never split on it. |
| `//`, newline | URLs only (149,925 rows); newlines do not occur (0 rows). |
| `;` in soap, brush | ~Zero yield (exact: 1 and 4 rows); brush's only sampled strict pass was the `Hands` joke. |
| `\|` in soap, fragrance, brush | Duplicates (`Vide Poche` listed twice; `Tabac Original` + hashtag repeat) and handle/knot; soap's genuine yield is ~1 in 2. |
| `/` in razor, fragrance, brush | Head/plate/handle (razor), collabs (fragrance), handle/knot (brush); every sampled strict pass in these cells was false. |
| `+` in razor, brush | Head+handle / handle+knot = one product; every sampled strict pass false. |
| `then` in aftershave, soap, fragrance, brush | Aftershave `then` lives inside prose routines (only ~2/7 sampled strict passes clean); soap/fragrance/brush are prose or ~zero. |

### Notes on the enabled cells with small yields

- `;`/razor (9 rows), `;`/blade (6), `;`/fragrance (4), `then`/razor
  (7), `then`/blade (22), `+`/blade (12), `+`/fragrance (10): tiny
  pools, but every sampled strict pass examined was genuine, and the
  guard (not the pool size) is doing the filtering. Keep them enabled —
  the cost of enabling is zero false splits in the samples, and the
  alternative (excluding) loses real two-product rows like `Voskhod
  (face); Ladas (head)`.
- `+`/soap (94 rows): enabled *with* the G6 additive exclusion. Without
  G6 the Frost Drops trap fires; with it the examined strict passes were
  genuine two-soap joins (`Dr. Jon's - Classic - Soap + CFG Cryogen`).

## 9. Follow-ups surfaced by the analysis (not part of the split design)

1. **Composite aliases poison reverse-subset matching.** Posters' whole
   multi-product field strings have been harvested as aliases (e.g.
   `"Cold" Water Rinse | Chiseled Face Ghost Town Barber Aftershave
   Splash` on the Ghost Town Barber entry; `Tatara Masamune - Gillette
   Silver Blue (1)` on the Tatara entry; `Rockwell 6S (R3) + …`-style
   strings). Their token sets swallow routine phrases and fragments:
   `Cold water rinse` → Ghost Town Barber, `Silver Blue` → Tatara
   Masamune, `A plate` → Razorock Hawk. This affects ordinary matching
   too, not just splitting — a whole field value of `Cold water rinse`
   would match Ghost Town Barber today. Recommendation: alias hygiene
   pass — do not harvest aliases from strings containing `|`, `;`, or
   ` + `, and consider dropping existing aliases that contain them (or
   at least the routine-phrase tokens). Also the reverse direction:
   composite aliases cause false *whole*-blocks (`Stirling - I, Rich
   Moose AS; Nivea balm` whole-matched a Rich Moose entry).
2. **`unverified/aftershave/leftover-lather` is attested but is not a
   product.** "Leftover lather" is a joke/note (28 aftershave rows). It
   should be reviewed for `not_a_product` (or at least demoted) — as it
   stands it lets a routine phrase count as a product match. Same
   question applies to other `unverified/…` ids carrying `attested`
   status (e.g. `unverified/blade/7am-plus-hi-platinum-durablade`,
   `unverified/blade/zorrik`) — those two look legitimate (real
   products, stale cluster ids), so this is a case-by-case review, not
   a blanket rule.
3. **Bare-brand subset matching lets cross-field pastes through.**
   `Rockwell 6S (R3)` in the blade field resolves to the Rockwell
   *blade* via the bare alias `Rockwell`. This is pre-existing matcher
   behaviour, not something the split introduces; the split only
   surfaces it. A cross-index check (a part that matches an entry in a
   *different* field's index at equal strength should not split) would
   kill the residual ~2–3 rows, but it is optional polish, not required
   for shipping.
4. **The `H:`/`F:` and `Pass N:` labels** (`H: Schick Grip / F:
   Universal Shavette`; `Pass 1: Feather SS; Pass 2, 3 - Rockwell 6s`)
   are a small, clean, genuine two-product signal that the current
   design does not exploit. If a later pass wants more razor yield,
   splitting on the labelled pattern is nearly free of false positives —
   but the pool is tiny (a handful of rows), so it is not worth
   delaying the build for.

## 10. Recommendation (stated plainly)

**Ship the P-25 split with the per-field separator table in §8 and the
strengthened guard G0–G6 in §5 — and do not ship it with the naive
"both parts must match" guard alone, which I have shown produces false
splits at 50–90% in the worst cells.**

Concretely: split on `;` (razor, blade, aftershave, fragrance), `|`
(aftershave, blade, razor), ` / ` (blade, aftershave, soap), ` + `
(blade, aftershave, fragrance, soap), and ` then ` (blade, razor) —
each half counting as one use, dataset rows untouched — **only** when:
the whole string is not itself a product (G0, incl. trailing format-word
strip); every part resolves tier-1/2; all resolved entries are distinct;
no part resolves only by reverse-subset on fewer than 3 tokens; no part
is longer than 80 chars; routine phrases and menthol-drop additives are
treated as junk, not products. Strip `~~...~~` strikethrough segments,
markdown links, and bare URLs before splitting. Exclude `,` entirely,
exclude ` and ` / ` & ` / `w/` / `with` / `vs` / `x` / em-dash / ` - ` /
`:` / parens, and do not enable any separator in brush (the brush field
is handle+knot constructions throughout — every sampled strict pass
there was a false split of one brush into two).

Expected effect on the full dataset: **22,943 rows (9.5%) split**,
dominated by `|` in aftershave (20,433 rows). The remaining ~35,700 rows
that contain a recommended separator but fail the guard stay whole —
that is the safe direction, and the largest single cause of declines is
parts that do not resolve (routine items like Thayers, alum, and generic
balms that lack strong standalone entries), not guard over-strictness.

Before shipping, run the A/B verification from the held design (match
before/after on a sample, diff resolutions) — and include in the diff a
check of the §6 worked cases (`Crystal Super + Platinum` must stay one
blade; the Karve `D Plate; B Plate` string must stay one razor;
`Tallow + Steel` must stay one soap).

## Appendix: reproducibility

- Scripts (scratch, `/tmp`): `sep_count.py` (census), `sep_sample.py`
  (samples, seed 20261116 → `samples.txt`, 2,623 lines, all read;
  `long_strings.txt`, 200 longest strings, read in full),
  `precision_test.py` (naive guard, seed 20261117),
  `precision_strict.py` (distinct + rev-floor),
  `precision_full_guard.py` (G0–G6; final table + full-dataset
  estimate), `verify_cells.py` (all strict passes for undecided cells,
  same seed/samples).
- Results: `/tmp/precision_results.json`,
  `/tmp/precision_strict.json`, `/tmp/precision_full_guard.json`,
  `/tmp/draft_estimate.json`.
- The precision test imports `match_all.py` read-only and calls its
  `match_field` / `match_brush` over the indexes built from
  `catalog_merged.json`. It does not apply P-15 loose aliases or P-14
  format resolution, so parts like bare `Astra` under-resolve; that
  biases strict rates downward (safe direction).
- Sample sizes: 40 rows per separator per field (seed 20261117) for the
  precision test; 25 rows per separator per field (seed 20261116) for
  manual classification. Pools smaller than the sample size were sampled
  in full (`;`/blade n=31, `vs`/razor n=29, `then`/brush n=22, etc.).
