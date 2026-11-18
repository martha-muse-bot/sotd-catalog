---
id: sotd-anecdotal-watch
title: Anecdotal product weekly watch
enabled: true
owner: goal:sotd-canonical-product-catalog
mode: task
schedule:
  kind: weekly
  timezone: '@user.current'
  time: 11:15:00
  dow: [Mon]
delivery:
  - chat_id: cb2a7a82-5389-428b-9380-dcb02ff5eb26
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"8dde535f-cbc0-4a9d-96f8-c6d9e018f54f","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"5ac1ab52-3f96-4dd6-afc1-3407e0e9949e"}'
  presentation_locale: en-US
---
Weekly anecdotal-product watch (P-23). Anecdotal entries are real-but-unvalidatable products (prototypes, one-offs); the validator loop spends no routine research on them, but a usage explosion may mean one hit the market — this watch catches that.

1. Run: python3 ~/workspace/sotd/catalog/anecdotal_watch.py
   It compares current matched uses per anecdotal entry (status='anecdotal' in catalog.db, counted across ~/workspace/sotd/matched_*.json) against the watermark at ~/workspace/sotd/catalog/work/anecdotal_watch_state.json, and prints candidates with NEW uses since last check (top 3 by delta) with recent example posts. Entries with zero new uses are already filtered out — never research those.
2. If no candidates: run python3 ~/workspace/sotd/catalog/anecdotal_watch.py --commit (updates the watermark) and end SILENTLY. No user report.
3. Before researching a candidate, sanity-check its recent examples (authors/dates in the script output): a burst of NEW authors posting it is the launch signal; the same author reposting is not. Skip candidates that are clearly not launches, note why in the daily log.
4. For each remaining candidate (max 3): quick web research — 2-3 searches like "[brand] [product] buy", "[brand] [product] release", maker-site search. Question: has this product gone into production or gained a maker/retailer listing since it was marked anecdotal?
5. If primary evidence found (maker/retailer product page): promote the entry per the standing promotion procedure — verified id <Category>/<brand>-<product>, evidence recorded, aliases/attestation carried, delete the anecdotal entry, export via sotd_db.export_json (take catalog/.catalog.lock for writes; abort writes if the lock is fresh). Report the promotion to the user with the evidence.
6. If the evidence is ambiguous (looks like a launch but not confirmable): bring it to the user as a decision item — one single message with evidence report, recommendation, and options.
7. If nothing found: run anecdotal_watch.py --commit and end SILENTLY.
8. Routine notes go to ~/memory/YYYY-MM-DD.md. Do not edit MEMORY.md.

Rules: never widen this into routine re-research of anecdotal entries — the delta filter is the whole point. Do not invent a launch from thin evidence; the bar for promotion is the same primary-evidence standard as always.
