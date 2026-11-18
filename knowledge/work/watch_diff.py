#!/usr/bin/env python3
"""Diff two watch suffixes' snapshots; print totals, availability and flips."""
import json, glob, sys

D = "/home/hatch/workspace/goals/sotd-canonical-product-catalog/hidden_files/watch-snapshots"

def load(pat):
    out = []
    for f in sorted(glob.glob(f"{D}/{pat}")):
        out += json.load(open(f))["products"]
    return out

def avail(p):
    return any(v.get("available") for v in p.get("variants", []))

def diff(store, po, pn):
    o = {p["handle"]: p for p in load(po)}
    n = {p["handle"]: p for p in load(pn)}
    flips = []
    for h in sorted(set(o) | set(n)):
        if h not in o:
            flips.append((h, "NEW", avail(n[h])))
        elif h not in n:
            flips.append((h, "DELISTED", avail(o[h])))
        elif avail(o[h]) != avail(n[h]):
            flips.append((h, "AVAIL %s->%s" % (avail(o[h]), avail(n[h])), avail(n[h])))
    print(f"{store}: {len(o)} -> {len(n)} products, avail "
          f"{sum(avail(p) for p in o.values())} -> {sum(avail(p) for p in n.values())}")
    for f in flips:
        print("   FLIP:", f)
    return o, n

old_date, old, new_date, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
date = new_date
old_date_g = old_date
diff("B&M", f"barristerandmann_products_{old_date}{old}.json", f"barristerandmann_products_{new_date}{new}.json")
diff("CL", f"chatillonlux_products_{old_date}{old}.json", f"chatillonlux_products_{new_date}{new}.json")
diff("BlackShip", f"blackshipgroomingco_products_{old_date}{old}.json", f"blackshipgroomingco_products_{new_date}{new}.json")
diff("BattleBros", f"battlebrothers_products_{old_date}{old}.json", f"battlebrothers_products_{new_date}{new}.json")
diff("HoM", f"houseofmammoth_products_{old_date}{old}.json", f"houseofmammoth_products_{new_date}{new}.json")
diff("NA", f"nakedarmor_products_{old_date}{old}_p*.json", f"nakedarmor_products_{new_date}{new}_p*.json")
diff("Maggard", f"maggardrazors_products_{old_date}{old}_p*.json", f"maggardrazors_products_{new_date}{new}_p*.json")
hom = load(f"houseofmammoth_products_{new_date}{new}.json")
print("HoM seaforth hits:", [p["handle"] for p in hom
      if "seaforth" in p["handle"].lower() or "seaforth" in (p.get("title") or "").lower()])
