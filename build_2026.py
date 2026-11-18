#!/usr/bin/env python3
"""Build the full-year 2026 SOTD dataset: parse every raw thread JSON,
write combined JSON + CSV, and print year stats."""
import sys, json, glob, re, csv
from collections import Counter
sys.path.insert(0, '.')
from sotd_parser import normalize_all

CANON_COLS = ["thread_date", "thread_title", "author", "created_utc",
              "razor", "blade", "blade_uses",
              "brush", "soap", "preshave", "aftershave", "fragrance",
              "bowl", "rating", "notes"]

def main():
    files = sorted(glob.glob('raw/2026-*.json'))
    # skip the Oct 13-19 browser files? No — include everything; dedupe by thread id
    seen, combined = set(), []
    per_thread = []
    for f in files:
        d = json.load(open(f))
        tid = d["thread"]["id"]
        if tid in seen:
            continue
        seen.add(tid)
        comments = d["comments"]
        # copy each comment (leaving the raw files untouched) and stamp thread
        # identity on the copies actually passed to the parser
        comments = [dict(c) for c in comments]
        for c in comments:
            c.setdefault("thread_id", d["thread"]["id"])
            c.setdefault("thread_title", d["thread"]["title"])
            c.setdefault("thread_date", d["thread"]["date"])
        es = normalize_all(comments)
        combined.extend(es)
        per_thread.append((d["thread"]["date"], d["thread"]["title"], len(es)))

    json.dump(combined, open("sotd_2026_full.json", "w"), indent=1, ensure_ascii=False)
    with open("sotd_2026_full.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CANON_COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(combined)
    print(f"threads: {len(per_thread)}  entries: {len(combined)}")

    def canon(v):
        v = v.lower()
        v = re.sub(r"\([^)]*\)", "", v)
        return re.sub(r"\s+", " ", v).strip(" -–—.,;:")
    def short2(v):
        return " ".join(canon(v).split()[:2])

    soaps, razors, blades, perday = Counter(), Counter(), Counter(), Counter()
    for e in combined:
        perday[e["thread_date"]] += 1
        if e.get("soap"): soaps[short2(e["soap"])] += 1
        if e.get("razor"): razors[short2(e["razor"])] += 1
        if e.get("blade"): blades[short2(e["blade"])] += 1

    missing_days = []
    import datetime
    d0 = datetime.date(2026, 1, 1)
    while d0 <= datetime.date(2026, 10, 19):
        if d0.isoformat() not in perday:
            missing_days.append(d0.isoformat())
        d0 += datetime.timedelta(days=1)
    print("days missing from dataset:", missing_days or "none")
    print("\ntop soaps:")
    for s, c in soaps.most_common(12): print(f"  {c:4d}  {s}")
    print("\ntop razors:")
    for s, c in razors.most_common(12): print(f"  {c:4d}  {s}")
    print("\ntop blades:")
    for s, c in blades.most_common(12): print(f"  {c:4d}  {s}")
    print(f"\nwith gear: {sum(1 for e in combined if e.get('razor') or e.get('soap'))}/{len(combined)}")
    print("blade use counts:", sum(1 for e in combined if e.get("blade_uses")))
    print("unique authors:", len({e["author"] for e in combined}))

if __name__ == "__main__":
    main()
