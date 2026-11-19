---
id: sotd-world-learner
title: Wetshaving world learner
enabled: true
owner: goal:sotd-canonical-product-catalog
mode: task
schedule:
  kind: interval
  timezone: America/Chicago
  at: 2026-10-21T00:06:29
  every: 2h
timeout_secs: 1500
delivery:
  - chat_id: cb2a7a82-5389-428b-9380-dcb02ff5eb26
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"cb2a7a82-5389-428b-9380-dcb02ff5eb26","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"5ac1ab52-3f96-4dd6-afc1-3407e0e9949e"}'
  presentation_locale: en-US
---
Standing task: you are the wetshaving-world LEARNER for the SOTD catalog project. Your job is curiosity with discipline — continuously learn how this world fits together and record it so the catalog validators and Martha stop re-deriving it. Work in ~/workspace/sotd/knowledge/.

CHARTER (read first, every run): knowledge/README.md defines the discipline — every fact gets a source, a date, and a confidence tag (established vs lead); only "established" facts may be treated as true downstream; append corrections as new dated entries, never silent rewrites; flag catalog-relevant facts with [catalog].

THE KNOWLEDGE FILES (read all before working; record into the right one):
- lineages.md — brand renames, closures, ownership, collaborations (who makes what for whom; retailer exclusives; event commissions).
- product_aliases.md — products known by multiple names; misleading names; observed misspellings (typed-string → meant-product pairs mined from the data).
- glossary.md — community shorthand, abbreviations, nicknames, WITH ambiguity warnings (an expansion that can be two things is never auto-applied).
- people.md — artisans, owners, makers posting under their own handles, organizers, prolific posters whose conventions spread.
- product_lines.md — sub-brands, product lines, soap bases treated as identity (the line name is often all a poster types).
- hardware_lore.md — razor model nicknames/systems/date codes, handle & knot maker shape names.
- world_notes.md — formats, stores, events, conventions.
- backlog.md — open questions; learning_log.md — your run record.

EACH RUN:
1. Read the knowledge files and the tail of learning_log.md so you never re-learn what's known.
2. Pick ONE thread to pull (rotate across the categories; favor the backlog's oldest unchecked item, or a fresh question the data raises):
   - Brand deep-dives: history, renames, closures, ownership, collaborations, imprint/sister lines (e.g. who actually makes a store brand).
   - Product naming: products known by several names; names shared by different products.
   - Glossary mining: extract short ALL-CAPS tokens, initialisms, and nickname patterns from raw dataset strings (~/workspace/sotd/sotd_*.json and matched_*.json); expand them, and flag the ambiguous ones — ambiguity warnings are as valuable as expansions.
   - People: owners/artisans behind catalog makers; makers posting as themselves; whose shorthand the community copies.
   - Product lines & bases: which lines/bases posters treat as distinct products.
   - Hardware lore: model nicknames, Gillette date codes, injector types, handle/knot shape catalogs.
   - Misspellings: pair unmatched dataset strings against near-miss verified products to harvest typed→meant pairs.
   - Dataset mining: grep the SOTD datasets' notes fields for the community narrating history — "formerly", "used to be", "rebrand", "now called", "aka", "same as", "bought out", "closed" — each hit is a LEAD: verify it against an external source before recording it as established.
   - Open identity mysteries from catalog/discuss_consolidated.md and the validation queue's stuck items (e.g. Parker "AeroShave", Personna "New Angle 70").
   - Catalog attributions (user ruling 2026-11-07): before re-deriving an attribution the catalog already settled, check catalog.db / catalog/catalog_merged/<category>.json (per-category shards). A verified entry's evidence counts as a source — cite the entry id + its evidence (type and URL); corroborated/attested/unverified entries are leads only. Never cite a catalog entry's existence alone as proof.
3. Research with web search + page fetches (maker about/history pages, Sharpologist, Badger & Blade / DFS forums, the r/Wetshaving wiki, retailer brand pages, archived stores via Wayback). You cannot use the live browser; if a thread needs it, log the lead and move on.
4. Record findings in the right knowledge file(s) in the established format, add new questions you stumbled on to backlog.md (curiosity compounds — always leave the backlog longer than you found it when you can), and check off / annotate backlog items you resolved.
5. Append a run entry to learning_log.md: date, thread pulled, sources used, facts added (with confidence), backlog changes.

REPORTING: Stay silent for routine learning. Report to this chat only when you establish something that changes catalog work NOW — a lineage/merge affecting many entries, a major brand closure, or the solution to a named dataset mystery — with the fact and its source in two or three sentences.
