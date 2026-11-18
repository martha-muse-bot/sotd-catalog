---
id: nmrs-pr-review-watch
title: nmrs PR review watch
enabled: true
owner: goal:sotd-canonical-product-catalog
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 08:30:00
delivery:
  - chat_id: cb2a7a82-5389-428b-9380-dcb02ff5eb26
metadata:
  tags: [cron:exact-time]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: en-US
---
Daily nmrs PR review watch for Jim's SOTD catalog give-back work. Each morning, check whether nmrs has reviewed, commented on, merged, or closed any open PR from the martha-muse-bot fork to nmrs/sotd-pipeline — so maintainer feedback never sits unnoticed again. This watch READS ONLY: it never opens, edits, or closes a PR, and it never pushes anything.

Read first, every run:
- `~/workspace/custom-connectors/custom.github-nmrs/CONNECTOR.md` and follow it exactly. All GitHub work goes through the `call` function in `~/workspace/custom-connectors/custom.github-nmrs/bin/github.py` against api.github.com only. Never put a token, key, or credential in a command argument, environment variable, file, or log.
- The state file `~/workspace/goals/sotd-canonical-product-catalog/hidden_files/nmrs_pr_review_watch_state.md`, which records the last-seen review/comment/merge state per PR.

Each run:
1. List the open PRs from martha-muse-bot/sotd-pipeline to nmrs/sotd-pipeline (currently #31–#36; include any newer ones).
2. For each, fetch its reviews and comments via the API and compare against the state file.
3. Report ONLY genuinely new nmrs activity since the last check: new reviews (especially changes-requested), new comments, merges, or closures — one message, per PR, with the blocking item stated plainly. If nothing new, stay silent: no message, no report.
4. Update the state file with anything reported (PR, reviewer, timestamp, state) so the next run does not re-report it. Never delete state entries; append.

Stop condition: none set by this schedule — it is standing daily coverage the user approved 2026-11-17. If the PR channel closes (no open PRs and no new PRs for a sustained period), say so in a run report and ask whether to disable it rather than disabling it silently.
