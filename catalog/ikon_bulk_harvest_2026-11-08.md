# iKon bulk harvest — prep note 2026-11-08

Prepared by proactivity research, 2026-11-08 ~10:00 CST. Not applied to the catalog.
No entries were created, promoted, merged or edited for this note.

## Why now

- Morning world-learner run (2026-11-08) corrected the standing record: iKon Razors
  is NOT defunct. ikonrazors.com is live and selling 26 products (store rebuilt
  Jan 2023). Founder Greg Kahn; maker spelling "Tek".
  Source: `~/workspace/sotd/knowledge/lineages.md` Run 2026-11-08 section;
  `~/workspace/sotd/knowledge/hardware_lore.md` Run 2026-11-08 section.
- Re-verified live in this run: `https://ikonrazors.com/products.json?limit=250`
  crawled 2026-11-08 15:55 UTC; sampled products match the learner inventory
  (B1 Open Comb Deluxe Travel Kit $104.99 available, Short Comb Razor kit $55,
  B1 OSS kit $99.99, B1 Slant Razor $120, B1 Slant Head $100, X3 Slant Head $50,
  OG1 Head $35 available, Short Comb Head $35 available, Tek Head $50,
  Short Comb Razor $45 available, OSS Handle $22 available). Products carry
  `updated_at` 2026-11-08T10:55:43-05:00 — the store was touched today.
- DB recheck in this run (`catalog/catalog.db`, 2026-11-08): 104 entries whose id
  contains "ikon", statuses 88 unverified / 10 corroborated / 6 attested /
  **0 verified**, 621 attested uses in total. Still the largest verified-coverage
  gap in the razor catalog. The correction was reported to the user in the SOTD
  side chat 2026-11-08 15:20 UTC; no harvest has been run yet.

## What the live store can promote (LANE 1 bulk harvest)

Maker/store listing is primary evidence under the catalog rules. Heads below are
distinct models by geometry (P-03 / P-17: model = one entry; handles, finishes
and kit bundles are attributes/variants, never entries).

| Head (canonical) | Live store evidence | Catalog clusters to fold/promote | Uses in family |
|---|---|---|---|
| B1 Standard (solid bar) | B1 Standard Head $79.99 available; B1 Standard Razor $89.99 available | `ikon-b1-standard` (7u), `ikon-b1` (3u, corroborated), `ikon-b1oss` (1u, corroborated — OSS is the dual-function head, see below; do NOT fold blindly) | B1 family 92u / 12 clusters |
| B1 Deluxe (open comb) | B1 Open Comb Deluxe Head $79.99 available; B1 Open Comb Deluxe Razor $89.99 available; Travel Kit $104.99 | `ikon-b1-deluxe` (30u, corroborated), `ikon-b1-oc` (7u, corroborated), `ikon-b1-deluxe-oc` (2u), `ikon-open-comb-deluxe` (1u), `ikon-deluxe-oc-satin-silver-coating` (1u) | part of 92u above |
| B1 OSS (dual-function OC+SB) | B1 OSS Head $79.99 available; B1 OSS Razor $89.99 available ("best-selling") | `ikon-b1oss` (1u), `ikon-b1-oss-slant` (2u — check: OSS slant wording is suspect, verify before folding) | part of 92u above |
| B1 Slant | B1 Slant Head $100; B1 Slant Razor $120 (both currently unavailable, still listed) | `ikon-b1-slant` (1u) | part of 92u above |
| X3 Slant | X3 Slant Head $50; X3 Slant Razor $75 available | 36 X3 clusters, incl. `ikon-x3-slant-razor` (2u) and all "X3 on <other handle>" strings (handle reuse, fold per P-17) | 134u / 36 clusters |
| Tek | Tek Head $50; Tek Razor $75 available ("Aggressive level shave") | `ikon-shavecraft-tek` (32u, corroborated), `ikon-tek` (attested), `ikon-razors-tek-head-base-plate-with-bulldog-80-mm-handle` (corroborated), `ikon-shavecraft-104-tech` (1u — 104 "Tech" is the Tek head, era name), `ikon-tech-tek` (1u) | 50u / 6 clusters |
| Short Comb | Short Comb Head $35 available; Short Comb Razor $45 available | `ikon-razors-ikon-short-comb-with-bulldog-80-mm-handle` (88u, 1 author — PhilosopicalZombie), `ikon-shavecraft-short-comb-head-w-maggard-mr5-handle` (1u) | 90u / 3 clusters |

Rough coverage if those 7 heads are promoted: ~366 of the 621 uses, with the
handle-variant clusters folding into their head entry rather than becoming entries.

## Guards — do not fold

- `ikon-b1-tech` (28u, all ChangoBat, 2018) stays in the B1 family, never the Tek
  entry (learner-resolved 2026-11-08).
- "B1 Tech" / "Tech" without B1 → Tek only as a LOOSE alias (era/community
  spelling), never certain on a bare "Tech" string alone.
- Maggard V3 / V3A heads on iKon handles (7 clusters) are Maggard products,
  handle reuse only.
- "Weber ARC on iKon" / DE89 on iKon handles are other makers' heads on iKon
  handles, never iKon products.
- OG1 Head $35 / OG1 Razor $44.99 are on the store but have ZERO dataset rows —
  watcher only, no entry owed until a string appears.

## NOT promotable on store evidence — still needs other primary evidence

- 101 (77u / 13 clusters, incl. `ikon-101` 41u / 6 authors) and 102 (114u /
  11 clusters, incl. `ikon-102` 73u / 12 authors): NOT on the current store.
  These are the two biggest remaining gaps after the harvest; evidence route is
  retailer listings / labelled photos / B&B, not the maker site.
- SBS (3 clusters, 19 bare-SBS strings, 2016–2020): NOT on the store; expansion
  still unpinned — do not guess. One entry for both generations (P-17).
- El Jefe (5u / 2 clusters): NOT on the store; retailer-only or discontinued,
  unpinned.

## Suggested next step (needs the user's go-ahead on prioritisation)

Run the iKon harvest as the next validator batch: promote the 7 heads above on
the live maker listings, folding the handle-variant clusters per P-17, with the
guards above. That leaves 101 / 102 / SBS / El Jefe for the ordinary queue.

## Addendum 2026-11-11 — map revised; live-store recheck pending

Prepared by proactivity research, 2026-11-11 ~12:00 CST. Still not applied to the catalog.
This addendum supersedes the OG1 / 101 / 102 / El Jefe sections above.

- **OG1 = 101 (learner run 2026-11-10 ~01:06, verified against the live store feed
  in-session):** the store lists OG1 as a dual open-comb/safety-bar head — the 101
  design. 101 strings end 2021-06-10; the dataset has zero OG1 strings.
  → The 101 clusters fold into a NEW OG1 entry on maker-listing evidence.
  OG1 is NOT a watcher-only item (corrects the section above).
- **X3 ≠ 102, never fold:** X3 is the 2012 original slant; 102 was dropped in the
  Jan 2023 store rebuild. They stay separate entries (102 left to the ordinary
  queue — not on the current store).
- **El Jefe = AC-format SE razor, 2016–2017, discontinued by the Jan 2023 rebuild.**
  → An El Jefe AC entry is owed (evidence route: retailer/photo, not the live store).
- **SBS:** letters still unpinned; dates bracketed (learner run 2026-11-10).
  One entry for both generations (P-17) when evidence lands.
- **DB recheck 2026-11-11 (catalog/catalog.db):** still 104 iKon entries,
  88 unverified / 10 corroborated / 6 attested / 0 verified, 621 attested uses —
  unchanged since 2026-11-08. Family uses by id-keyword: X3 134u/36 clusters,
  102 115u/12, Short Comb 90u/3, 101 78u/14, B1 family ~86u, Tek ~50u, El Jefe 5u/2, SBS 3u/3.
- **Live-store recheck 2026-11-11:** `browser.open` on
  `https://ikonrazors.com/products.json?limit=250` returned HTTP 429 (upstream,
  3 attempts). A read-only `browser.browse` recovery was dispatched
  (task browser-task:f1296ef2-336b-57af-9254-8ad189f41afe); result pending at
  prep time — the delivery agent must confirm OG1/B1/X3/Tek/Short Comb listings
  from that handoff before presenting the decision, or present with the
  2026-11-08 / 2026-11-10 verifications cited instead.
- **Revised harvest shape for the user's decision:** the original 7 heads
  (B1 Standard, B1 Deluxe, B1 OSS, B1 Slant, X3, Tek, Short Comb; ~366u/~59%)
  PLUS a new OG1 entry folding the 101 clusters (~78u) → ~444u (~72% of 621),
  with an El Jefe AC entry owed separately and 102/SBS left to the ordinary queue.
  Guards from the original note still apply (B1 Tech stays B1; bare "Tech" loose
  to Tek only; Maggard/Weber/DE89 heads on iKon handles are not iKon products;
  do not fold ikon-b1oss blindly into B1 Standard; verify ikon-b1-oss-slant).

- **Live-store recheck LANDED 2026-11-11 11:55–11:59 CST** (browser.browse,
  browser-task:f1296ef2-336b-57af-9254-8ad189f41afe): 26 products, all nine
  harvest products listed with prices matching individual product JSONs —
  OG1 Head $35 avail, OG1 Razor $44.99 avail, B1 Standard Head $79.99 avail,
  B1 Open Comb Deluxe Head $79.99 avail, B1 OSS Head $79.99 avail,
  B1 Slant Head $100 listed/unavailable, X3 Slant Head $50 listed/unavailable,
  Tek Head $50 listed/unavailable, Short Comb Head $35 avail.
  updated_at 2026-11-11 ~12:56–12:59 -05:00. Availability from main-feed variant field only.
