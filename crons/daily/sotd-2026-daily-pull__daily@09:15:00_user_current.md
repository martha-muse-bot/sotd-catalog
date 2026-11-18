---
id: sotd-2026-daily-pull
title: SOTD 2026 daily pull
enabled: true
owner: goal:sotd-canonical-product-catalog
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 09:15:00
delivery:
  - chat_id: 8dde535f-cbc0-4a9d-96f8-c6d9e018f54f
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"8dde535f-cbc0-4a9d-96f8-c6d9e018f54f","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"5ac1ab52-3f96-4dd6-afc1-3407e0e9949e"}'
  presentation_locale: en-US
---
Daily SOTD 2026 keeper. Run `python3 ~/workspace/sotd/pull_daily_2026.py` from the workspace. It pulls any missing 2026 days (capped at 7 per run) from the Arctic Shift archive API and rebuilds sotd_2026_full.json/.csv. It is idempotent: days that already have raw files are skipped, and a day that fails stays missing for the next run. After the run, verify with `python3 ~/workspace/sotd/pull_daily_2026.py --check`. Then re-run the matcher so the day's entries are normalized the same morning, independent of validator batches: `python3 match_all.py 2022 2024 2025 2026` in `~/workspace/sotd/catalog` (~60s) — this regenerates the matched files and `coverage_report.md`. If new days were pulled, report briefly which days were pulled and the rebuilt dataset totals. If a day fails after the script's retries, report the failure plainly, including which days are still missing — do not claim the archive API is down, since past background runs have failed from an egress restriction in the run context rather than the API itself. If nothing was missing, no chat report is needed.
