#!/usr/bin/env python3
"""Backfill Source lines on bare glossary entries.

Every replacement is exact-match; the script aborts on any old string
that does not occur exactly once, so nothing is silently half-applied.
Counts come from tools/verify_glossary_abbrs.py over 240,908 rows
(matched_2016-2025 + sotd_2026_full), verified 2026-11-07.
"""
from pathlib import Path

P = Path("/home/hatch/workspace/sotd/knowledge/glossary.md")
text = P.read_text()

EDITS = [
    ("- **B&M** = Barrister and Mann. Established.",
     "- **B&M** = Barrister and Mann. Established. Source: dataset usage, verified 2026-11-07 (7,100 product-field rows carry 'B&M'; 96 rows also carry the full form)."),
    ("- **HoM** = House of Mammoth. Established.",
     "- **HoM** = House of Mammoth. Established. Source: dataset usage, verified 2026-11-07 (1,293 product-field rows carry 'HoM'; 169 rows also carry the full form)."),
    ("- **NO** = Noble Otter. **AMBIGUOUS**: also the ordinary word \"no\".\n  Established.",
     "- **NO** = Noble Otter. **AMBIGUOUS**: also the ordinary word \"no\".\n  Established. Source: dataset usage, verified 2026-11-07 (1,058 product-field rows carry 'NO'; 134 rows also carry the full form)."),
    ("- **CF** = Chiseled Face. Established.",
     "- **CF** = Chiseled Face. Established. Source: dataset usage, verified 2026-11-07 (448 product-field rows carry 'CF'; 28 rows also carry the full form)."),
    ("- **WK** = Wholly Kaw. Established.",
     "- **WK** = Wholly Kaw. Established. Source: dataset usage, verified 2026-11-07 (881 product-field rows carry 'WK'; 58 rows also carry the full form)."),
    ("- **A&E** = Ariana & Evans. Established.",
     "- **A&E** = Ariana & Evans. Established. Source: dataset usage, verified 2026-11-07 (2,172 product-field rows carry 'A&E'; 19 rows also carry the full form)."),
    ("- **M&M** = Murphy & McNeil. Established.",
     "- **M&M** = Murphy & McNeil. Established. Source: dataset usage, verified 2026-11-07 (21 product-field rows carry 'M&M' — thin but attested; 2 rows also carry the full form)."),
    ("- **SBS** = Summer Break Soaps. Established.",
     "- **SBS** = Summer Break Soaps. Established. Source: dataset usage, verified 2026-11-07 (946 product-field rows carry 'SBS'; 96 rows also carry the full form)."),
    ("- **GD** = Grooming Dept. Established.",
     "- **GD** = Grooming Dept. Established. Source: dataset usage, verified 2026-11-07 (277 product-field rows carry 'GD'; 11 rows also carry the full form)."),
    ("- **T+S** = Tallow + Steel. Established.",
     "- **T+S** = Tallow + Steel. Established. Source: dataset usage, verified 2026-11-07 (396 product-field rows carry 'T+S'; 9 rows also carry the full form)."),
    ("- **APR** = Australian Private Reserve. Established. [catalog]",
     "- **APR** = Australian Private Reserve. Established. Source: dataset usage, verified 2026-11-07 (837 product-field rows carry 'APR'; 41 rows also carry the full form). [catalog]"),
    ("- **TOBS** = Taylor of Old Bond Street. Established (\"soap=TOBS\n  grapefruit\"). [catalog]",
     "- **TOBS** = Taylor of Old Bond Street. Established (\"soap=TOBS\n  grapefruit\"). Source: dataset usage, verified 2026-11-07 (708 product-field rows carry 'TOBS'; 11 rows also carry the full form). [catalog]"),
    ("- **SV** = Saponificio Varesino. Established (\"Saponificio Varesino -\n  Manna di Sicilia\"). [catalog]",
     "- **SV** = Saponificio Varesino. Established (\"Saponificio Varesino -\n  Manna di Sicilia\"). Source: dataset usage, verified 2026-11-07 (355 product-field rows carry 'SV'; 29 rows also carry the full form). [catalog]"),
    ("- **RR** = RazoRock. Established (dominant in wetshaving context).\n  Low ambiguity. [catalog]",
     "- **RR** = RazoRock. Established (dominant in wetshaving context).\n  Low ambiguity. Source: dataset usage, verified 2026-11-07 (1,147 product-field rows carry 'RR'; 66 rows also carry the full form). [catalog]"),
    ("- **EJ** = Edwin Jagger. Established (\"Edwin Jagger Badger Hair Brush\").\n  [catalog]",
     "- **EJ** = Edwin Jagger. Established (\"Edwin Jagger Badger Hair Brush\").\n  Source: dataset usage, verified 2026-11-07 (493 product-field rows carry 'EJ'; 2 rows also carry the full form). [catalog]"),
    ("- **WSP** = Wet Shaving Products. Established (\"WSP Rustic Shaving Soap -\n  Fougére Noir\"). [catalog]",
     "- **WSP** = Wet Shaving Products. Established (\"WSP Rustic Shaving Soap -\n  Fougére Noir\"). Source: dataset usage, verified 2026-11-07 (519 product-field rows carry 'WSP'; the full form appears in 185 rows, never in the same row as the abbreviation). [catalog]"),
    ("- **MLS** = Mickey Lee Soapworks (closed 2019, see lineages.md; \"soap=MLS\n  Kraken\" — Kraken was an MLS scent). Established. [catalog]",
     "- **MLS** = Mickey Lee Soapworks (closed 2019, see lineages.md; \"soap=MLS\n  Kraken\" — Kraken was an MLS scent). Established. Source: dataset usage, verified 2026-11-07 (2,346 product-field rows carry 'MLS'; 17 rows also carry the full form). [catalog]"),
    ("- **SW** = Southern Witchcraft(s). Established. Low ambiguity in\n  wetshaving context. [catalog]",
     "- **SW** = Southern Witchcraft(s). Established. Low ambiguity in\n  wetshaving context. Source: dataset usage, verified 2026-11-07 (328 product-field rows carry 'SW'; 4 rows also carry the full form). [catalog]"),
    ("- **AP** = AP Shave Co (Canadian brush maker; \"AP Shave Co Tuxedo\n  Synthetic\" brushes; also G5C knots). Established. [catalog]",
     "- **AP** = AP Shave Co (Canadian brush maker; \"AP Shave Co Tuxedo\n  Synthetic\" brushes; also G5C knots). Established. Source: dataset usage, verified 2026-11-07 (12,819 product-field rows carry 'AP'; 10,083 carry the full form, all also carrying the token as expected). [catalog]"),
    ("  - **LGC** = **L**e **G**rand **C**hypre. Established (community).",
     "  - **LGC** = **L**e **G**rand **C**hypre. Established (community). Source: dataset usage, verified 2026-11-07 (179 product-field rows carry 'LGC'; 53 rows also carry the full form)."),
    ("- **GTB** = Ghost Town Barber (Chiseled Face's own shorthand for the\n  scent). Established.",
     "- **GTB** = Ghost Town Barber (Chiseled Face's own shorthand for the\n  scent). Established. Source: dataset usage, verified 2026-11-07 (35 product-field rows carry 'GTB'; 7 rows also carry the full form)."),
    ("- **MMOC** = GEM Micromatic Open Comb. **MMCP** = Micromatic Clog-Pruf.\n  Established.",
     "- **MMOC** = GEM Micromatic Open Comb. **MMCP** = Micromatic Clog-Pruf.\n  Established. Source: dataset usage, verified 2026-11-07 (MMOC: 2,761 product-field rows, 33 also carrying the full form; MMCP: 6 notes-field rows only — the abbreviation is rare, the expansion 'Micromatic Clog-Pruf' is attested in 188 rows)."),
    ("- **\"The Bird\"** = Blackland Blackbird razor. Established (community\n  nickname; dataset-attested).",
     "- **\"The Bird\"** = Blackland Blackbird razor. Established (community\n  nickname; dataset-attested). Source: dataset usage, verified 2026-11-07 (64 notes-field rows say 'the bird'; 3 razor-field rows carry 'The Bird')."),
    ("- **Fatboy** = Gillette 195 Adjustable razor. Established.",
     "- **Fatboy** = Gillette 195 Adjustable razor. Established. Source: dataset usage, verified 2026-11-07 (1,849 razor-field rows carry 'Fatboy'; 287 rows also carry 'Gillette 195')."),
    ("- **Splash** = aftershave splash (vs balm — different product forms of\n  the same scent). **EdT / EdP / Parfum** = fragrance concentrations;\n  posters often omit the concentration entirely. Established.",
     "- **Splash** = aftershave splash (vs balm — different product forms of\n  the same scent). **EdT / EdP / Parfum** = fragrance concentrations;\n  posters often omit the concentration entirely. Established. Source: dataset usage, verified 2026-11-07 ('Splash' in 17,702 aftershave-field rows; 'EdT' in 5,080 product-field rows; 'EdP' in 1,347)."),
    ("- **SB** = solid bar (Wolfman guard type: \"WR1-SB\", \"WR-SB\" — vs OC open\n  comb). Established (dataset razor-field usage). [catalog]",
     "- **SB** = solid bar (Wolfman guard type: \"WR1-SB\", \"WR-SB\" — vs OC open\n  comb). Established (dataset razor-field usage). Source: dataset usage, verified 2026-11-07 (10,886 product-field rows carry 'SB'; the expansion is spelled out in 86 rows). [catalog]"),
    ("- **SP** = Super Platinum (blade suffix: \"Astra SP\", \"7 o'clock Black\n  SP\"). Established. [catalog]",
     "- **SP** = Super Platinum (blade suffix: \"Astra SP\", \"7 o'clock Black\n  SP\"). Established. Source: dataset usage, verified 2026-11-07 (9,953 product-field rows carry 'SP'; 14 rows also carry the full form). [catalog]"),
    ("- **SI** = Super Iridium (\"Polsilver SI\" = Wizamet Super Iridium blades).\n  Established. [catalog]",
     "- **SI** = Super Iridium (\"Polsilver SI\" = Wizamet Super Iridium blades).\n  Established. Source: dataset usage, verified 2026-11-07 (2,952 product-field rows carry 'SI'; 2 rows also carry the full form). [catalog]"),
    ("- **AS** = aftershave (dominant). Note: \"AS\" is also the Feather **AS-D2**\n  razor model (\"Feather AS D2\") — check field position. Established.\n  [catalog]",
     "- **AS** = aftershave (dominant). Note: \"AS\" is also the Feather **AS-D2**\n  razor model (\"Feather AS D2\") — check field position. Established.\n  Source: dataset usage, verified 2026-11-07 (10,969 product-field rows carry 'AS'; 428 rows also carry the full form). [catalog]"),
    ("- **OC** = Open Comb (razor guard type). Established. [catalog]",
     "- **OC** = Open Comb (razor guard type). Established. Source: dataset usage, verified 2026-11-07 (6,734 product-field rows carry 'OC'; 3 rows also carry the full form). [catalog]"),
    ("- **DE** = Double Edge. **SE** = Single Edge. Established. [catalog]",
     "- **DE** = Double Edge. **SE** = Single Edge. Established. Source: dataset usage, verified 2026-11-07 ('DE' in 3,872 product-field rows, 3 also carrying the full form; 'SE' in 1,889 rows, 22 also carrying the full form). [catalog]"),
    ("- **AC** = Artist Club (Feather AC / Kai / Schick Proline blade system).\n  Established. [catalog]",
     "- **AC** = Artist Club (Feather AC / Kai / Schick Proline blade system).\n  Established. Source: dataset usage, verified 2026-11-07 (1,898 product-field rows carry 'AC'; 71 rows also carry the full form). [catalog]"),
    ("- **NEW** = Gillette NEW (razor); **LC** = **L**ong **C**omb, **SC** =\n  **S**hort **C**omb (Gillette NEW variants — but see SC's Soap Commander\n  ambiguity above). Established. [catalog]",
     "- **NEW** = Gillette NEW (razor); **LC** = **L**ong **C**omb, **SC** =\n  **S**hort **C**omb (Gillette NEW variants — but see SC's Soap Commander\n  ambiguity above). Established. Source: dataset usage, verified 2026-11-07 ('NEW' in 2,446 rows, 1,784 also carrying 'Gillette NEW'; 'LC' in 657 rows, 1 also carrying the full form; 'SC' in 914 rows, 1 also carrying the full form). [catalog]"),
    ("- **GC** = RazoRock **G**ame **C**hanger (\"Razorock GC .68/.84\").\n  Established. [catalog]",
     "- **GC** = RazoRock **G**ame **C**hanger (\"Razorock GC .68/.84\").\n  Established. Source: dataset usage, verified 2026-11-07 (1,070 product-field rows carry 'GC'; 3 rows also carry the full form). [catalog]"),
    ("- **CG** = Charcoal Goods (razor maker; \"CG Antique Brass, L1/L2\").\n  Established. [catalog]",
     "- **CG** = Charcoal Goods (razor maker; \"CG Antique Brass, L1/L2\").\n  Established. Source: dataset usage, verified 2026-11-07 (859 product-field rows carry 'CG'; 14 rows also carry the full form). [catalog]"),
    ("- **MR** = Maggard Razors — handles (\"Maggard Slant on MR 5 handle\",\n  \"MR-14\") and the Maggard house soap line (\"MR Limes and bergamot\").\n  Established. [catalog]",
     "- **MR** = Maggard Razors — handles (\"Maggard Slant on MR 5 handle\",\n  \"MR-14\") and the Maggard house soap line (\"MR Limes and bergamot\").\n  Established. Source: dataset usage, verified 2026-11-07 (746 product-field rows carry 'MR'; 317 rows also carry 'Maggard'). [catalog]"),
    ("- **HD** = **H**eavy **D**uty (\"Merkur 34C HD\", \"Rocket HD 500\").\n  Established. [catalog]",
     "- **HD** = **H**eavy **D**uty (\"Merkur 34C HD\", \"Rocket HD 500\").\n  Established. Source: dataset usage, verified 2026-11-07 (1,019 product-field rows carry 'HD'; the expansion is spelled out in only 4 rows — the token is the community's standard form). [catalog]"),
    ("- **FH** = **F**ull **H**ollow (straight-razor grind: \"5/8 FH\").\n  Established. [catalog]",
     "- **FH** = **F**ull **H**ollow (straight-razor grind: \"5/8 FH\").\n  Established. Source: dataset usage, verified 2026-11-07 (932 product-field rows carry 'FH'; the full form appears in 1,645 rows, never in the same row as the abbreviation). [catalog]"),
    ("- **XL** = size tag, \"extra large\" (Mühle \"Silvertip Fibre XL\" = 23mm;\n  \"Mergress XL\" handle). Established. [catalog]",
     "- **XL** = size tag, \"extra large\" (Mühle \"Silvertip Fibre XL\" = 23mm;\n  \"Mergress XL\" handle). Established. Source: dataset usage, verified 2026-11-07 (2,476 product-field rows carry 'XL'; 25 rows also carry 'Silvertip Fibre XL'). [catalog]"),
    ("- **STF** = Mühle **S**ilvertip **F**ibre (\"Muhle Silvertip Fibre XL\",\n  \"Muhle XL STF\"). Established. [catalog]",
     "- **STF** = Mühle **S**ilvertip **F**ibre (\"Muhle Silvertip Fibre XL\",\n  \"Muhle XL STF\"). Established. Source: dataset usage, verified 2026-11-07 (1,225 product-field rows carry 'STF'; 1 row also carries the full form). [catalog]"),
    ("- **HMW** = **H**igh **M**ountain **W**hite (badger hair grade; \"DS\n  Cosmetics 26mm High Mountain White bulb\"). Established. [catalog]",
     "- **HMW** = **H**igh **M**ountain **W**hite (badger hair grade; \"DS\n  Cosmetics 26mm High Mountain White bulb\"). Established. Source: dataset usage, verified 2026-11-07 (991 product-field rows carry 'HMW'; 2 rows also carry the full form). [catalog]"),
    ("- **GSB** = Gillette **S**ilver **B**lue (blades; \"GSB (2)\"). Established.\n  [catalog]",
     "- **GSB** = Gillette **S**ilver **B**lue (blades; \"GSB (2)\"). Established.\n  Source: dataset usage, verified 2026-11-07 (3,516 product-field rows carry 'GSB'; 12 rows also carry the full form). [catalog]"),
    ("- **PTFE** = blade coating (polytetrafluoroethylene; \"GEM SS PTFE\").\n  Established. [catalog]",
     "- **PTFE** = blade coating (polytetrafluoroethylene; \"GEM SS PTFE\").\n  Established. Source: dataset usage, verified 2026-11-07 (12,584 product-field rows carry 'PTFE'; the chemical name is never spelled out in the dataset — the token is the standard form). [catalog]"),
    ("- **LE** = Limited Edition. **EDP** = Eau de Parfum. Established.\n  [catalog]",
     "- **LE** = Limited Edition. **EDP** = Eau de Parfum. Established.\n  Source: dataset usage, verified 2026-11-07 ('LE' in 1,345 product-field rows; 'EDP' in 1,347 — neither expansion is spelled out alongside its abbreviation). [catalog]"),
    ("- **CNC** = CNC-machined (razor manufacturing tag, e.g. \"CNC 6061\").\n  Note, not a product. Established. [catalog]",
     "- **CNC** = CNC-machined (razor manufacturing tag, e.g. \"CNC 6061\").\n  Note, not a product. Established. Source: dataset usage, verified 2026-11-07 (846 product-field rows carry 'CNC'). [catalog]"),
    ("- **BBS** = **B**aby **B**utt **S**mooth (the closest shave grade;\n  Sharpologist Karve review glosses it verbatim). Established.",
     "- **BBS** = **B**aby **B**utt **S**mooth (the closest shave grade;\n  Sharpologist Karve review glosses it verbatim). Established. Source: dataset usage, verified 2026-11-07 (9,051 notes-field rows carry 'BBS'; the expansion is spelled out in 2 rows)."),
    ("- **DFS** = **D**amn **F**ine **S**have (one tier below BBS; \"a very nice\n  DFS result\", \"DFS++\"). Established (dataset usage).",
     "- **DFS** = **D**amn **F**ine **S**have (one tier below BBS; \"a very nice\n  DFS result\", \"DFS++\"). Established (dataset usage). Source: dataset usage, verified 2026-11-07 (3,546 notes-field rows carry 'DFS'; 6 rows also carry the full form)."),
    ("- **WTG** = **w**ith **t**he **g**rain; **XTG** = across; **ATG** =\n  **a**gainst. Established (thousands of dataset hits).",
     "- **WTG** = **w**ith **t**he **g**rain; **XTG** = across; **ATG** =\n  **a**gainst. Established (thousands of dataset hits). Source: dataset usage, verified 2026-11-07 ('WTG' in 4,976 notes-field rows; 'XTG' in 2,904; 'ATG' in 5,507)."),
    ("- **LG** = Lather Games (the r/Wetshaving annual shaving competition;\n  every June per Sharpologist — 2022 ran June, 2023 moved to July).\n  Established.",
     "- **LG** = Lather Games (the r/Wetshaving annual shaving competition;\n  every June per Sharpologist — 2022 ran June, 2023 moved to July).\n  Established. Source: dataset usage, verified 2026-11-07 (4,094 notes-field rows carry 'LG'; 743 rows also carry the full form)."),
    ("- **SOTN** = **S**have **O**f **T**he **N**ight; **SOTE** = **S**have\n  **O**f **T**he **E**vening (notes-field post headers). Established\n  (dataset usage).",
     "- **SOTN** = **S**have **O**f **T**he **N**ight; **SOTE** = **S**have\n  **O**f **T**he **E**vening (notes-field post headers). Established\n  (dataset usage). Source: dataset usage, verified 2026-11-07 ('SOTN' in 2,636 notes-field rows; 'SOTE' in 1,164 — the expansions are essentially never spelled out, the tags are the standard form)."),
    ("- **PIF** = **P**ay **I**t **F**orward (community giveaway; \"threw up a\n  PIF... worst case, I re-PIF it\"). Established.",
     "- **PIF** = **P**ay **I**t **F**orward (community giveaway; \"threw up a\n  PIF... worst case, I re-PIF it\"). Established. Source: dataset usage, verified 2026-11-07 (2,354 notes-field rows carry 'PIF'; 1 row also carries the full form)."),
]

failed = []
for old, new in EDITS:
    n = text.count(old)
    if n != 1:
        failed.append((old[:60], n))
        continue
    text = text.replace(old, new)

if failed:
    print(f"FAILED {len(failed)} replacements (file NOT written):")
    for s, n in failed:
        print(f"  count={n} :: {s!r}")
else:
    P.write_text(text)
    print(f"OK: applied {len(EDITS)} source backfills to glossary.md")
