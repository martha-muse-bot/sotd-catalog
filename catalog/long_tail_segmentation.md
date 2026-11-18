# Long-tail segmentation of the remaining SOTD validation queue

Run: 2026-10-28 (read-only; script `catalog/long_tail_segment.py`,
machine-readable data `catalog/long_tail_segment_data.json`,
CSV `catalog/long_tail_segmentation.csv`).

## Population and method

- **Population: 55,846 pending queue items** in `catalog.db`
  (recomputed; see reconciliation below). Every pending item is assigned
  exactly **one** best route, in this priority order:
  1. **photo-confirm** — a classifiable SOTD photo with a strong/medium
     OCR verdict still awaiting visual confirmation (OCR alone never
     promotes);
  2. **set-sibling** — at least one entry in the item's set
     (`set_siblings`) is already verified;
  3. **nmrs-agree** — nmrs v2 tier `cm-rx-agree` or `cm-only`;
  4. **rx-only** — nmrs v2 tier `rx-only`;
  5. **candidate_alias** — queue kind `candidate_alias`;
  6. **no-route** — none of the above.
- **Photo verdicts** are the union of `phase1_scan.jsonl` (4,663 rows) and
  Phase 2 `phase2_scan_w0.jsonl` + `phase2_scan_w1.jsonl` (union exactly
  13,108 entry_ids, matching the plan; 1,864 cross-file overlaps from the
  w0 relaunch deduped by entry_id, max verdict wins). Phase 1 items
  already human-adjudicated are excluded from the photo route: the 615
  `phase1_confirm.json` entries and all 689 `review_ledger_2026-10-21.jsonl`
  rows (confirm/confirm-kit/reject all mean a human looked).
- **Frequency:** distinct authors from entry attestation (present for all
  55,846 pending items — zero unknowns). 1–2 authors = tail end.
- **Maker size:** pending items per `brand_group` (post-merge groups).

## Reconciliation (all counts exact)

- Pending now **55,846**, down 27 from the 55,873 recorded after the
  brand-group merge (2026-10-28 00:05) — validator-loop churn since
  (promoted +5, merged +18, parked +5 = 28 departures; 1-item residual
  against the earlier snapshot, immaterial).
- nmrs v2 backlog file holds 55,998 records; **152** of them point at
  queue_ids no longer pending, and **0** pending items lack a backlog
  record: 55,998 − 152 = 55,846. ✓
- Tier deltas vs the v2 counts are fully explained by those 152
  departures: cm-rx-agree 5,865→5,802 (−63), rx-only 24,201→24,123 (−78),
  no-signal 6,085→6,077 (−8), sibling-hint 2,886→2,883 (−3);
  cm-only 43, untestable-direct 16,126, disagree 15, candidate_alias 777
  unchanged.
- **Route counts sum exactly to 55,846; unclassified items: 0.**
  (Candidate-alias queue items ref the candidates table by integer
  index, not the entries table; their category/authors/uses come from
  the candidate record and their brand_group from the proposed entry —
  142 of 777 have no resolvable brand_group.)

## Route × category

| route | soap | aftershave | fragrance | blade | razor | brush | total | % pending |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| photo-confirm | 1,535 | 1,099 | 814 | 50 | 121 | 222 | 3,841 | 6.9 |
| set-sibling | 3 | 8 | 5 | 0 | 0 | 0 | 16 | 0.0 |
| nmrs-agree | 1,876 | 0 | 0 | 3 | 1,769 | 2,087 | 5,735 | 10.3 |
| rx-only | 8,786 | 0 | 0 | 1,117 | 3,980 | 8,601 | 22,484 | 40.3 |
| candidate_alias | 419 | 81 | 73 | 5 | 87 | 112 | 777 | 1.4 |
| no-route | 2,330 | 10,285 | 6,798 | 623 | 963 | 1,994 | 22,993 | 41.2 |
| **total** | **14,949** | **11,473** | **7,690** | **1,798** | **6,920** | **13,016** | **55,846** | **100** |

Note the structural split: nmrs tests razors/blades/brushes/soaps directly,
so **aftershave and fragrance appear only in photo-confirm, set-sibling,
candidate_alias, and no-route** — never in nmrs-agree or rx-only. The
AS/frag tail is routed by photo, set, or nothing at all.

## Per-route author / uses profile

| route | items | 1 author | 2 authors | 3+ authors | tail (1–2) | uses total | median uses | max uses |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| photo-confirm | 3,841 | 3,310 | 478 | 53 | 3,788 (98.6%) | 14,857 | 1 | 437 |
| set-sibling | 16 | 7 | 5 | 4 | 12 (75.0%) | 98 | 4 | 18 |
| nmrs-agree | 5,735 | 5,029 | 443 | 263 | 5,472 (95.4%) | 45,741 | 2 | 641 |
| rx-only | 22,484 | 20,903 | 1,026 | 555 | 21,929 (97.5%) | 73,275 | 1 | 1,285 |
| candidate_alias | 777 | 612 | 90 | 75 | 702 (90.4%) | 3,385 | 1 | 149 |
| no-route | 22,993 | 21,088 | 1,121 | 784 | 22,209 (96.6%) | 61,902 | 1 | 546 |
| **total** | **55,846** | **50,949** | **3,163** | **1,734** | **54,112 (96.9%)** | **199,258** | — | — |

Headline: **the whole pending queue is the tail by frequency** (96.9%
have 1–2 authors). Route, not frequency, is what separates actionable
items from residue. The no-route segment also carries real weight:
61,902 uses (31.1% of pending uses), so it is not a corner of
one-offs — it includes heavily-used but evidence-poor items.

## The no-route segment (hard tail)

- **22,993 items (41.2% of pending)**; 22,209 with 1–2 authors.
- By category: aftershave 10,285 (44.7%), fragrance 6,798 (29.6%),
  soap 2,330 (10.1%), brush 1,994 (8.7%), razor 963 (4.2%), blade 623 (2.7%).
  AS + fragrance = 17,083 (74.3% of no-route).
- By nmrs tier: untestable-direct 14,794, no-signal 5,896,
  sibling-hint 2,289, cm-vs-rx-DISAGREE 14.
- **Soft edge (2,303 items with a lead but no direct route):**
  sibling-hint 2,289 (AS/frag whose soap sibling carries an nmrs signal —
  resolvable when that soap's signal is validated) and disagree 14
  (adjudication pending).
- **Pure hard tail: 20,690 items** with no signal of any kind
  (no-signal + untestable-direct), of which **20,025 have 1–2 authors**.
  This is the vintage/discontinued residue: no photo, no verified
  sibling, no nmrs signal, no maker catalog — evidence only via eBay
  label photos, Wayback, or retailer pages.

## Photo route detail

- Scan verdicts overall (17,771 unique rows): strong 1,525, medium 3,271,
  none 10,774, no_photo 2,174, dead 27.
- Pending items with a strong/medium verdict: 3,952; minus 111 already
  adjudicated (Phase 1 ledger rejects still pending) = **3,841
  photo-confirm** — 3,678 from Phase 2, 163 left over from Phase 1.
- Photo-confirm by maker (maker-batched contact sheets): Catie's Bubbles
  172, Barrister and Mann 139, Declaration Grooming 137, Stirling 81,
  Chicago Grooming Co. 77, Southern Witchcrafts 62, Summer Break 61,
  House of Mammoth 61, Australian Private Reserve 58, Ariana & Evans 57;
  193 with no brand_group.

## Set-sibling route detail (nearly exhausted)

Only **17 pending items have a verified set sibling at all** (16 routed
here; 1 took the photo route first on priority). Set cross-validation's
immediately unlockable pool is essentially spent — earlier passes
already resolved what verified soaps could unlock. Future unlocks depend
on new soap verifications, and the pool they would unlock is exactly the
14,794 untestable-direct AS/frag items (the passive-unlock path).

## Maker concentration

- **2,218 named brand groups** hold pending items, plus one unattributed
  bucket; 30 of 2,248 registry groups have zero pending items.
- **Unattributed bucket (empty brand_group): 15,797 items (28.3% of
  pending)** — soap 3,291, brush 3,765, aftershave 3,236, razor 2,929,
  fragrance 1,730, blade 846. Maker batching cannot cover this mass;
  by route: no-route 9,151, rx-only 5,783, nmrs-agree 527,
  photo-confirm 193, candidate_alias 142, set-sibling 1.
- Named top 10 makers (pending items): Declaration Grooming 1,600,
  Barrister and Mann 1,402, Stirling 815, Chatillon Lux 799, Dogwood
  Handcrafts 684, Yaqi 646, Catie's Bubbles 620, Maggard 554, Summer
  Break 544, Gillette 515 — together 14.6% of pending (24.7% for the
  top 25 named). Excluding the unattributed bucket, the queue is
  genuinely long-tailed across makers.
- **1,161 brand groups hold just 1–2 pending items** (1,490 items):
  the small-maker tail. Maker-batched validator wakes work for the top
  makers; the 1,161 small groups are one-or-two-item jobs.

## Interpretation: what the bulk routes can move

- **Photo confirmation — 3,841 items, the only route that verifies
  outright at scale.** Build the maker-batched contact sheets (makers
  above, plus the 193 unattributed) and this segment converts to
  verified/attested on visual confirmation. Phase 1 precedent: 85 photo
  verifications + 255 set resolutions from 4,663 rows.
- **nmrs-signal validation — 5,735 agree + 22,484 rx-only = 28,219
  items (50.5% of pending).** The agree tier is the cheapest validator
  work (both nmrs layers concur); rx-only splits into clean 16,430
  (one distinct regex product) vs ambiguous 6,054 (2+ products, needs
  disambiguation). Note these routes cover hardware + soap only — they
  cannot touch the AS/frag tail.
- **Set cross-validation — 16 items now, but it is the passive engine
  for the 14,794 untestable-direct items:** every future soap
  verification can unlock its AS/frag siblings without new research.
- **Candidate-alias adjudication — 777 items** (90.4% tail authorship):
  alias-or-standalone judgments, mostly soap (419).
- **The hard tail — 20,690 pure no-lead items (20,025 with 1–2
  authors), AS/frag-dominated, plus 9,151 unattributed-maker no-route
  items.** No bulk route reaches these. At validator pace alone
  (a few items per wake) this residue takes years; it shrinks only via
  per-item research (maker/retailer pages, eBay label photos, Wayback)
  or via upstream soap verifications unlocking AS/frag siblings.
  Triage with a documented residue disposition (P-11-style unresolved
  reporting, author-scoped typo folds, non-product calls) is what turns
  this from an open-ended queue into a shrinking one.
