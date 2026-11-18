#!/usr/bin/env python3
"""Learner misspellings mining, ARTISAN dimension (2026-11-04).

Backlog item (g) from the 2026-11-02 run: the first pass (verified-only
targets) was dominated by mass-market names because verified entries skew
that way. This run restricts targets to artisan-ish entries and re-ranks.

Artisan = verified entries whose brand is NOT on the MASS_MARKET exclusion
list below (judgment call, documented in product_aliases.md run writeup).
The exclusion list covers: razor/blade mass houses, heritage shaving houses,
drugstore/consumer brands, mainstream fragrance houses, mass brush houses,
generic retailers. Wetshaving-specialist retailers (Maggard, WCS, TRC,
Pasteur, Italian Barber, BullGoose) stay IN as artisan-channel targets.

Also writes the FULL unrestricted pair list (all pairs, not just top-400)
for backlog item (a) continuation: misspelling_cands_all_2026-11-04.json.
"""
import json, sqlite3, glob, re, unicodedata
from collections import Counter, defaultdict

BASE = '/home/hatch/workspace/sotd'
OUTDIR = '/home/hatch/workspace/sotd/knowledge/tools'
FIELDS = ['razor', 'blade', 'brush', 'soap', 'aftershave', 'bowl',
          'fragrance', 'preshave']

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-z0-9 ]', ' ', s.lower())
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# --- mass-market / heritage / consumer / retailer brand exclusions (normalized) ---
MASS_MARKET = set(map(norm, [
    # razor / blade mass houses
    'Gillette', 'Schick', 'Wilkinson Sword', 'Personna', 'Astra', 'BIC',
    'Dorco', 'Feather', 'Kai', 'Merkur', 'Mühle', 'Edwin Jagger', 'Parker',
    'Lord', 'Shark', 'Derby', 'Rapira', 'Voskhod', 'Polsilver', 'Wizamet',
    'Treet', 'Supermax', 'Zorrik', 'Nacet', 'Perma-Sharp', 'Crystal',
    'Bolzano', 'Timor', 'GEM', 'PAL', 'Star', 'Ever Ready', 'Valet',
    'Enders', 'Durham Duplex', 'AutoStrop', 'Rolls Razor', 'Dovo',
    'Thiers-Issard', 'Boker', 'Puma', 'Wacker', 'Ralf Aust', 'Weck',
    'Fromm', 'Baxter', 'Vikings Blade', 'Baili', 'Weishi', 'QShave',
    'Ming Shi', 'Rimei', 'Yuma', 'Zaza', 'Tatra', 'Tiger', 'Leon',
    'Sokol', 'Sputnik', 'Ladas', 'Crown', 'Silver Star', 'Eli',
    'Big Ben', 'Crown Salon', 'Derby Extra', 'Derby Premium', 'Derby Usta',
    'Treet Platinum', 'Treet Dura Sharp', 'Gillette 7 O\'Clock',
    '7 O\'Clock', 'Astra Superior Platinum', 'Astra Superior Stainless',
    'Feather Hi-Stainless', 'Feather New Hi-Stainless', 'Kai Stainless',
    'Schick Super II', 'Schick Injector', 'Gillette Tech', 'Gillette NEW',
    'Gillette Super Speed', 'Gillette Slim', 'Gillette Fatboy',
    'Gillette Black Beauty', 'Merkur 34C', 'Merkur 23C', 'Merkur 37C',
    'Merkur 41C', 'Merkur 42C', 'Merkur Futur', 'Merkur Progress',
    'Mühle R89', 'Mühle R41', 'Edwin Jagger DE89', 'Parker 96R',
    'Parker 99R', 'Parker 24C', 'Parker 26C', 'Parker Variant',
    'Parker SoloEdge', 'Rockwell', 'Leaf Shave', 'Supply', 'OneBlade',
    'Henson', 'Manscaped', 'Philips', 'Braun', 'Panasonic', 'Remington',
    'Wahl', 'Andis', 'Gillette Guard', 'Gillette Venus',
    # heritage shaving houses
    'Proraso', 'Cella', 'Arko', 'Tabac', 'Palmolive', 'Williams',
    'Colgate', 'Barbasol', 'Geo F Trumper', 'Truefitt & Hill',
    'D R Harris', 'Taylor of Old Bond Street', 'Floris', 'Penhaligon\'s',
    'Acqua di Parma', 'Czech & Speake', 'Crabtree & Evelyn',
    'L\'Occitane', 'The Art of Shaving', 'Ach. Brito', 'Musgo Real',
    'Claus Porto', 'LEA', 'La Toja', 'Myrsol', 'Floid', 'Varon Dandy',
    'Figaro', 'Bea', 'Irisch Moos', 'Speick', 'Dr. Dittmar', 'Haslinger',
    'Klar Seifen', 'Sir Irisch Moos', 'Mäurer & Wirtz', 'Dreiring',
    # mass brush houses
    'Omega', 'Semogue', 'Zenith', 'Simpson', 'Thater', 'Shavemac',
    'Plisson', 'Vulfix', 'Kent', 'Vie-Long', 'Yaqi', 'DScosmetic',
    'Frank Shaving', 'Boti', 'Kent Brushes',
    # drugstore / consumer
    'Old Spice', 'Brut', 'Aqua Velva', 'Clubman', 'Pinaud', 'Mennen',
    'Speed Stick', 'Nivea', 'Florena', 'L\'Oréal', 'Unilever', 'P&G',
    'Combe', 'Edgewell', 'Energizer', 'Neutrogena', 'Dove',
    'Irish Spring', 'Ivory', 'Zest', 'Dial', 'Suave', 'Axe', 'Lynx',
    'Burma Shave', 'Noxzema', 'Kiehl\'s', 'Jack Black', 'Anthony',
    'Every Man Jack', 'Bulldog', 'Harry\'s', 'Dollar Shave Club',
    'Billie', 'Flamingo', 'Cremo', 'Edge', 'Gillette Foamy',
    'Nivea Men', 'Lab Series', 'Vaseline', 'Afta', 'Williams Mug',
    # mainstream fragrance houses
    'Creed', 'Davidoff', 'Lacoste', 'Versace', 'Dolce & Gabbana',
    'Armani', 'Ralph Lauren', 'Tom Ford', 'Hugo Boss', 'Calvin Klein',
    'Chanel', 'Dior', 'Hermès', 'Guerlain', 'Paco Rabanne',
    'Jean Paul Gaultier', 'Issey Miyake', 'Montblanc', 'Bvlgari',
    'Burberry', 'Cartier', 'YSL', 'Yves Saint Laurent', 'Givenchy',
    'Kenzo', 'Abercrombie & Fitch', 'Al Haramain', 'Amouage',
    'Adidas', 'Nike', 'Hugo', 'Boss', 'Terre d\'Hermès',
    'Bleu de Chanel', 'Sauvage', 'Aventus',
    # designer / luxury fragrance tier (added 2026-11-05, backlog item (15)):
    # EdTs by these houses fill the fragrance field but are never artisan
    # targets — the 2026-11-04 artisan pass kept pairing them against
    # artisan entries (e.g. Giorgio Armani strings vs artisan targets).
    # SCOPE: designer / mass / luxury houses only. Niche artisan perfumers
    # (Zoologist, Tauer, Papillon, Slumberhouse, Dusita, Nishane, Memo,
    # Nasomatto, Ormonde Jayne, Beaufort London, etc.) are DELIBERATELY
    # NOT excluded — they are legitimate artisan-dimension targets.
    # Brand strings are matched exactly after normalization, so both the
    # house name and its common short form are listed where both appear
    # as catalog brand strings (e.g. 'Armani' was already listed but did
    # NOT match brand 'Giorgio Armani' — the gap this tier closes).
    'Giorgio Armani', 'Emporio Armani', 'Jo Malone', 'Kilian',
    'Byredo', 'Le Labo', 'Diptyque', 'Maison Margiela', 'Parfums de Marly',
    'Xerjoff', 'Frederic Malle', 'Maison Francis Kurkdjian', 'MFK',
    'Initio', 'Serge Lutens', 'L\'Artisan Parfumeur', 'Annick Goutal',
    'Goutal', 'Caron', 'Houbigant', 'Viktor & Rolf', 'Mugler',
    'Thierry Mugler', 'Narciso Rodriguez', 'Valentino', 'Prada', 'Gucci',
    'Lancome', 'Lancôme', 'Estée Lauder', 'Clinique', 'Elizabeth Arden',
    'Carolina Herrera', 'Marc Jacobs', 'Michael Kors', 'Coach',
    'Tory Burch', 'John Varvatos', 'Nautica', 'Perry Ellis',
    'Kenneth Cole', 'Banana Republic', 'Zara', 'Bath & Body Works',
    'Victoria\'s Secret', 'Britney Spears', 'Jennifer Lopez', 'JLo',
    'Sean John', 'Usher', 'David Beckham', 'Beckham', 'Halle Berry',
    'Sarah Jessica Parker', 'SJP', 'Kim Kardashian', 'Katy Perry',
    'Taylor Swift', 'Ariana Grande', 'Rihanna', 'Beyoncé',
    'Alfred Dunhill', 'Dunhill', 'Jaguar', 'Ferrari', 'Bentley',
    'Mercedes-Benz', 'Lamborghini', 'Porsche', 'Azzaro', 'Lalique',
    'Chopard', 'Van Cleef & Arpels',
    # generic retailers / private-label channels
    'Amazon', 'eBay', 'AliExpress', 'Walmart', 'Target', 'CVS',
    'Walgreens', 'Boots', 'Superdrug', 'Tesco', 'HEMA', 'Müller',
    'dm', 'Rossmann', 'Costco', 'Dollar General', 'TopCare',
]))

con = sqlite3.connect(f'{BASE}/catalog/catalog.db')

def load_targets(artisan_only):
    targets = {}
    excl = MASS_MARKET if artisan_only else set()
    for eid, brand, product, data in con.execute(
            "select id, brand, product, data from entries where status='verified'"):
        if not brand:
            continue
        if artisan_only and norm(brand) in excl:
            continue
        try:
            d = json.loads(data)
        except Exception:
            d = {}
        names = set()
        if brand and product:
            names.add(f'{brand} {product}')
        if product:
            names.add(product)
        if brand:
            names.add(brand)
        for a in (d.get('aliases') or []) + (d.get('loose_aliases') or []):
            if isinstance(a, str):
                names.add(a)
        for n in names:
            nn = norm(n)
            if len(nn) >= 3:
                targets.setdefault(nn, (eid, f'{brand} {product}'))
    return targets

def load_unmatched():
    counts = Counter()
    authors = defaultdict(set)
    field_hits = defaultdict(set)
    for f in sorted(glob.glob(f'{BASE}/matched_*.json')):
        for post in json.load(open(f)):
            a = post.get('author') or ''
            for fld in FIELDS:
                s = post.get(fld)
                if not s or not isinstance(s, str):
                    continue
                m = (post.get('matches') or {}).get(fld)
                unmatched = (m is None) or (isinstance(m, dict) and
                                            str(m.get('id', '')).startswith('unverified/'))
                if unmatched:
                    counts[(s, fld)] += 1
                    authors[(s, fld)].add(a)
                    field_hits[s].add(fld)
    agg = defaultdict(lambda: [0, set(), set()])
    for (s, fld), c in counts.items():
        a = agg[s]
        a[0] += c
        a[1] |= authors[(s, fld)]
        a[2] |= field_hits[s]
    return agg

def lev(a, b, limit):
    if abs(len(a) - len(b)) > limit:
        return limit + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        row_min = i
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            v = min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + cost)
            cur.append(v)
            if v < row_min:
                row_min = v
        if row_min > limit:
            return limit + 1
        prev = cur
    return prev[-1]

def mine(targets, agg):
    cands = []
    target_set = set(targets)
    for s, (uses, au, fl) in agg.items():
        ns = norm(s)
        if len(ns) < 4 or uses < 2 or ns in target_set:
            continue
        if re.fullmatch(r'[0-9 ]+', ns):
            continue
        cands.append((s, ns, uses, len(au), sorted(fl)))
    blocks = defaultdict(list)
    for nn, info in targets.items():
        blocks[(nn[0] if nn else '', len(nn))].append((nn, info))
    results = []
    for s, ns, uses, nauth, fl in cands:
        lim = 2 if len(ns) < 12 else 3
        best = None
        for L in range(max(1, len(ns) - lim), len(ns) + lim + 1):
            for nn, info in blocks.get((ns[0], L), []):
                d = lev(ns, nn, lim)
                if d <= lim and (best is None or d < best[0]):
                    best = (d, nn, info)
                    if d <= 1:
                        break
        if best:
            results.append((uses, best[0], s, ns, best[1], best[2], nauth, fl))
    results.sort(key=lambda r: (-r[0], r[1]))
    return [{'uses': u, 'authors': na, 'fields': fl, 'typed': s,
             'typed_norm': ns, 'dist': d, 'target_norm': tn,
             'entry_id': eid, 'entry': disp}
            for u, d, s, ns, tn, (eid, disp), na, fl in results]

agg = load_unmatched()
print('distinct unmatched strings:', len(agg))

targets_art = load_targets(artisan_only=True)
print('artisan target names:', len(targets_art))
res_art = mine(targets_art, agg)
print('artisan near-miss pairs:', len(res_art))
json.dump(res_art[:400], open(f'{OUTDIR}/misspelling_cands_artisan_2026-11-04.json', 'w'),
          indent=1, ensure_ascii=False)
print('wrote artisan top-400')

targets_all = load_targets(artisan_only=False)
print('all target names:', len(targets_all))
res_all = mine(targets_all, agg)
print('all near-miss pairs:', len(res_all))
json.dump(res_all, open(f'{OUTDIR}/misspelling_cands_all_2026-11-04.json', 'w'),
          indent=1, ensure_ascii=False)
print('wrote full unrestricted pair list (item (a) staging)')
