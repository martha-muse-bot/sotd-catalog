---
id: sotd-escalation-queue
title: SOTD escalation queue sweep
enabled: true
owner: goal:sotd-canonical-product-catalog
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 10:15:00
timeout_secs: 10800
delivery:
  - chat_id: cb2a7a82-5389-428b-9380-dcb02ff5eb26
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cb2a7a82-5389-428b-9380-dcb02ff5eb26","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"5ac1ab52-3f96-4dd6-afc1-3407e0e9949e"}'
  presentation_locale: en-US
---
Work the SOTD catalog escalation queue: items the validator loop escalated because only parent-level live-browser checks can resolve them.

Setup (every run):
1. Read ~/workspace/sotd/catalog/validation_README.md first — DB discipline (catalog.db ONLY via catalog/sotd_db.py; respect .catalog.lock: if it is <2h old, end the run quietly; re-fetch entry+queue item before ANY verdict), evidence standard (PRIMARY only: maker/store page, brand social post with product image, SOTD photo with readable label, label-readable YouTube hold-up, set cross-validation; wetshavingdatabase/wsdb are leads only, never primary), and the escalation-queue section.
2. Read the knowledge files listed in the README before researching (established = trusted context, lead = pointer-only).

Each run:
1. Take up to 50 items: state='awaiting_parent' AND parent_kind='browser', ordered by seq (oldest first). parent_kind='decision' items follow the user's 100% rule, not a hands-off rule: at 100% confidence, decide autonomously — apply the verdict, and record the evidence plus the ACTUAL basis in decisions (a prior user ruling with its date, primary evidence, etc.). Never write 'user-approved' or 'User ruled: …' unless the user actually ruled; the Cerberus (2026-10-30) and Dr. Bronner's (2026-10-31) incidents were flagged for approval language written before/without the ruling, not for the verdicts themselves. Below 100% confidence, escalate promptly to the user with a crisp parent_need and then leave the item alone — no verdict, no annotations. The tightening: when confidence isn't clear, the item goes to the user quickly instead of sitting annotated. Just note any new decision-kind items (arrived since the last run) in your report.
2. For each item, read its parent_need and attempts history, then do the browser check with browser.browse (task_id 'new' per item; run independent items in parallel batches). Checks are READ-ONLY: Wayback captures, maker/retailer product pages, eBay listing photos with readable labels, SOTD/imgur photos. Never sign in, never post, never buy. If a check needs a sign-in or a CAPTCHA the browser cannot pass, skip the item and note it.
3. Judge at the 100%-confidence bar (user's operating rule: proceed at 100%, hold uncertainty):
   - Primary evidence settles it: apply the verdict directly via sotd_db (promote/merge per the README taxonomy), record evidence + date in decisions, set the queue state accordingly.
   - Evidence found but identity still uncertain: attach findings to attempts, set state back to 'pending' with a note so the validator loop re-takes it.
   - Nothing found: log what was tried in attempts, keep state 'awaiting_parent', update parent_need if the ask changed.
4. Respect .catalog.lock before every write batch; the validator loop runs concurrently — re-fetch before verdicts.
5. Run export_json() after any writes.

Report in your final message: per item (queue_id + one-line outcome: resolved-promoted / resolved-merged / returned-to-pending / still-blocked + why), escalation-queue depth after the run, and any NEW decision-kind items that arrived (queue_id + the decision question only).
