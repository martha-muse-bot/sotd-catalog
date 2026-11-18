#!/usr/bin/env python3
"""Lather Games sweep: early LG threads were human-posted with titles like
'Lather Games Thread - June 2nd, 2019: <theme>' (no 'SOTD' in title), so both
the index and the AutoModerator pull can miss them. Scans every day of June
and July unfiltered and unions in any 'lather games'-titled post not already
in threads_<year>.json. (The API's title search times out; day windows work.)
Usage: python3 lg_sweep.py 2019"""
import requests, time, json, datetime, sys
BASE = "https://arctic-shift.photon-reddit.com/api"
S = requests.Session()
YEAR = int(sys.argv[1])
DAY = 86400
def get(params, retries=6):
    for i in range(retries):
        try:
            r = S.get(BASE + "/posts/search", params=params, timeout=120)
            if r.status_code == 200 and r.json().get("data") is not None:
                return r.json()["data"]
        except Exception: pass
        time.sleep(5 * (i + 1))
    return None
def all_posts_day(d0):
    out, after = [], d0
    while True:
        batch = get({"subreddit":"Wetshaving","after":after,"before":d0+DAY,"limit":100,
                     "sort":"asc","fields":"id,title,created_utc,author,num_comments,link_flair_text"})
        if batch is None: return None
        out.extend(batch)
        if len(batch) < 100: return out
        after = batch[-1]["created_utc"]; time.sleep(1)
threads = json.load(open(f"threads_{YEAR}.json"))
have = {t["id"] for t in threads}
added, failed = 0, []
d = datetime.date(YEAR, 6, 1)
while d <= datetime.date(YEAR, 7, 31):
    d0 = int(datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc).timestamp())
    posts = all_posts_day(d0)
    if posts is None:
        failed.append(d.isoformat()); d += datetime.timedelta(days=1); continue
    for p in posts:
        if "lather games" in (p.get("title") or "").lower() and p["id"] not in have:
            p["day"] = d.isoformat(); p["found_via"] = "lg_day_sweep"
            threads.append(p); have.add(p["id"]); added += 1
            print(f"  ADDED {d} {p['id']} {p['author']} | {p['title']} | c:{p['num_comments']}", flush=True)
    d += datetime.timedelta(days=1)
    time.sleep(1)
json.dump(threads, open(f"threads_{YEAR}.json","w"), indent=1)
print(f"lg sweep done: added {added}, failed days={failed}, total={len(threads)}")
