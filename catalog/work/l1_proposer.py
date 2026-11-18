#!/usr/bin/env python3
"""L1 proposer: typo/synonym proposals over the CURRENT pending backlog.

Proposals ONLY — writes nothing to the catalog DB. Output is
catalog/work/l1_proposals_2026-10-28.json for validator review.

Two signals, same category only:
  (a) token-Jaccard against verified entries (and pending peers):
      >= 0.75 -> 'candidate' (close synonym/variant)
      [0.55, 0.75) -> 'nearest' (nearest_verified hint, NOT a merge:
      cf. the Gillette Blue boundary — a conspicuously omitted
      discriminator is itself signal, so nearest never auto-merges)
  (b) character-level typo: a pair sharing >= 1 token, with <= 2
      unmatched tokens on each side, where an unmatched token pair
      qualifies as a typo (bounded Levenshtein):
        distance 1, any length >= 3
        distance 2, min length >= 5
        distance 3, min length >= 6
      Short scent words are protected by the length floors
      ('rose'/'roam', distance 2 at length 4, does NOT qualify).
  (c) bare-token pass: a single-token cluster string with NO exact
      verified token match in its category gets edit-compared
      against same-first-letter verified/pending tokens
      (catches 'gilette' -> 'gillette' where token-sharing finds
      nothing). Correct bare tokens are skipped by the exact-match
      filter, so this pass only fires for unknown tokens.

Guardrails:
  - category always in the key; blades additionally need format
    compatibility (cluster format None or == target format).
  - disputed/hold-list ids and needs-review clusters never proposed
    (neither as source nor as target).
  - group conflict (both groups set and different) demotes a
    verified-target proposal to 'nearest' at best, never 'candidate';
    it is recorded with a group_conflict flag.
  - generic tokens (posting list > 1500) are not used for candidate
    generation: pairs sharing only a generic token are low-value
    and fail the unmatched-token cap anyway.
  - per source, top 8 proposals kept (Jaccard desc, then kind).

Plain normalization only (N + strip 'and' + category noun) — NO
brand-shorthand/initials expansion, so typos are visible, not
masked. Alias sets per entry capped at 40 (canonical first).
"""
import json
import re
import sys
from collections import Counter, defaultdict
from html import unescape

sys.path.insert(0, "/home/hatch/workspace/sotd/catalog")
import sotd_db  # noqa: E402

CAT = "/home/hatch/workspace/sotd/catalog"
WORK = f"{CAT}/work"
DATE = "2026-10-28"
EXCLUDED = {
    "unverified/blade/schick",
    "unverified/blade/parker-premium-platinum",
    "unverified/soap/woolly-wash-soapery-tranquility",
    "unverified/soap/catie-s-bubbles-maggard-meet-exclusive",
    "unverified/brush/clubman-pinaud-synthetic",
    "unverified/soap/a-e-cody-soap-insp-by-maullu-nero-e-rosso",
    "unverified/soap/barrister-and-mann-soapmakers-of-awesometown-soap",
}
CATNOUN = {
    "soap": "soap",
    "aftershave": "aftershave",
    "fragrance": "fragrance",
    "blade": "blade",
    "razor": "razor",
    "brush": "brush",
}
GENERIC_FREQ = 1500
MAX_SETS = 40
KEEP_PER_SOURCE = 8


def N(s):
    if not s:
        return ""
    s = unescape(str(s)).lower()
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def lev_bounded(a, b, maxd):
    if abs(len(a) - len(b)) > maxd:
        return maxd + 1
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        rowmin = cur[0]
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
            if cur[j] < rowmin:
                rowmin = cur[j]
        if rowmin > maxd:
            return maxd + 1
        prev = cur
    return prev[-1] if prev[-1] <= maxd else maxd + 1


def typo_token_pair(a, b):
    """Return distance if (a, b) qualifies as a typo pair, else None."""
    m = min(len(a), len(b))
    if m < 3:
        return None
    if abs(len(a) - len(b)) > 3:
        return None
    d = lev_bounded(a, b, 3)
    if d == 1:
        return d
    if d == 2 and m >= 5:
        return d
    if d == 3 and m >= 6:
        return d
    return None


def token_sets(entry):
    noun = CATNOUN.get(entry["category"])
    strs = []
    if entry.get("brand") and entry.get("product"):
        strs.append(entry["brand"] + " " + entry["product"])
    if entry.get("label"):
        strs.append(entry["label"])
    strs.extend(entry.get("aliases") or [])
    out, seen = [], set()
    for s in strs:
        toks = frozenset(
            t for t in N(s).split() if t != "and" and t != noun
        )
        if toks and toks not in seen:
            seen.add(toks)
            out.append(toks)
    return out[:MAX_SETS]


def main():
    conn = sotd_db.connect(read_only=True)
    entries = sotd_db.all_entries(conn)
    qstates = {}
    for i in sotd_db.all_queue(conn):
        qstates[i.get("ref")] = i.get("state")
    conn.close()

    eligible = {}
    for e in entries:
        if e["id"] in EXCLUDED or e.get("status") == "needs-review":
            continue
        eligible[e["id"]] = e
    verified = {i: e for i, e in eligible.items()
                if e.get("status") == "verified"}
    pending = {i: e for i, e in eligible.items()
               if e.get("status") in ("unverified", "corroborated", "attested")
               and qstates.get(i) == "pending"}
    print(f"eligible: verified {len(verified)}, pending {len(pending)}")

    sets = {i: token_sets(e) for i, e in eligible.items()}
    # inverted index (category, token) -> [(entry_id, set_idx)]
    index = defaultdict(list)
    for eid, ss in sets.items():
        cat = eligible[eid]["category"]
        for si, s in enumerate(ss):
            for t in s:
                index[(cat, t)].append((eid, si))
    generic = {k for k, v in index.items() if len(v) > GENERIC_FREQ}
    print(f"index tokens: {len(index)}, generic skipped: {len(generic)}")
    for k in generic:
        del index[k]

    # per-category verified token vocabulary, grouped by first letter,
    # plus token -> verified entries (for the bare pass)
    verified_tokens = defaultdict(set)
    verified_token_entries = defaultdict(list)
    for eid, e in verified.items():
        toks = set().union(*sets[eid]) if sets[eid] else set()
        for t in toks:
            verified_tokens[e["category"]].add(t)
            verified_token_entries[(e["category"], t)].append(eid)
    verified_by_letter = {}
    for cat, toks in verified_tokens.items():
        d = defaultdict(list)
        for t in toks:
            d[t[0]].append(t)
        verified_by_letter[cat] = d
    for (cat, t), eids in verified_token_entries.items():
        eids.sort(
            key=lambda i: -((eligible[i].get("attestation") or {}).get("uses")
                            or 0)
        )

    counts = Counter()
    proposals = {}

    def fmt_compatible(src, tgt):
        if src["category"] == "blade" and src.get("format") and tgt.get("format"):
            return src["format"] == tgt["format"]
        return True

    for sid, src in pending.items():
        best = {}  # target_id -> proposal dict
        for s in sets[sid]:
            cand = set()
            for t in s:
                cand.update(index.get((src["category"], t), []))
            for (tid, ti) in cand:
                if tid == sid:
                    continue
                tgt = eligible[tid]
                tset = sets[tid][ti]
                inter = s & tset
                if not inter:
                    continue
                union = s | tset
                j = len(inter) / len(union)
                us, ut = s - tset, tset - s
                typo = None
                if len(us) <= 2 and len(ut) <= 2:
                    for a in us:
                        for b in ut:
                            d = typo_token_pair(a, b)
                            if d is not None:
                                typo = (a, b, d)
                                break
                        if typo:
                            break
                if j < 0.55 and not typo:
                    continue
                if not fmt_compatible(src, tgt):
                    continue
                cur = best.get(tid)
                if cur is None or j > cur["jaccard"]:
                    gconf = bool(
                        src.get("brand_group")
                        and tgt.get("brand_group")
                        and src["brand_group"] != tgt["brand_group"]
                    )
                    if j >= 0.75:
                        kind = "nearest" if gconf else "candidate"
                    elif typo:
                        kind = "typo"
                    else:
                        kind = "nearest"
                    best[tid] = {
                        "target": tid,
                        "target_status": tgt.get("status"),
                        "jaccard": round(j, 3),
                        "kind": kind,
                        "typo_tokens": list(typo[:2]) if typo else None,
                        "typo_distance": typo[2] if typo else None,
                        "group_conflict": gconf,
                    }
                elif typo and cur["typo_tokens"] is None:
                    cur["typo_tokens"] = list(typo[:2])
                    cur["typo_distance"] = typo[2]
                    if cur["kind"] == "nearest" and cur["jaccard"] < 0.75:
                        cur["kind"] = "typo"
        # bare-token pass: single-token source sets with no exact
        # verified token match in this category. The corrected token
        # is proposed (not a single entry: a bare typo has no
        # context, so up to 3 most-used verified entries carrying
        # the corrected token are listed and the validator uses
        # post context to pick).
        for s in sets[sid]:
            if len(s) != 1:
                continue
            tok = next(iter(s))
            if tok in verified_tokens[src["category"]]:
                continue
            cands = []
            for vtok in verified_by_letter[src["category"]].get(tok[0], []):
                d = typo_token_pair(tok, vtok)
                if d is not None:
                    cands.append((d, vtok))
            if not cands:
                continue
            best_d = min(d for d, _ in cands)
            for d, vtok in sorted(cands):
                if d != best_d:
                    continue
                for tid in verified_token_entries[
                        (src["category"], vtok)][:3]:
                    if not fmt_compatible(src, verified[tid]):
                        continue
                    if tid not in best:
                        best[tid] = {
                            "target": tid,
                            "target_status": "verified",
                            "jaccard": None,
                            "kind": "typo-bare",
                            "typo_tokens": [tok, vtok],
                            "typo_distance": d,
                            "group_conflict": False,
                        }
        if not best:
            continue
        plist = sorted(
            best.values(),
            key=lambda p: (-(p["jaccard"] or 0),
                           {"candidate": 0, "typo": 1, "typo-bare": 1,
                            "nearest": 2}[p["kind"]]),
        )[:KEEP_PER_SOURCE]
        proposals[sid] = plist
        for p in plist:
            counts[f"proposals_{p['kind']}"] += 1
            counts[f"proposals_{p['kind']}_{p['target_status']}"] += 1
        counts["sources_with_proposals"] += 1

    by_cat = Counter()
    for sid in proposals:
        by_cat[eligible[sid]["category"]] += 1
    out = {
        "date": DATE,
        "counts": dict(counts),
        "sources_by_category": dict(by_cat),
        "pending_sources": len(pending),
        "proposals": proposals,
    }
    path = f"{WORK}/l1_proposals_{DATE}.json"
    with open(path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(dict(counts), indent=1))
    print("sources by category:", dict(by_cat))
    print(f"report: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
