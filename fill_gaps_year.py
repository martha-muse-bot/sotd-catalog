#!/usr/bin/env python3
"""Generalized gap-fill: for days missing their expected SOTD thread count,
re-query without the author filter to catch human-posted threads (AutoMod
failures). Event months detected empirically from the data.

Usage: python3 fill_gaps_year.py 2025
Reads/writes: threads_<year>.json
"""
import requests, time, json, datetime, sys
from collections import Counter

BASE = "https://arctic-shift.photon-reddit.com/api"
S = requests.Session()
DAY = 86400
YEAR = int(sys.argv[1])
OUT = f"threads_{YEAR}.json"
START = int(datetime.datetime(YEAR, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
END = int(datetime.datetime(YEAR + 1, 1, 1, tzinfo=datetime.timezone.utc).timestamp())

def get(path, params, retries=6):
    for i in range(retries):
        try:
            r = S.get(BASE + path, params=params, timeout=120)
            if r.status_code == 200:
                j = r.json()
                if j.get("data") is not None:
                    return j["data"]
        except Exception:
            pass
        time.sleep(5 * (i + 1))
    return None

def is_sotd_title(title):
    t = (title or "").lower()
    return "sotd" in t or "shave of the day" in t

def get_all_posts_day(d0):
    """All subreddit posts for one UTC day, paginating past the 100 cap."""
    out, after = [], d0
    while True:
        batch = get("/posts/search", {
            "subreddit": "Wetshaving", "after": after, "before": d0 + DAY,
            "limit": 100, "sort": "asc",
            "fields": "id,title,created_utc,author,num_comments,link_flair_text"})
        if batch is None:
            return None
        out.extend(batch)
        if len(batch) < 100:
            return out
        after = batch[-1]["created_utc"]
        time.sleep(1)

def main():
    threads = json.load(open(OUT))
    by_day = {}
    for t in threads:
        by_day.setdefault(t["day"], []).append(t)

    month_two = Counter()
    month_days = Counter()
    for day, ts in by_day.items():
        m = int(day.split("-")[1])
        month_days[m] += 1
        if len(ts) >= 2:
            month_two[m] += 1
    event_months = {m for m in month_days if month_two[m] >= 20}
    print(f"event months detected: {sorted(event_months)}", flush=True)
    print(f"days with 2+ threads by month: {dict(sorted(month_two.items()))}", flush=True)

    expected = lambda day: 2 if int(day.split("-")[1]) in event_months else 1

    gaps = []
    d = START
    while d < END:
        day = datetime.datetime.fromtimestamp(d, datetime.timezone.utc).strftime("%Y-%m-%d")
        have = len(by_day.get(day, []))
        if have < expected(day):
            gaps.append((day, have, expected(day)))
        d += DAY
    print(f"{len(gaps)} gap days: {gaps}", flush=True)

    fixed = 0
    for day, have, want in gaps:
        d0 = int(datetime.datetime.strptime(day, "%Y-%m-%d").replace(
            tzinfo=datetime.timezone.utc).timestamp())
        posts = get_all_posts_day(d0)
        if posts is None:
            print(f"{day}: query failed, still gap", flush=True)
            continue
        found = [p for p in posts
                 if is_sotd_title(p.get("title"))
                 and p["id"] not in {t["id"] for t in by_day.get(day, [])}]
        for p in found:
            p["day"] = day
            p["found_via"] = "gap_fill_human_post"
            threads.append(p)
        if found:
            fixed += 1
            print(f"{day}: found {len(found)} extra thread(s): "
                  f"{[(p['author'], p['title'][:60]) for p in found]}", flush=True)
        else:
            print(f"{day}: no SOTD thread found even unfiltered "
                  f"(checked {len(posts)} posts)", flush=True)
        time.sleep(3)

    json.dump(threads, open(OUT, "w"), indent=1)
    print(f"gap-fill done, fixed {fixed}/{len(gaps)} days, total threads={len(threads)}", flush=True)

if __name__ == "__main__":
    main()
