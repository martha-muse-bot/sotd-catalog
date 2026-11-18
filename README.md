# sotd-catalog — Canonical catalog of r/Wetshaving Shave of the Day products

This repo is the backup and handoff copy of the SOTD canonical product
catalog project: the matcher, the validation queue, the precedents, and
the world knowledge behind them. It exists so the work survives
independently of any one agent session or machine. The live project
runs on its home machine; this repo is its committed state.

## What this project is

Every morning, r/Wetshaving posts a "Shave of the Day" thread. Each
post names a razor, blade, brush, soap, aftershave, and fragrance in
free-form text. This project turns that messy text into a canonical
catalog of real shaving products, so each morning's entries can be
matched to verified products. **Matching daily entries to verified
products is the primary job; the encyclopedia serves it.**

- **Dataset:** 241,319 parsed SOTD rows, 2016–2026 (see "What is NOT in
  this repo" — the raw datasets are regenerable and live outside git).
- **Catalog:** ~48,368 entries (verified 6,663 as of 2026-11-18),
  keyed by blade format first, then brand and product name, each with
  an alias list and first-party evidence.
- **Matcher:** `catalog/match_all.py` — three-tier resolution
  (verified > attested/corroborated > unverified), loose aliases,
  author-scoped aliases, razor–blade format agreement (P-14),
  composite splitting (P-25, plus the comma carve-out).
- **Validation:** a standing validator loop works
  `catalog/validation_queue.json` (~64,795 items), promoting entries
  on primary evidence only, merging proven duplicates, and escalating
  what only the user can decide.
- **World knowledge:** `knowledge/` — brand lineages, renames,
  closures, product lines, hardware lore, glossary. This directory is
  the SOURCE; the
  [wetshaving-knowledge](https://github.com/martha-muse-bot/wetshaving-knowledge)
  repo is its published copy (Obsidian vault, Quartz site).
- **Upstream:** corrections to the nmrs/sotd-pipeline matcher go
  through the [sotd-pipeline](https://github.com/martha-muse-bot/sotd-pipeline)
  fork as pull requests (2/day cadence).

## What's in this repo

| Path | What it is |
|---|---|
| `sotd_parser.py`, `build_2026.py`, `build_year.py`, `fill_gaps.py`, `fill_gaps_year.py`, `lg_sweep.py` | Dataset parser and pull/backfill scripts |
| `catalog/sotd_db.py` | The only way to read/write the catalog DB |
| `catalog/match_all.py` | The matcher (P-25 composite split, comma carve-out) |
| `catalog/catalog_public.json` | The public catalogue: scrubbed export of the products only (see above). Regenerated from the live DB on every push by `tools/sync_to_github.py`. |
| Match data | NOT in this repo — the full DB (`catalog/catalog.db.gz`) and the JSON exports (`catalog_merged.json`, `validation_queue.json`, `candidate_aliases.json`, `brands.json`) live in the private sibling repo [sotd-catalog-data](https://github.com/martha-muse-bot/sotd-catalog-data). |
| `catalog/validation_README.md` | The validator contract: tiers, evidence standard, procedure |
| `catalog/precedents.md` | The precedent registry (P-01…P-25) — rulings that bind |
| `catalog/discuss_consolidated.md` | The discuss queue — open identity questions |
| `catalog/multi_item_field_analysis_2026-11-16.md`, `catalog/comma_carveout_scoping_2026-11-17.md` | Composite-split design analyses |
| `catalog/ikon_bulk_harvest_2026-11-08.md`, `catalog/tech_attribute_fold.md`, `catalog/long_tail_segmentation.md` | Harvest plan, attribute-fold project, queue segmentation |
| `catalog/work/l1_proposer.py` | The L1 candidate/typo proposer (wired into the validator loop) |
| `knowledge/` | World knowledge (source of truth; see above) |
| `crons/` | The scheduled-job definitions (validator, learner, sweeps, PR program) |
| `hooks/sotd_validator_loop.sh` | The validator-loop hook script |
| `GOAL.md` | The goal statement |
| `tools/sync_to_github.py` | Push-after-change sync script (see below) |
| `HANDOFF.md` | The handoff document — start here if you inherit this project |
| `manifest.json` | File inventory with sizes + md5s for this tree state |

## What is NOT in this repo (and why)

- **Raw datasets (`sotd_*_full.json`, 240 MB) and matched outputs
  (`matched_*.json`, 384 MB):** regenerable. The pull recipe is
  Arctic Shift archive → live-browser pull → `sotd_parser.py`
  (Reddit blocks direct server-side fetches), then
  `python3 catalog/match_all.py <years>` to regenerate matched files.
  See HANDOFF.md for the recovery path.
- **`catalog/work/` scratch (23 GB):** A/B snapshots, OCR venv,
  corroboration photos, ingest indexes — except `l1_proposer.py`,
  which is included above. Rebuilt on demand.
- **`external/`:** the local sotd-pipeline clone (the fork on GitHub
  is the real copy).
- **Pre-SQLite backups, matcher backups, queue-order backups,
  `*.tmp`, `__pycache__`, `.catalog.lock`:** history, not state.

## Restore

```bash
# The catalog DB lives in the private sibling repo sotd-catalog-data;
# clone it and copy catalog/catalog.db.gz here, then:
gunzip catalog/catalog.db.gz          # -> catalog/catalog.db
python3 -c "import sys; sys.path.insert(0,'catalog'); import sotd_db; c=sotd_db.connect(); print(sotd_db.counts(c))"
python3 catalog/match_all.py 2022 2023 2024 2025 2026   # regenerate matched files
```

The scrubbed public catalogue (`catalog/catalog_public.json`) is
already in this repo — it is a read-only product list, not a
substitute for the DB.

`catalog.db` is the single source of truth. Never edit the JSON
exports directly — regenerate them with `sotd_db.export_json()`, and
never write the tables with ad-hoc SQL; all writes go through
`catalog/sotd_db.py`.

## Staying in sync

**Rule (2026-11-17): push after every validated change.** Every time
a change is made that is validated as working, run
`python3 tools/sync_to_github.py push` for this repo and
`python3 tools/sync_to_github.py push-data` for the private data
repo (the script refuses to push data unless the data repo verifies
as private). There are NO periodic or
occasional syncs and NO sync cron — the script is run by hand after
each validated change. `push` refreshes the staging tree from the
live workspace (fresh DB export, re-gzip, copy) and uploads one
commit to `main` via the GitHub API. See HANDOFF.md.

**These repos are the go-forward working directories (Jim,
2026-11-18), not a periodic snapshot artifact.** The live workspace
is mirrored here on every validated change, never on a timer. The
trigger is explicit: after any validated catalog change, code change,
or knowledge change, run refresh + push so the repos reflect it the
same turn. The staging trees are the push source, not a snapshot
product.

## The catalogue: public products, private match data (decided 2026-11-17)

This repo holds a true public catalogue:
`catalog/catalog_public.json` — just what all the products in the
catalogue are (11,979 entries: verified, needs-review, attested,
corroborated, anecdotal). It is a scrubbed export, regenerated from
the live DB on every push: no aliases, no loose aliases, no
author-scoped aliases, no attestation examples or provenance, no
unverified clusters (those are raw post strings, not products), and
no decisions or match_notes — the audit trail and working notes are
excluded by Jim's 2026-11-18 decision, because their prose quoted
alias strings and Reddit author names. Evidence prose is redacted
the same way: Reddit author names, u/ handles, thread IDs, and
quoted alias strings that aren't the product/brand name become
[redacted]; the bare words "aliases"/"author_scoped" in our own
notes and reddit.com citation links in evidence remain. The match data — the full DB and its JSON exports, i.e. everything about
what strings match to which catalog items, plus the queue and
attestation provenance — lives in the **private** repo
[martha-muse-bot/sotd-catalog-data](https://github.com/martha-muse-bot/sotd-catalog-data)
and stays private by design. What a public face for the match data
might look like is a later decision, not this one. See HANDOFF.md.
