# Unverified tier + standing validation — policy and procedure

Approved by the user 2026-10-20 (tier policy + bidirectional set
cross-validation rule). This document is the contract for the unverified
tier and for every future validation run. Follow it exactly.

The standing validator runs as cron `sotd-catalog-validator`
(every 30 min, batch of 12 items) and follows this procedure.

**Trusted sources:** `~/workspace/sotd/knowledge/trusted_sources.md` is the
first-check list for research (Maggard first for attribution). Store product
pages from listed retailers count as primary evidence.

**Knowledge base first (user ruling 2026-11-07):** before researching an
item, check `~/workspace/sotd/knowledge/` — `lineages.md`,
`product_aliases.md`, `glossary.md`, `people.md`, `product_lines.md`,
`hardware_lore.md`, `world_notes.md`. A fact tagged **established** with its
source counts as the evidence basis: cite the learner's source on the entry
(with file and line) and do NOT independently re-confirm it. A fact tagged
**lead** is pointer-only, never evidence. If the knowledge base is silent on
the item, research normally.

**Precedents:** `catalog/precedents.md` is the registry of user rulings and the
precedents they establish. Precedents bind validation and merge opinions: before
recommending or applying any merge, split, alias, or attribution, check the
registry for a governing precedent and follow it (or flag the deviation and the
evidence that justifies it). New user rulings are added to the registry with their
precedent links; an overturned precedent queues its dependent decisions for
re-review.

## Storage (SQLite — since 2026-10-21)

**`catalog/catalog.db` (SQLite) is the single source of truth** for
catalog entries, the validation queue, candidate aliases, and the brand
registry. It replaced the JSON files as the write store: writes are
transactional and crash-safe (WAL mode, 60s busy timeout), so concurrent
agents no longer contend over whole-file rewrites or advisory locks for
data safety.

- **All writes go through `catalog/sotd_db.py`** — `connect()`,
  `upsert_entry()`, `delete_entry()`, `update_queue()`, `upsert_brand()`,
  `counts()`. Never write the tables with ad-hoc SQL, and never edit the
  JSON files directly.
- **`catalog_merged/` (7 per-category shards), `validation_queue.json`,
  `candidate_aliases.json`, and `brands.json` are read-only EXPORTS**
  regenerated from the DB by `sotd_db.export_json()`. Readers (the
  matcher `match_all.py`, reports, humans) read the exports; after any
  write batch, re-run `export_json()` so the exports stay current.
- Entry `status` is an **open set**, not an enum. The status taxonomy
  (user rulings, 2026-10-20; definitions in
  `~/memory/groups/r-wetshaving.md`, "Status taxonomy"): **unverified**
  (raw-string cluster, nothing established) → **attested** (existence
  established by 3+ distinct-author SOTD posts; name not confirmed) /
  **corroborated** (identity resolved by the nmrs external catalog) →
  **verified** (primary evidence per the standing standard); plus
  **needs-review**, the hold state for items awaiting joint review.
  Status = strongest basis held; corroborated/attested never auto-promote
  to verified. Entry data is stored as full JSON, so new fields (e.g. a
  `corroboration` record `{source, type, target, upstream_commit}`)
  round-trip untouched.
- The `.catalog.lock` discipline in the procedure below still applies to
  multi-step write passes (it serializes agent workflows, e.g. a batch
  that reads the queue then writes many entries); the DB's own
  transactions handle row-level safety underneath it.
- Migration record: `catalog/migration_status.md`; pre-migration JSON
  snapshots live in `catalog/pre-sqlite-backup-*/`.

## The tiers

`catalog_merged/` (7 per-category shards) holds three tiers of entries:

1. **verified** — settled on PRIMARY evidence (see standard below).
2. **needs-review** — high-attestation or otherwise important items held for
   joint review with the user. Never created by the validator.
3. **unverified** — one entry per unmatched product cluster from the matched
   datasets. These are *attested strings*, not confirmed products. They exist
   so the matcher can resolve posts to a stable id and so validation has a
   worklist. Never present an unverified entry as a confirmed product.

Coverage is always reported by tier (see `coverage_report.md`; **P-13**,
user ruling 2026-10-21): **tier-1 %** = resolved to verified/needs-review;
**tier-2 %** = resolved to attested/corroborated; **addressable %** =
tier-1 + tier-2 + resolved to unverified. Never quote a single blended
number. The matcher (`match_all.py`) indexes **every** tier with resolution
precedence tier-1 > tier-2 > unverified — a hit *or* an ambiguity at a tier
is final, a clean miss falls through — and every stored match records its
tier (tier-2 hits carry match method `tier-2`, unverified hits method
`unverified`). A product must never disappear from usage/coverage reports
because its evidence improved: before P-13 the ~7,800 attested/corroborated
entries resolved zero posts because the matcher only indexed the
verified/needs-review and unverified tiers.

**Format agreement (P-14, user ruling 2026-10-21).** Blade and format
must agree within a post. The matcher applies a format pass per post,
inside the certain match (after the context-free three-tier match of
the blade and razor strings, before the loose/author-scoped
post-passes):

- A blade match that is ambiguous across formats is narrowed to the
  candidate(s) whose format equals the format of the razor matched in
  the same post; symmetrically, a cross-format razor ambiguity is
  narrowed by the post's blade format. Such resolutions carry method
  suffix `+razor-format` / `+blade-format`.
- A bare brand string — just the brand (optionally + "blade(s)") for
  a brand with formatted entries in more than one format, e.g. "Kai",
  "Personna", "Schick" — is never blanket-resolved by alias: the
  paired razor's format selects the format first, then the P-07
  popularity default picks within that format (the entry holding the
  bare string as an alias, else the format-generic product such as
  Personna "Injector Blades", else a single candidate in the format,
  else a dominant footprint: ≥10 aliases+clusters and ≥3× the
  runner-up). With no razor signal, the context-free result stands —
  P-14 runs *before* P-07, which applies only when the pairing gives
  no signal. Bare "Personna" with a DE razor stays on the unresolved
  bare cluster by design (§B3): the format agrees but the product is
  undecidable among coequal DE Personnas.
- Razor format = the razor entry's `type` when it names a blade
  format (DE / AC / GEM / Injector / Cartridge / FHS / Half-DE /
  Hair Shaper / Durham Duplex; "Shavette" / "Straight" / "SE" give no signal — a
  shavette may take several formats), else a format derived in a
  pre-pass from the same run's unambiguous razor↔specific-blade
  pairings (≥3 posts, ≥90% one format; bare-brand strings and
  "Unspecified" clusters are excluded from derivation so they cannot
  poison it — this is how the Weck Sextoblade earns Hair Shaper).
- Per-year P-14 resolution counts are printed in `coverage_report.md`.
- **Hard constraint (user ruling 2026-10-21): no default resolves
  against the paired format.** The narrowing above governs
  ambiguities; this constraint governs *hits*. A default hit is
  voided when the entry it lands on is in a different format from the
  razor (for blades) or blade (for razors) matched in the same post.
  "Default" means: a P-15 loose pick; a bare-brand string's hit; or a
  hit whose only identification basis is the bare-brand alias — a
  "bare-decisive" subset capture (e.g. "Kai Captain Sharpblade"
  landing on `DE/kai-stainless` through its bare "Kai" record, which
  shadowed the attested AC Sharpblade entry at the tier below).
  Certain evidence-based matches are never voided. Fallback order
  after a void: (1) a format-scoped loose alias (below); (2) the
  certain match recomputed within the paired format — a hit, or an
  ambiguity inside that format; (3) an ambiguity among the brand's
  entries in that format (a single such entry resolves as a hit);
  (4) unresolved. A bare-decisive context-free hit also yields to a
  specific identification of the same string at a lower tier even
  before any format check — the bare record is the weakest
  identification in the system — but a lower-tier bare capture (a hit
  or an ambiguity resting solely on bare records) does not count as
  specific. The named violation this closes: bare "Feather" in an
  AC-razor post, which used to default to `DE/feather-hi-stainless`;
  it now resolves through the format-scoped loose alias on
  `AC/feather-artist-club-professional-pb-20` (basis_share 0.559:
  Professional 2,400 of 4,293 identified Feather AC uses 2016–2026;
  Jatai, Feather's US distributor, calls the Professional "the
  standard go-to blade" and the ProGuard "the second most popular").
  Per-year void counts are printed in `coverage_report.md` ("P-14
  hard filter" line; first full run: 388 blade voids, 3 razor voids).

**Loose aliases (P-15, user ruling 2026-10-21).** An entry may carry a
`loose_aliases` list, separate from its certain `aliases`. Each record is
`{alias, basis_share, basis, precedent, date}`: it declares that an
otherwise ambiguous string probabilistically defaults to the entry that
carries the record, and `basis_share` records the entry's share among
identified uses of the family (the computation belongs in `basis`). The
matcher applies a loose alias to its exact string unless an explicit
exact/normalized certain alias uniquely identifies that same string; a
loose alias takes precedence over subset/reverse-subset inference (so
"Shark (Egypt)" is not captured by the bare "Shark" cluster's subset
hit), over ambiguities, and over clean misses. A loose
resolution is stored as `{id, method: "loose-alias", tier: <target tier>,
probabilistic: true, loose_alias, basis_share}`. Coverage reporting puts
these in a distinct **probable** column/% sub-line: they count toward
addressable, but never toward the certain tier-1, tier-2, or unverified
counts. Never put a loose string in `aliases` (that would silently make
it certain), and never use a loose alias to settle whether a distinct
product exists — identity disputes stay unresolved under P-11. A
record may carry `format_context` (e.g. `"AC"`): it is then scoped to
posts whose paired razor/blade format equals that context, is excluded
from the context-free loose index, and is applied only by the P-14
hard filter above (fallback step 1).

**Author-scoped aliases (§B4, user ruling 2026-10-21).** An entry may
carry an `author_scoped_aliases` list, separate from both `aliases` and
`loose_aliases`. Each record is `{alias, author, basis}`: it declares
that ONE named author's use of an otherwise ambiguous string is
*documentary-proven* to mean the entry carrying the record — the proof
(the author's own string history, a verbatim note, a use-counter
continuation) is written out in `basis`. The matcher applies scoped
rules per post, after the certain three-tier match and the P-14
format pass: a rule fires only for posts whose `author` matches the
record (case-insensitive) and only when the certain result is an
ambiguity or a clean miss — it never overrides a certain hit. A scoped
resolution is stored as `{id, method: "author-scoped", tier: <target
tier>, author_alias, scoped_author}` and counts in its certain tier (the
proof is documentary, not probabilistic, so it is NOT a P-15 loose
alias). Every other author's use of the same string is untouched.
First application: bare "Gillette Blue" resolves to
`DE/gillette-silver-blue` for SirKravsALot (146 posts; his string
evolved from his transposed "Gillette Blue Silver" in the same razor,
shortening on 2024-06-06) and Sleezey-Sleeze (7 posts; run continues as
"GSB" with a verbatim note) — and stays ambiguous for all other authors,
per the P-15 boundary (a conspicuously omitted discriminator is signal).

## Blade format taxonomy

Blade formats are the primary field, taken from the blade itself (maker
spec / product identity), never from the paired razor. Current taxonomy:
**DE / GEM / AC / Injector / Half-DE / Hair Shaper / FHS / Cartridge /
A77 / Durham Duplex**. The taxonomy is extensible — flag unknown formats,
never force a fit. **Durham Duplex** was added 2026-10-21 (discuss §D,
user ruling): the proprietary long blade (patented 1907) for the Durham
Duplex / Demonstrator / Domino razors; NOS only. Its settled entry is
`Durham Duplex/durham-duplex` (needs-review). A forum report that
Personna's pathology blade is an exact modern match for the format is
recorded on that entry as an UNVERIFIED note — it never justifies
aliasing a Personna entry into this format.

## How the tier was built (build_unverified.py)

- Source: `matched_{2022,2024,2025,2026}.json` (in `~/workspace/sotd/`).
  Unmatched = the field's match is null (or brush kind `unmatched`).
  Ambiguous resolutions are excluded — they are not clusters.
- Clusters group by `(field, N(raw))` using `match_all.py`'s normalization
  `N()`. Each cluster records raw_strings, uses, distinct_authors, years,
  and up to 3 example post refs `{thread_id, thread_date, author}`.
- Exclusions (never become entries): documented non-products and parser
  artifacts from the discuss files — "none"-type markers, `|`-joined
  composite leftovers, wedge/steel dimension strings, the Oct "no brush"
  jokes, generic witch-hazel strings, and the individually documented
  exclusions listed in build_unverified.py. When new datasets land
  (2021, 2023, backfill years), re-run the builder with the same exclusion
  lists and extend them only with documented evidence.
- **Fuzzy pre-check** before an entry is created: token-set Jaccard
  similarity of the cluster against every same-category verified/needs-review
  entry's alias token sets and its canonical brand+product set. Aliases that
  are just the brand name alone are excluded from comparison.
  - similarity **≥ 0.75** → **candidate alias**: parked in
    `candidate_aliases.json`, NOT a catalog entry.
  - **0.55 ≤ similarity < 0.75** → unverified entry, with
    `nearest_verified {id, similarity}` recorded in `match_notes`.
  - below 0.55 → plain unverified entry.
- Unverified entry schema: `id: "unverified/<category>/<slug>"` (slug from
  the most common raw string, `-2`/`-3` on collision), `category`,
  `brand: null`, `product: null`, `label` = most common raw string,
  `status: "unverified"`, `aliases` = raw_strings,
  `attestation {uses, distinct_authors, years, examples}`,
  `match_notes`, `evidence: []`, `decisions: []`, plus `set_key` /
  `set_siblings` for scent categories (below).

## Sets and BIDIRECTIONAL set cross-validation (user rule, 2026-10-20)

Soap, aftershave and fragrance products from the same maker with the same
scent form a **set**. Cross-validation is **bidirectional**: validating ANY
member of a set on primary evidence validates every unverified sibling —
direction does not matter (a verified aftershave unlocks the soap just as a
verified soap unlocks the aftershave).

- **`set_key`** = normalized `maker/scent`: for verified/needs-review
  entries, maker = the entry's brand, scent = its product with form words
  stripped. For unverified entries, maker = the longest known-brand prefix
  of the normalized label (brand lexicon = brands of tier-1 scent entries);
  if no brand matches, the maker part is empty and the key is the whole
  form-stripped string — identical strings across categories still link.
  Form words stripped from the scent part: soap, shaving, shave, aftershave,
  splash, balm, toner, edt, edp, eau de parfum/toilette, cologne, fragrance,
  perfume, lotion, etc.
- Every soap/aftershave/fragrance entry carries `set_key` and
  `set_siblings` (ids of the other entries sharing the key). Every queue
  item and candidate-alias record in those categories carries `set_key` too.
- **Sibling sweep on any validation:** whenever a set member is promoted on
  primary evidence — by research, or because it was already verified when
  set keys were computed — immediately promote ALL unverified siblings
  sharing the `set_key`, in the same pass, without consuming separate
  research slots. Cross-validated entries get:
  - proper id `<Category>/<brand>-<product>` (slug taken from the validated
    sibling's id, brand/product copied from it);
  - evidence `[{type: "set-cross-validation", sibling: <validated entry
    id>, url: <that sibling's primary-evidence URL>, shows: …}]`;
  - `decisions` noting the promotion, the sibling, and the date.
- **Form-variant collapse:** raw clusters often split one product by form
  words ("Bay Rum" / "Bay Rum Aftershave" / "Bay Rum Balm" / "Bay Rum
  Splash"). Siblings sharing `set_key` AND category collapse into ONE
  promoted entry per category — fold all clusters' aliases in, mark every
  folded cluster's queue item `promoted` to the same id. Attestation:
  uses summed, distinct_authors = max of the clusters (author sets are not
  unioned), noted in `match_notes`.
- **Same-category form variants of an already-verified entry** (e.g.
  "…Steady Shaving Soap" vs the verified "…Steady") are proven duplicates:
  fold aliases into the verified entry, mark the queue item `merged`.
- Sets apply only within soap/aftershave/fragrance. Blades, razors and
  brushes have no sets.

First application (2026-10-20): the sweep promoted **190 entries from 566
clusters** (104 soap→aftershave, 69 soap→fragrance, 15 aftershave→fragrance,
1 fragrance→aftershave, 1 aftershave→soap) and merged 2 form-variant Steady
clusters into the verified soap. See `validation_progress.md`.

## The queue (validation_queue.json)

One ordered worklist covering every unverified entry AND every
candidate-alias cluster.

Item: `{queue_id ("Q000001"…), kind: "unverified"|"candidate_alias",
ref (unverified entry id, or integer index into candidate_aliases.json),
proposed_entry_id (candidate aliases only), set_key (scent categories),
seq, state, attempts: []}`.

- **`queue_id` is a permanent id** assigned at build time; it never changes,
  so logs can cite it forever.
- **`seq` is the current work order.** Process pending items in `seq` order.
- **Hint order** (user decision, 2026-10-27 — re-ordered by nmrs hint
  strength first, superseding the 2026-10-20 block order for sequencing;
  the set-unlock rationale survives structurally because soap items dominate
  the early tiers, and set cross-validation still resolves siblings whenever
  a soap verifies, regardless of position). Pending items run in this order,
  from `catalog/nmrs_backlog_results.json` tiers (script
  `catalog/nmrs_reorder_queue.py`; old order backed up to
  `catalog/queue_order_backup_2026-10-27.json`):
  1. **cm-rx-agree** — both nmrs layers agree; cheapest confirmations.
  2. **cm-only** — correct_matches hit, regex silent (CM is strongest).
  3. **rx-only clean** — exactly one distinct regex product.
  4. **sibling-hint** — aftershave/fragrance via a soap sibling's signal.
  5. **cm-vs-rx-DISAGREE** — adjudication (CM usually wins, needs judgment).
  6. **rx-only ambiguous** — 2+ distinct regex products; disambiguate first.
  7. **no-signal** — full research, no lead.
  8. **untestable-direct** — aftershave/fragrance with no nmrs signal and no
     sibling signal (passive set-unlock path may still resolve them).
  9. **candidate_alias items** — original relative order preserved.
  Within a tier, items batch by **brand_group** (one wake works one maker:
  research the maker once, verdict its whole set), then distinct_authors
  desc, then uses desc. The old 2026-10-20 block order (soaps, then
  aftershave/fragrance, then blade/razor/brush, each by authors desc) is
  retired for sequencing; attestation still orders work within a
  maker batch, it never gates it.
- States: `pending` → `promoted` | `merged` | `not_a_product` |
  `rejected_alias` (candidate alias proven wrong → cluster becomes a normal
  unverified entry). `promoted_to` / `merged_into` record the destination id.
  Items resolved by set cross-validation are marked in the same pass and
  **do not count against the batch size** — a batch of 12 means 12 items
  that needed research.
- **Escalation queue (user design, 2026-10-30):** the primary queue is
  the workers' worklist; items blocked on parent-only work (live-browser
  checks, user decisions) escalate to state `awaiting_parent` — the
  escalation queue. Fields: `parent_need` (the crisp
  ask: what check, where, what evidence would settle it), `parent_kind`
  (`browser` | `decision`). `next_queue` only takes `pending`, so workers
  never stall behind the escalation queue; the hook's poll loop counts
  `awaiting_parent` toward "drained" but never wakes a worker for it.
  Move an item to the escalation queue ONLY when your own angles are exhausted
  (≥2 real research attempts, or an explicit dead end like 403-blocked
  fetches with no alternative source) AND the remaining step is parent-only.
  Record the dead ends in `attempts` and write a specific `parent_need` —
  never "looks hard". If an item is bounced back to `pending`, that
  means the worker could have done it: do the work, don't re-queue it.
  Escalated items return to `pending` (with findings attached) or are resolved
  directly; decision-kind items come back with the user's ruling — or the
  worker's own, under the guard below.
  **Decision-kind guard (user ruling, 2026-10-31, scope corrected same evening).**
  The standing confidence rule governs decision-kind items too: at 100%
  confidence a worker DECIDES AUTONOMOUSLY and applies the verdict — the user
  was explicit about this. The decision is recorded as the worker's OWN
  decision (decisions entry: evidence, date, and the worker's role), never as
  "User ruled: …" or "user-approved". The offense was pre-writing the USER's
  ruling before it existed (Cerberus 2026-10-30, Dr. Bronner's 2026-10-31 —
  matching the eventual outcome does not make it acceptable); making your own
  call at 100% is not an offense, it is the rule. When confidence is anything
  less than 100%, the item is the user's alone: NO worker touches its row —
  no state change, no note, no annotation, no verdict language — and the only
  allowed move is escalating the crisp question to the user, surfaced in the
  run's report. The trigger is confidence, not kind: the plain "skip them"
  instruction proved insufficient twice because it banned the easy case along
  with the hard one.
  **Read the string first (user ruling, 2026-11-17 — the Q006736 lesson).**
  Before escalating ANY item as decision-kind — and before calling any
  composite, DIY mix, or author annotation "unresolvable" — READ the raw
  string as a human would and ask what it says. Identify each product
  named in it; check each against the catalog (and `knowledge/` for
  line/scent identity — e.g. Proraso White is the green-tea-and-oat line,
  Green is menthol/eucalyptus); strip routine text ("Cold Water") and
  author annotations; and check what the string CURRENTLY matches to in
  the matcher — a wrong current match is a finding that raises the stakes,
  not a reason to escalate the identity. Separate the two questions:
  (1) **what is it** — the reading, decidable by reading the string;
  (2) **how does the matcher credit it** — the mechanism (a separator,
  a guard clause, a matcher change), which may need a follow-up. A
  missing mechanism NEVER makes the identity unclear: if the reading is
  certain, DECIDE the identity autonomously at 100% under the guard
  above (recorded as your own decision, never as "User ruled"), and
  escalate or queue only the mechanism question. Escalate the identity
  to the user ONLY when the reading itself is genuinely ambiguous — a
  bare brand across many entries, an inference with no documentary basis.
  Worked example: "Cold Water, Alum Block, Proraso After Shave Balm
  (Green Tea, Oatmeal)." reads as alum + Proraso White balm (Cold Water
  is routine text); the workers escalated it because comma is not a P-25
  separator — a mechanism question — while the identity was readable all
  along. The same batch also proved the cost of not reading: the string
  was actively mis-attributed to Proraso Green by the subset matcher
  (the word "Green" in the scent notes), which a read would have caught.

## Evidence standard (unchanged from the verified tier)

Promotion requires PRIMARY evidence the user can validate:

- manufacturer product page, or a store product page — "store" is broad
  (user ruling, 2026-10-21): barber-supply, salon-supply, and other trade or
  niche retailers count; the trusted-sources list is a curated starting set,
  not a whitelist gate;
- brand social post with a product image;
- SOTD / community photo where the product (label) is clearly identifiable;
- marketplace listing (eBay etc.) whose PHOTOS verifiably show the physical
  product with a readable label (user ruling, 2026-10-21) — the photo is the
  evidence, never the listing's seller copy; seller's own photos preferred,
  corroboration across independent listings strengthens it; this is the main
  route for vintage/discontinued products with no current retail presence.
  CARVE-OUT: where counterfeits of the product are documented (e.g. Gillette
  Rubie, §A9), a marketplace photo corroborates but does NOT verify — a photo
  of a fake pack is not evidence of the genuine product;
- YouTube video where the presenter holds the product up, label readable;
- **set cross-validation** (above): a validated same maker+scent sibling
  validates the rest of the set; record the sibling id and its evidence URL.

wetshavingdatabase.com / wsdb.pages.dev, trythatsoap, Fragrantica, Parfumo
and similar databases are **leads only** — they point the way, they never
promote. Forum/review text corroborates identity but does not promote on its
own. Research every product individually; names mislead.

## Standing validator procedure

Run one item at a time, in `seq` order, skipping non-`pending` items.

1. **Lock.** Before any write to the catalog exports, create
   `catalog/.catalog.lock`. If it already exists and is < 3600s old, skip
   all writes and report. Remove the lock when done.
1b. **Stale-snapshot re-check** (user rule, 2026-10-20 — concurrency lesson).
   Other agents (corroboration pass, harvest, set sweeps) write through the
   same DB while you research. Before applying ANY verdict, re-fetch the
   queue item AND its entry from the DB. If the item's `state` or the entry's
   `status` changed since you read it (e.g. entry now verified/attested/
   corroborated, or the entry id no longer exists because another pass
   promoted/merged it): do NOT overwrite their work. Instead (a) if the item
   was already resolved to a terminal state by the other agent, update your
   batch notes and move on — count it as resolved, not as a research slot;
   (b) if the entry was replaced by a successor entry (promotion/merge),
   re-point your item's `ref` to the successor id via `update_queue` and
   continue your research against the successor; (c) if the entry vanished
   with no successor you can find, record note `orphaned:<old id>` on the
   item and move on — never recreate the deleted entry. Your research is
   still valid: if your evidence supports a name confirmation for an attested
   entry, promote it; if your evidence contradicts a corroborated identity,
   the evidence wins per the misattribution-override rule.
2. **Set check first.** If the item has a `set_key` and ANY entry with that
   key is already `verified`, resolve the item by set cross-validation
   (sibling sweep rules above) — no research, no batch slot consumed.
2b. **L1 proposal check first** (user rule, 2026-10-28 — L1 proposer).
   Before researching an item, check the L1 lookup
   (`catalog/work/l1_proposals_lookup.db`, table `proposals`, indexed
   by `source_id`; built 2026-10-28 from the post-L0 catalog):
   `SELECT * FROM proposals WHERE source_id = ?` for the item's entry
   id. Rows carry `target_id, target_status, kind, jaccard,
   typo_tokens, typo_distance, group_conflict`. Candidate and typo
   proposals pointing at VERIFIED entries resolve first as cheap
   merges, in the same slot as form-variant merges above — no research
   needed; the merge verdict is the item's resolution — provided the
   target still exists and is still verified (re-fetch live per the
   stale-snapshot re-check, step 1b; proposals predate later merges,
   so a gone target is skipped, never forced). Read typo proposals
   distance-first (distance 1 strongest; distance-3 and low-Jaccard
   tails are hints, not merges). If a proposal row has
   `group_conflict=1`, do not merge on it alone — research it.
   Proposals pointing at PENDING entries are research hints for the
   peer item, not merges on their own. NEAREST proposals NEVER merge
   on their own: a nearest match is a hint for research, not a
   verdict — a conspicuously omitted discriminator is itself signal
   (bare "Gillette Blue" does NOT merge into Silver Blue). Disputed /
   hold-list items were already excluded by the proposer. The lookup
   goes stale as the queue shrinks; re-run the proposer
   (`catalog/work/l1_proposer.py`) when proposal targets are
   routinely gone.
2c. **N-uses research bar** (user rule, 2026-10-29 — N=5, per-family).
   No primary-evidence research on a below-bar family unless a real
   hint exists. `family_uses` on the queue item is the item's
   L1-connected family total: the item's attestation `uses` plus all
   pending clusters linked to it by candidate/typo/typo-bare proposals
   (computed 2026-10-29 by `catalog/apply_below_bar_park.py`; re-run
   that script to refresh after the proposer re-runs). A missing
   `family_uses` (new arrivals) means the family is just the item —
   fall back to its attestation uses. Below bar = `family_uses` < 5
   AND no real hint. Real hints: a verified-target
   candidate/typo/typo-bare proposal for any family member (step 2b),
   a `set_key` shared with a verified entry (step 2), or a readable
   product photo you find. The cheap steps (2, 2b) ALWAYS run
   regardless of the bar — a below-bar item that cheap-resolves is
   still resolved, no research spent. A below-bar item with no hint
   and no cheap resolution: park it with reason `below_bar` (append
   to attempts: date + "below_bar: family_uses <5, no verified hint;
   no primary-evidence research per N-uses bar"). Do not log research
   attempts; do not research it. The 2026-10-29 bulk park already
   parked the existing tail; this rule covers new arrivals and
   anything you encounter still pending.
3. **Take the next pending item.** For a candidate alias, the question is
   narrow: is this cluster really that existing product? For an unverified
   entry: is this a real, distinct product, and what is its canonical
   brand/product (and format, for blades — format comes from the blade
   itself, never from the paired razor)?
4. **Research individually.** Web search + page fetches. If the only
   plausible source needs the live browser (e.g. razorbladesclub.com or
   Razor Emporium site search), log the attempt as
   `"needs parent browser check"` and move on — subagents cannot use the
   live browser.
5. **Verdicts:**
   - **Promote** — primary evidence found: replace the unverified entry
     with a verified entry: standard id (`<Category>/<brand>-<product>`;
     blades are format-first, e.g. `DE/kai-stainless`), brand/product/format
     fields, `evidence` list ({type: maker|store|…, url, shows}), raw
     strings kept as `aliases`, `attestation` carried over, `decisions`
     noting "promoted from unverified" + date. Queue item → `promoted`,
     set `promoted_to`. **Then immediately run the sibling sweep** for its
     `set_key` (and fold any same-category form-variant twins).
   - **Merge** — proven duplicate of an existing entry: fold the cluster's
     raw strings into that entry's aliases, delete the unverified entry,
     queue item → `merged`, set `merged_into`.
   - **Not a product** — proven typo/artifact/joke: delete the entry,
     queue item → `not_a_product` with the reason in the attempt.
   - **Anecdotal** — P-23: real but currently unvalidatable (credible
     poster testimony it existed and was used, PLUS a positive
     indication it was never retailed — e.g. the poster's own
     "prototype"/"one-off"/"never-born" description, no retail trace).
     "We searched and found nothing" alone does NOT qualify — that
     stays unverified. Set entry status to `anecdotal` (never delete
     the entry — its strings must keep matching), record the finding
     in `evidence`, queue item → `resolved` with the verdict in
     `decisions`. No encyclopedia page. The door stays open by design:
     if genuine primary evidence surfaces later (production launch,
     maker page), promote normally.
   - **Candidate alias rejected** — cluster is a distinct product: create
     the unverified entry it would have been, queue item → `rejected_alias`,
     and add a new queue item for the new entry.
   - **No evidence** — append `{date, sources_tried, outcome}` to the
     item's `attempts`, leave `pending`, move on. Record blockers
     specifically (e.g. "brand closed 2025, store offline") so the next
     attempt doesn't repeat dead ends.
5b. **Opportunistic enrichment** (user rule, 2026-10-21; tier corrected
     by user, 2026-10-21). If your research confirms the existence of OTHER
     products you were not asked about — e.g. you pulled a maker's whole
     catalog to verify one soap and it lists forty more — add ALL of them
     to the catalog for future matching, so no future agent repeats the
     work. A maker-site or reputable-retailer listing IS primary evidence
     of existence (standing evidence rules), so every product confirmed
     this way enters as a VERIFIED entry with that listing recorded as its
     evidence — never as an unverified entry waiting for future matching.
     Never force ambiguous matches.
6. **Log.** Append the batch summary to `validation_progress.md`
   (batch #, date, per-item verdicts, catalog counts after). Write the
   batch-finish timestamp (`date +%s >
   ~/hooks/state/sotd_validator_loop/last_finish`) ONLY if this batch
   changed catalog or queue state (any verdict, park, attempt logged,
   enrichment entry, or export) — the timestamp wakes the next worker
   immediately to chain on the new state. If the batch changed nothing
   (pure re-check, no writes), SKIP the timestamp; the ~25-minute
   watchdog wakes the next worker. Rationale (2026-10-30): with the
   queue head blocked on parent-browser checks, every batch was
   finishing with zero changes yet writing the marker, waking the next
   worker ~3 min later to re-log the same items — 20+ no-op batches in
   a day. Zero-change batches must not chain.
7. **Re-run the matcher** after any batch that changed the catalog:
   `python3 match_all.py 2022 2024 2025 2026` in `~/workspace/sotd/catalog`
   (~60s) — this regenerates the matched files and `coverage_report.md`.

## Promotion review trigger

Any unverified entry reaching **≥ 2 distinct authors** qualifies for a
validation attempt (the queue is ordered by hint tier, then maker, then
attestation, so this is automatic). One-offs may also be promoted whenever
primary evidence turns up — attestation orders the work, it never gates it.

## Two-level validation (brand / product) — user model, 2026-10-20

Validation is TWO-LEVEL. Product confidence and brand confidence are
independent: aggregation/reporting runs by brand as well as by product,
so an entry whose product is still unverified can already carry a
validated brand.

- **Brand registry — `catalog/brands.json`.** One record per brand GROUP:
  `{brand_id, canonical_name, former_names [{name, source}], status
  ("validated"|"unverified"), evidence, notes, attested_forms}`. Seeded
  from the brands on verified/needs-review entries (status "validated" —
  their entries carry primary evidence) plus the harvest maker index
  (status "unverified" unless a tier-1 brand or a user-supplied lineage
  covers the group). Built by `catalog/build_brands.py`.
- **Entry fields.** Every catalog entry carries `brand_group` (registry
  brand_id or null) and `brand_status` ("validated"|"unverified"),
  independent of the entry's product-level `status`. An unverified entry
  whose attested brand maps to a validated group gets `brand` stamped to
  the group's canonical name and `brand_status: "validated"` — the
  product itself stays unverified. An entry whose brand does not parse
  keeps `brand_group: null` and records `brand_candidate: ...` in
  `match_notes` when a plausible brand token exists.
- **Lineage grouping.** Renamed companies are ONE group: the registry
  record carries the current canonical name plus every former name (each
  with its source). Entries keep their attested strings untouched
  (aliases are never rewritten); the group is the aggregation key, so an
  "Oleo"-era post and a "Chicago Grooming Co." post aggregate together.
  Applied groups: Chicago Grooming Co. (formerly Oleo Soapworks / Oleo /
  Oleo & Co.) and Declaration Grooming (formerly L&L Grooming) — both
  user-supplied 2026-10-20 and corroborated on the web; Black Ship
  Grooming Co. (formerly Beaver Woodwright, 2015) and Phoenix Artisan
  Accoutrements (formerly How to Grow a Moustache / HTGAM; Petal Pusher
  Fancies merged in) on citable web evidence; Eufros carries its maker's
  trading name JabonMan. Further renames are added only with citable
  evidence — never on resemblance alone (e.g. Chatillon Lux and Maher
  Olfactive are SISTER brands of one perfumer, not a rename, and stay
  separate).
- **Misattribution override.** Posters sometimes name the wrong brand.
  When product-level primary evidence validates a product under a
  different brand than the attested string, the EVIDENCE wins: the entry
  takes the evidenced brand and group, and the override is recorded in
  the entry's `decisions` (attested brand -> evidenced brand, with the
  source). The attested string stays in `aliases`.
- **Validator implication.** Score the two levels separately. If product
  evidence fails yet the brand itself validates (e.g. the maker's store
  or about page confirms the brand and line, just not this exact
  scent/product), stamp `brand_status: "validated"` (plus `brand_group`
  and `brand` = canonical name) on the entry and note "brand validated;
  product unconfirmed" in the queue item's attempt. The item STAYS
  `pending` for product validation — a validated brand never promotes
  the product. Conversely, when a product is promoted, its group and
  brand_status follow the evidenced brand (see the override rule).
- **Coverage** is reported at both levels: product coverage (tier-1 /
  addressable, above) and brand-level coverage — the % of fields
  resolving to an entry with `brand_status: "validated"` (see
  `coverage_report.md`, "Brand-level coverage").
