# HANDOFF — SOTD Canonical Product Catalog

If you are reading this because the person or agent who ran this
project is gone, start here. This document tells you what the project
is, how it fits together, how to run it, and how to recover it.

## The one-sentence version

Every morning r/Wetshaving posts a Shave of the Day thread; this
project turns those free-form posts into a canonical catalog of real
shaving products so each morning's entries can be matched to verified
products. **Matching daily entries to verified products is the
primary job; the encyclopedia serves it.**

## THE PUSH RULE — read this first

**Push after every validated change. Every time a change is made that
is validated as working, commit it and push it
(`python3 tools/sync_to_github.py push`). There are NO periodic or
occasional syncs and NO sync cron.** The script is run by hand after
each validated change, nothing more. The repo rots the moment pushes
become "later" — this rule exists because the project was nearly lost
once already: until 2026-11-17 none of it was in any repo at all.

**These repos are the go-forward working directories (Jim,
2026-11-18), not a periodic snapshot artifact.** The live workspace
is mirrored to them on every validated change, never on a timer.
The trigger is explicit: after any validated catalog change, code
change, or knowledge change, run refresh + push so the repos reflect
it the same turn. The staging trees are the push source, not a
snapshot product.

## THE SPLIT (decided 2026-11-17)

This repo holds a true public catalogue:
`catalog/catalog_public.json` — just what all the products in the
catalogue are (11,979 entries: verified, needs-review, attested,
corroborated, anecdotal). It is a scrubbed export, regenerated from
the live DB on every push by `tools/sync_to_github.py`: per entry
only id, category, brand, brand_group, brand_status, product,
status, evidence, set_key, set_siblings,
and attestation counts only (uses, distinct_authors, years).
Stripped: aliases, loose_aliases, author_scoped_aliases,
attestation examples (thread_id/thread_date/author provenance),
unverified clusters (raw post strings, not products), and any nested
provenance keys — plus decisions and match_notes, excluded by Jim's
2026-11-18 decision (the audit trail / working notes; their prose
quoted alias strings and Reddit author names, ~36 entries).
Evidence prose is redacted the same way: Reddit author names, u/
handles, thread IDs, and quoted alias strings that aren't the
product/brand name become [redacted]. The match data — the full DB and its JSON exports,
i.e. everything about what strings match to which catalog items,
plus the queue and attestation provenance — lives in a separate
**private** repo,
[martha-muse-bot/sotd-catalog-data](https://github.com/martha-muse-bot/sotd-catalog-data),
and stays private by design. What a public face for the match data
might look like is a later decision, not this one. Both repos follow
the same push-after-change rule, and the sync script handles both —
`push` for this repo, `push-data` for the data repo (it refuses to
push data unless the data repo verifies as private). Do not let the
two repos drift apart silently.

The merged catalog export is sharded by category into 8 files under
`catalog/catalog_merged/` (Jim, 2026-11-18 — instead of gzipping the
48 MB single file, which would make diffs unreadable; the split
keeps diffs per-category). The 8th shard, `handle`, was added
2026-11-18 (P-26) for handles sold standalone. `sotd_db.export_json()` writes the shards
and `match_all.py` loads the shard directory; no single
`catalog_merged.json` exists anywhere anymore. This also respects
GitHub's real API size limits (measured 2026-11-18, both below the
documented numbers): Data API create-blob rejects files above ~10 MB
(9.8 MB ok, 18.3 MB → 422), Contents API accepts 28.6 MB but
rejects 48.5 MB (422). Largest shard is ~13 MB, so shards fit the
Contents API; the sync script routes any staging file over 10 MB
through the Contents API automatically (one commit each, before the
Data-API tree push).

## Architecture

```
Reddit SOTD threads (Arctic Shift archive)
  -> live-browser pull (Reddit blocks server-side fetches)
  -> sotd_parser.py                     (normalized rows: sotd_*_full.json)
  -> catalog/catalog.db                 (SQLite: entries, queue, candidates, brands)
       -- sotd_db.py is the ONLY write path; JSON files are read-only exports
  -> catalog/match_all.py              (matcher -> matched_*.json + coverage_report.md)
  -> catalog/validation_queue.json     (worklist, worked by the validator loop)
```

Supporting loops, all driven by the definitions in `crons/`:

- **Validator loop** (every 30 min, batch of 12): works the queue in
  `seq` order — promotes on primary evidence, merges proven
  duplicates, marks proven non-products, parks below-bar families.
  Procedure: `catalog/validation_README.md`. Hook script:
  `hooks/sotd_validator_loop.sh`.
- **Escalation queue:** items blocked on parent-only work escalate to
  state `awaiting_parent` with `parent_need` + `parent_kind`
  (`browser` | `decision`). A daily sweep (~10:15 CST) works the 50
  oldest browser-kind items with live-browser checks.
- **World learner** (every 2 h): learns how the wet-shaving world
  fits together into `knowledge/` — lineages, renames, closures,
  product lines, hardware lore. Only `established` facts (sourced,
  dated) may be treated as true downstream; `lead` is pointer-only.
- **Daily pull** (~09:15 CST): pulls the newest SOTD threads,
  parses them, re-runs the matcher.
- **nmrs PR program:** corrections to the upstream nmrs/sotd-pipeline
  matcher go as pull requests from the
  [sotd-pipeline](https://github.com/martha-muse-bot/sotd-pipeline)
  fork — one correction per PR, 2 PRs/day cadence, with a daily
  review watch that surfaces the maintainer's feedback each morning.

The published encyclopedia is a separate repo:
[wetshaving-knowledge](https://github.com/martha-muse-bot/wetshaving-knowledge)
(Quartz site) — built from `knowledge/` + `catalog/precedents.md`.
`knowledge/` here is the SOURCE; the vault repo is its published copy.

## The precedent system (the rules that bind)

`catalog/precedents.md` is the registry of user rulings, P-01…P-25
(standing as of 2026-11-17). Every catalog opinion must cite its
governing precedent(s) and flag deviations; strong evidence can
overturn a precedent, which queues every dependent decision for
re-review. The load-bearing ones:

- **P-01** community treatment defines product identity.
- **P-04** brand of record / user intent is identity; manufacture is
  an attribute. **P-05** maker's own channel/co-brand name merges.
- **P-13** every tier is matcher-visible (verified > attested/
  corroborated > unverified), each tier-labeled in coverage.
- **P-14** razor–blade format agreement, with the hard constraint:
  no default may resolve a blade against the paired razor's format.
- **P-15** loose alias / probabilistic default — ALL likelihood-based
  defaults are loose, with the leader's share recorded; never used to
  settle identity disputes.
- **P-17** model-attribute: a maker's named model is ONE entry;
  revisions, eras, handles, finishes are attributes.
- **P-18** upstream-confidence: a catalog correction proposed to nmrs
  at 100% confidence is applied to our own catalog in the same turn.
- **P-19** custom commissions are not catalog entries.
- **P-21** version attribution by author pin, then maker, then era.
- **P-22** soap base is an attribute, never identity.
- **P-23** anecdotal tier: real but unvalidatable-in-principle
  products (prototype/one-off/never-born) keep an entry for matching,
  never published in the encyclopedia.
- **P-24** alum is its own post-shave thing, not an aftershave.
- **P-25** composite split: multi-product field strings split at
  ingest/matcher level, each half to its own entry (per-field
  separators + G0–G6 guard; `SPLIT_ENABLED` flag). The **comma
  carve-out** (variant (e), 2026-11-17) extends it to paren-aware
  commas on aftershave/blade/razor/fragrance (soap held), exact/
  normalized-only parts + alum fallback + weak-only paren rule
  (`COMMA_SPLIT_ENABLED` flag).

## Operating rules (standing, from the user)

- **100% confidence rule:** proceed at 100% confidence where the
  evidence supports it; hold uncertainty for joint review. At 100% a
  worker DECIDES AUTONOMOUSLY and records the decision as its own
  (evidence, date, actual basis) — never write "User ruled:" /
  "user-approved" unless the user actually ruled. Below 100%:
  escalate promptly with a crisp ask and leave the item untouched.
- **Read the string first (2026-11-17, the Q006736 lesson):** before
  escalating anything as decision-kind, read the raw string as a
  human would — identify each product named, strip routine text and
  annotations, check what it currently matches to. Separate *what is
  it* (the reading, decidable autonomously at 100% if certain) from
  *how the matcher credits it* (the mechanism, queued separately). A
  missing mechanism NEVER makes the identity unclear.
- **Choice presentation:** whenever the user is asked to choose, ONE
  single message contains, in order: (1) a report summarizing all
  available evidence, (2) a clear recommendation, (3) the options
  buttons. Never split the buttons into a follow-up message.
- **Evidence standard:** promotion requires PRIMARY evidence — maker/
  store product page ("store" is broad: barber/salon/trade retailers
  count), brand social post with product image, SOTD photo with a
  readable label, eBay listing PHOTOS with a readable label (the
  photo, never seller copy; documented-counterfeit products excepted),
  label-readable YouTube hold-up, or set cross-validation. Databases
  (wetshavingdatabase, trythatsoap, Fragrantica, Parfumo, nmrs
  catalog) are leads only, never primary. Research every product
  individually; names mislead.
- **Two-level validation:** brand confidence and product confidence
  are separate (brand registry in `catalog/brands.json`); a verified
  product overrides an attested brand.
- **Set cross-validation is bidirectional:** validating ANY member
  of a maker+scent set validates the siblings (soap/aftershave/
  fragrance), recorded with the sibling's evidence.
- **N-uses bar (N=5 per family):** no primary-evidence research on
  a below-bar family without a real hint (verified-target proposal,
  set sibling, readable photo). Cheap merges always run regardless.
- **Secrets:** API keys, tokens, and credentials live in local
  config / the connector store only — never in this repo, never in
  memory files. The staging tree was grepped before the first push;
  re-grep before any push that adds new file types.

## The queue design

- **Primary queue** (`state: pending`): the workers' worklist,
  ordered by `seq` (nmrs hint tier first, then maker batch, then
  attestation). One item = one unverified cluster or one
  candidate-alias proposal. States: `pending` → `promoted` |
  `merged` | `not_a_product` | `rejected_alias` | `resolved`
  (decision/anecdotal) | `parked` (below-bar).
- **Escalation queue** (`state: awaiting_parent`): items blocked on
  parent-only work, with `parent_need` (crisp ask) + `parent_kind`
  (`browser` | `decision`). Workers escalate only after their own
  angles are exhausted (≥2 real attempts or an explicit dead end).
- **Queue items carry `ref`** (the cluster entry id). Promotions
  create the new verified entry and set `promoted_to`; the source
  cluster entry remains at its tier. Never wrap entry fields in a
  nested `data` JSON string — `sotd_db.get_entry` returns the FLAT
  dict, and `update_queue` takes the FULL item dict (a partial dict
  SILENTLY DROPS omitted fields).
- **Concurrency is real:** validator workers, background passes, and
  the operator write the DB simultaneously. Re-fetch entry + queue
  item before ANY verdict; respect `.catalog.lock` (<1h old = skip
  writes); `upsert_entry` the merge target BEFORE any re-fetch in
  the same script.

## Key numbers (as of 2026-11-18)

- Catalog: 48,368 entries — verified 6,663; queue 64,795 items
  (pending ~16,263; awaiting_parent ~425); brands 2,319; candidates 799.
- Dataset: 241,319 rows, 2016–2026, 4,462 threads, 100% day coverage.
- Matcher: `python3 catalog/match_all.py <years>` (~2.5–4 min for
  4 years); outputs `matched_<year>.json` + `catalog/coverage_report.md`.
  P-25 A/B: 9,417 rows → 19,418 attributions, 0 split-caused
  regressions. Comma carve-out A/B (2022–2026): 208 rows / 441 parts,
  0 regressions.
- Categories (7): brush, aftershave, soap, fragrance, razor, blade,
  knot. No alum/treatment category exists.

## Recovery path (if you are starting from this repo alone)

1. **Restore the DB:** it lives in the private sibling repo
   [sotd-catalog-data](https://github.com/martha-muse-bot/sotd-catalog-data)
   — clone that repo and copy `catalog/catalog.db.gz` here, then
   `gunzip catalog/catalog.db.gz` → `catalog.db`.
   Verify: `sqlite3 catalog.db "PRAGMA integrity_check;"` → `ok`, and
   entry count matches the data repo's `manifest.json`. The scrubbed
   public catalogue (`catalog/catalog_public.json`) is already in
   this repo — a read-only product list, not a substitute for the DB.
2. **Regenerate exports** (they are in the repo, but confirm they
   match): `python3 -c "import sys; sys.path.insert(0,'catalog');
   import sotd_db; sotd_db.export_json(sotd_db.connect())"`.
3. **Re-pull the datasets** (only if you need the raw rows): the pull
   recipe is Arctic Shift archive → live-browser pull (Reddit blocks
   direct server-side fetches) → `sotd_parser.py`. Raw comments are
   `[{author, body, created_utc, id}]`; the parser writes normalized
   rows. A daily pull can be scheduled the same way. Datasets are
   NOT in this repo (240 MB, regenerable) — see README.
4. **Re-run the matcher:** `python3 catalog/match_all.py 2022 2023
   2024 2025 2026` (add years as their datasets land). This
   regenerates `matched_*.json` + `coverage_report.md`.
5. **Restart the loops** from `crons/`: validator (30 min), world
   learner (2 h), escalation sweep (daily ~10:15 CST), daily pull
   (~09:15 CST), nmrs daily PR (~08:15 CST) + review watch (~08:30
   CST), anecdotal watch (Mondays ~11:15 CST), nmrs sync (Mon/Thu).
   The hook script is `hooks/sotd_validator_loop.sh`.
6. **Upstream:** the nmrs PR program runs from the
   [sotd-pipeline](https://github.com/martha-muse-bot/sotd-pipeline)
   fork (branch per PR, one correction per PR, verified open +
   mergeable via the API before reporting). The vault site is the
   [wetshaving-knowledge](https://github.com/martha-muse-bot/wetshaving-knowledge)
   repo, rebuilt from `knowledge/` + `precedents.md`.

## What is intentionally NOT in this repo

- The match data itself (the full DB `catalog/catalog.db.gz` and the
  JSON exports — merged catalog as 8 per-category shards under
  `catalog/catalog_merged/`, `validation_queue.json`,
  `candidate_aliases.json`, `brands.json`) — it lives in the private
  sibling repo
  [sotd-catalog-data](https://github.com/martha-muse-bot/sotd-catalog-data)
  (see The Split above). The matcher cannot run without it; restore
  it first (Recovery path, step 1). The scrubbed public catalogue
  (`catalog/catalog_public.json`) IS in this repo.
- Raw datasets and matched outputs (regenerable; see above).
- `catalog/work/` scratch (23 GB) except `l1_proposer.py`.
- `external/` (local sotd-pipeline clone), pre-SQLite backups,
  matcher backups, queue-order backups, `*.tmp`, `__pycache__`.
- The Alexa voice-task bridge (`alexa-martha/`) — a separate project.
- The goal workspace's `hidden_files/` (1.1 GB of run logs and
  snapshots) — operational history, not project state.
- Any credential, token, or key (see Secrets above).

## Known open items (2026-11-18 snapshot)

- **Q006734 follow-on:** port the alum fallback into the P-25
  semicolon path (48 alum-led clusters / 422 uses). The comma
  carve-out's fallback does NOT cover it; Q006771 resolves with it.
- **Composite-cluster retirement:** P-25-split clusters still exist
  as entries; retirement pass scoped, not yet run.
- **Alias hygiene (§9):** composite strings harvested as aliases
  poison reverse-subset matching; a catalog pass is owed.
- **Comma carve-out follow-ups:** soap descriptor guard, blade G7
  guard (Super-Platinum restatement pattern).
- **Catalog lane (nmrs PRs):** blocked on Le R'sistant evidence and
  the Clubman Pinaud Synthetic design decision; code lane continues.
- **Q006736's Stirling rows:** the 123 rows carrying "Stirling Bay
  Laurel Witch Hazel" still credit alum only — the olive-oil/emu-oil
  third part matches nothing and the carve-out requires every part
  to resolve.
