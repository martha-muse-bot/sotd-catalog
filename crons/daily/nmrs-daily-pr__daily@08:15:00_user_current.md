---
id: nmrs-daily-pr
title: Daily nmrs PR
enabled: true
owner: goal:sotd-canonical-product-catalog
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 08:15:00
timeout_secs: 3600
delivery:
  - chat_id: cb2a7a82-5389-428b-9380-dcb02ff5eb26
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cb2a7a82-5389-428b-9380-dcb02ff5eb26","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"45275315-dced-4e7e-a837-a71f10e0995d"}'
  presentation_locale: en-US
---
Daily attempt at two upstream PRs to nmrs/sotd-pipeline — one catalog, one code — for Jim's SOTD catalog give-back work. Aim for two PRs per day, one per lane, worked independently; "attempt" is load-bearing — a lane with no settleable item is a blocker report for that lane, never a forced or thin PR, and a blocked lane never blocks the other lane.

Read first, every run:
- `~/workspace/custom-connectors/custom.github-nmrs/CONNECTOR.md` and follow it exactly. All GitHub work goes through the `call` function in `~/workspace/custom-connectors/custom.github-nmrs/bin/github.py` against api.github.com only.
- The queue: `~/workspace/goals/sotd-canonical-product-catalog/hidden_files/nmrs_pr_queue.md`. It holds the ordered candidates per lane, their evidence notes, and the dead list. Work each lane in order.

Rules that bind every run:
- ONE correction (or one coherent pattern fix) per PR. Never batch unrelated corrections.
- TWO LANES: work one catalog item AND one code item each run, independently. Each lane's PR is judged on its own evidence (catalog) or tests (code). Report both lanes every run: PR link and/or blocker.
- Open a PR only at 100% confidence with evidence in hand. If the evidence does not settle the item, mark it blocked in the queue with what would unblock it and report that instead. Never lower the bar to fill the quota.
- TRUE nmrs match semantics: razor and soap patterns sort by pattern-string length descending, then first match wins (YAML order only breaks equal-length ties). Blade patterns sort by the specificity score in `blade_matcher._calculate_pattern_score` (non-DE formats first, then length, non-optional parts, complexity, boundaries). Brush matching is strategy-ordered, not one global sorted list. Never propose a YAML reorder as a fix: under the length sort it is a no-op.
- Work ONLY through the fork `martha-muse-bot/sotd-pipeline`. Never push to upstream directly. Never put a token, key, or credential in a command argument, environment variable, file, or log. Keep redirects disabled. On a 401 or 403, check the request first; do not route around a block by switching tokens or endpoints. After any failed or uncertain write, check current state (GET the branch or PR) before retrying — never duplicate a completed action.
- API-only workflow (no git push with credentials): sync the fork's master with upstream via the merge-upstream API; create the branch ref from the synced master SHA; GET the target file from upstream master (content plus blob sha); PUT the edited file to the new branch with a commit message stating what changed and the evidence; open the PR with head `martha-muse-bot:<branch>` and base `master`, with problem, evidence, change, and verification in the body; GET the PR to verify it opened.
- Code changes (as opposed to catalog YAML changes): run the relevant tests in the local clone (`~/workspace/sotd/external/sotd-pipeline`) when feasible. Do not open a code PR without passing tests or a clear statement of what was verified.
- Leave the clone clean: this run shares `~/workspace/sotd/external/sotd-pipeline` with the weekly sync job, whose `git pull --ff-only` fails on uncommitted edits. At the end of every run, restore each file you modified there (`git checkout -- <path>`) and delete each file you created there. Never leave the working tree dirty.
- Update the queue file every run: mark the item done with its PR link, or blocked with the reason and what would unblock it. The chat report is the other half of the record. Do not edit MEMORY.md from a run.

Each run:
1. Read the connector doc and the queue. Pick the top CATALOG item and the top CODE item not marked done or blocked-awaiting-user.
2. Do the homework for each item (read the relevant nmrs patterns from the local clone for review, but always GET the file from upstream master via the API for the actual edit, so you never edit stale content). Code items additionally require relevant tests run in the local clone before opening.
3. If the homework settles an item, carry out the API workflow above and verify the PR. Open zero, one, or two PRs as the evidence allows — never force either lane.
4. Update the queue file, then report in your final message, per lane: either the PR link with what changed and the evidence, or a short blocker report naming the item, why it is held, and what would unblock it (for example, a decision or a piece of evidence Jim would need to supply).
