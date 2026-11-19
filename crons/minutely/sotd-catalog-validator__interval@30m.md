---
id: sotd-catalog-validator
title: SOTD catalog validator
enabled: false
owner: goal:sotd-canonical-product-catalog
mode: task
schedule:
  kind: interval
  timezone: America/Chicago
  at: 2026-10-20T22:13:10
  every: 30m
timeout_secs: 1800
delivery:
  - chat_id: cb2a7a82-5389-428b-9380-dcb02ff5eb26
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"cb2a7a82-5389-428b-9380-dcb02ff5eb26","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"5ac1ab52-3f96-4dd6-afc1-3407e0e9949e"}'
  presentation_locale: en-US
---
Standing task: work the SOTD catalog validation queue in ~/workspace/sotd, one batch per run.

STORAGE (post-SQLite): The source of truth is catalog/catalog.db, accessed ONLY through catalog/sotd_db.py (read the Storage section of catalog/validation_README.md first and follow it). catalog/catalog_merged/<category>.json (8 per-category shards), validation_queue.json, brands.json and candidate_aliases.json are read-only exports regenerated from the DB — never edit them directly. Take queue items with sotd_db.next_queue, write verdicts with upsert_entry/delete_entry/update_queue, and call export_json() once at the end of any batch that changed anything. If catalog/.catalog.lock exists and is less than 2 hours old, end quietly (a bulk multi-step pass is mid-flight).

SETUP: Read catalog/validation_README.md and follow its procedure. Also read the wetshaving knowledge base — ~/workspace/sotd/knowledge/lineages.md, product_aliases.md, glossary.md, people.md, product_lines.md, hardware_lore.md, world_notes.md — before researching: facts tagged "established" there are trusted context (renames, closures, aliases, shorthand expansions, naming traps); facts tagged "lead" are pointers only, never evidence; glossary entries marked AMBIGUOUS must never be auto-applied without context from the post itself.

STATUS TAXONOMY (user rulings, 2026-10-20): unverified < corroborated (identity resolved by the nmrs external catalog; existence likely) < attested (existence established by 3+ distinct-author posts; name NOT confirmed) < verified (primary evidence; settles existence and identity). Corroborated/attested entries never auto-promote. When you promote an ATTESTED entry on primary evidence, you are confirming its name: if the evidence matches the attested name, note "name confirmed" in decisions; if it contradicts, the evidenced identity wins (misattribution override below) and the attested name becomes an alias. Attested entries do NOT unlock set cross-validation — only verified siblings do.

TWO-LEVEL VALIDATION (user rule): brand confidence and product confidence are SEPARATE. The brands table in the DB (brands.json export) is the brand registry: renamed companies form ONE brand group (e.g. Chicago Grooming Co. includes former name Oleo; Declaration Grooming includes L&L Grooming) — the group is the aggregation key, entries keep their attested names. Every item you process gets both questions answered: is the BRAND validated (attested name maps to a validated group in the registry, or you find primary evidence the brand exists/existed under that name), and is the PRODUCT validated? If the product validates, stamp brand_status "validated" on the entry as part of the promotion. If product evidence fails but the brand validates, still stamp the entry's brand + brand_group + brand_status "validated" via sotd_db, note "brand validated, product unproven" in the attempt, and leave the item pending for the product. MISATTRIBUTION OVERRIDE: posters sometimes name the wrong brand — if product evidence shows the product belongs to a different brand than the attested string claims, the EVIDENCE wins: promote under the evidenced brand, set brand_status "overridden", and record the attested brand + the override in the entry's decisions.

SET CROSS-VALIDATION (user rule): soaps, aftershaves, and fragrances from the same maker with the same scent form a SET (queue items carry a set_key linking siblings). Validation is BIDIRECTIONAL: whenever ANY member of a set is validated on primary evidence — or is already verified in the catalog — every unverified sibling in the set is validated too, recorded with evidence {type: "set-cross-validation", sibling entry id + its evidence URL}, and its queue item is marked done WITHOUT separate research. Soaps are worked first within the scent categories because a validated soap unlocks its whole set; but an aftershave or fragrance validated first unlocks its set exactly the same way. Always check for a set sibling before researching any scent item.

BATCH: Take the next 12 pending items via sotd_db.next_queue in queue order (soaps by attestation first within scent categories, then highest distinct-author attestation). Before researching an item, resolve it by set cross-validation if a sibling is already verified (counts toward the batch's work but not its research slots — take additional items so the batch still researches up to 12 unvalidated items). For each researched item, work individually under the full evidence standard in ~/memory/groups/r-wetshaving.md: PRIMARY evidence only — manufacturer page, store product page, brand social post with a product image, community/SOTD photo with the product clearly identifiable, YouTube video with the label readable on pause, or set cross-validation from a verified same maker+scent sibling. wetshavingdatabase.com / wsdb.pages.dev and the nmrs catalog are leads/corroboration only, never primary evidence.

TIME BUDGET (hard rule — two runs died on research timeouts, 2026-10-21): you have 30 minutes and EVERY run must finish inside it. Research at most 6 items per run — form-variant merges and set cross-validations are cheap, so always resolve those FIRST and reserve research slots for items that genuinely need evidence hunting. STOP all new research at minute 20 of the run, no exceptions: apply whatever verdicts you have, call export_json() if anything changed, append the progress-log entry, and exit. If an item's research is incomplete when the budget ends, record the item as pending with the attempt noted and move on. An unexported, unlogged batch is the failure mode — a smaller batch is not.

VERDICTS (apply via sotd_db):
- Evidence found: promote. For kind "unverified"/"attested"/"corroborated", replace the entry with a proper entry (id <Category>/<brand>-<product>, brand/product/format fields from the evidence, evidence list with {type,url,shows}, the raw strings kept as aliases, status "verified", brand_group + brand_status per the TWO-LEVEL rule, note "promoted from unverified" — or "name confirmed from attested" — in decisions). For kind "candidate_alias", add the cluster's raw strings as aliases to the proposed entry and note the validation source in its match_notes. AFTER any promotion in a scent category, immediately promote all unverified set siblings per the SET CROSS-VALIDATION rule above.
- Proven duplicate of another entry: merge aliases into that entry, delete the source entry, record merged_into on the queue item.
- Proven not a product (typo of a known product — add as alias there if the evidence supports it — parser artifact, or joke): record the verdict and reason on the queue item and mark/delete the entry accordingly.
- No evidence found: append an attempt {date, sources tried, brand_outcome} to the queue item and leave it "pending"; after 2 thorough failed attempts set state "parked". You cannot use the live browser — if the only plausible source is browser-only (e.g. razorbladesclub.com's own site search, Razor Emporium), log the attempt as "needs parent browser check" and move on; do not loop on it.

LOG: Append a short batch summary (date, items processed, verdicts incl. brand-only validations, set siblings resolved by cross-validation) to catalog/validation_progress.md, update queue states via sotd_db, and call export_json() if anything changed.

REPORTING: Stay silent for routine batches. Report to this chat only when: (a) the queue's pending count reaches zero — give a final totals summary; (b) a run hits a real blocker or repeated failures; (c) cumulative promotions cross a multiple of 100 — give a one-line progress note with pending/promoted/parked counts.
