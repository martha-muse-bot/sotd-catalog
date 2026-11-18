---
id: sotd-nmrs-sync
title: nmrs SOTD-pipeline sync
enabled: true
owner: goal:sotd-canonical-product-catalog
mode: task
schedule:
  kind: weekly
  timezone: '@user.current'
  time: 07:15:00
  dow: [Mon, Thu]
delivery:
  - chat_id: cb2a7a82-5389-428b-9380-dcb02ff5eb26
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cb2a7a82-5389-428b-9380-dcb02ff5eb26","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"45275315-dced-4e7e-a837-a71f10e0995d"}'
  presentation_locale: en-US
---
Keep the local clone of the nmrs/sotd-pipeline corroboration source current.

Steps:
1. cd ~/workspace/sotd/external/sotd-pipeline. Read the current HEAD (git rev-parse HEAD) and the contents of .last_synced_commit (the commit the catalog last consumed).
2. git pull --ff-only. If the pull fails (network, divergence), report the failure briefly and stop.
3. If HEAD is unchanged: end quietly, no report.
4. If HEAD changed: run git diff --stat <old>..HEAD -- data/ and count how many entries changed in data/correct_matches/*.yaml and data/*.yaml (added/removed lines are enough). Update .last_synced_commit to the new HEAD. Append one line to ~/workspace/sotd/external/sync_log.md: date, old..new short hashes, changed data files.
5. Report to the chat ONLY if files under data/ changed: one line — new commit short hash, which catalog/match files changed, approximate added mapping lines. Stay silent if only code/webui/docs changed.

This job only maintains the clone; applying new mappings as catalog corroborations happens in the separate DB corroboration pass, not here.
