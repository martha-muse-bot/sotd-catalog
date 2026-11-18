#!/usr/bin/env python3
"""Generalized build: parse every raw thread JSON for a year, write combined
JSON + CSV in the 2026 schema, and print year stats incl. day coverage.

Usage: python3 build_year.py 2025
Writes: sotd_<year>_full.json, sotd_<year>_full.csv
"""
import sys, json, glob, csv, datetime
sys.path.insert(0, '.')
from sotd_parser import normalize_all

YEAR = int(sys.argv[1])

CANON_COLS = ["thread_date", "thread_title", "author", "created_utc",
              "razor", "blade", "blade_uses",
              "brush", "soap", "preshave", "aftershave", "fragrance",
              "bowl", "rating", "notes"]

def main():
    files = sorted(glob.glob(f'raw/{YEAR}-*.json'))
    seen, combined = set(), []
    thread_days = set()
    n_threads = 0
    for f in files:
        d = json.load(open(f))
        tid = d["thread"]["id"]
        if tid in seen:
            continue
        seen.add(tid)
        n_threads += 1
        thread_days.add(d["thread"]["date"])
        comments = [dict(c) for c in d["comments"]]
        for c in comments:
            c.setdefault("thread_id", d["thread"]["id"])
            c.setdefault("thread_title", d["thread"]["title"])
            c.setdefault("thread_date", d["thread"]["date"])
        combined.extend(normalize_all(comments))

    json.dump(combined, open(f"sotd_{YEAR}_full.json", "w"), indent=1, ensure_ascii=False)
    with open(f"sotd_{YEAR}_full.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CANON_COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(combined)

    entry_days = {e["thread_date"] for e in combined}
    all_days = []
    d0 = datetime.date(YEAR, 1, 1)
    while d0.year == YEAR:
        all_days.append(d0.isoformat())
        d0 += datetime.timedelta(days=1)
    days_with_threads = [d for d in all_days if d in thread_days]
    days_missing = [d for d in all_days if d not in thread_days]
    authors = {e["author"] for e in combined}
    print(f"SUMMARY year={YEAR} threads={n_threads} entries={len(combined)} "
          f"authors={len(authors)} days_with_threads={len(days_with_threads)}/{len(all_days)} "
          f"coverage={100.0*len(days_with_threads)/len(all_days):.1f}%")
    print(f"days with threads but no parsed entries: "
          f"{sorted(thread_days - entry_days) or 'none'}")
    print(f"DAYS_MISSING {json.dumps(days_missing)}")

if __name__ == "__main__":
    main()
