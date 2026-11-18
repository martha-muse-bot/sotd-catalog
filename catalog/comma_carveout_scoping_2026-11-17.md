# Comma carve-out scoping for the P-25 composite split

Date: 2026-11-17. Status: **scoping complete — variant (e) recommended** (build not
started; needs Jim's go-ahead + the same A/B verification P-25 got).
Read-only analysis only: no changes to `match_all.py`, `sotd_db.py`, the catalog
DB, or `precedents.md`.

## 0. Recommendation

**Ship variant (e) — comma + exact/normalized-only parts + the two narrow
exemptions (alum fallback, weak-only P5 paren rule) — on aftershave, blade,
razor, and fragrance. Hold soap** (12 rows) for a follow-up descriptor guard.

- Expected yield: **416 incremental rows / 868 part attributions** (428 / 892
  with soap). Incremental = rows not already split by the existing P-25
  separators (`;`, `|`, ` / `, ` + `, ` then `).
- **Q006736 splits correctly** under (e): `Alum Block` →
  `unverified/aftershave/alum` (subset, via the alum fallback);
  `Proraso After Shave Balm (Green Tea, Oatmeal).` →
  `aftershave/proraso-white-sensitive` (subset-rev, via P5). `Cold Water` is
  junk-dropped as routine text. The 24 currently-mis-attributed-to-Green rows
  move to White + alum.
- **B&M scent-name killer test: passed.** 23 B&M aftershave comma splits,
  **0** LLC-pattern, **0** Shave-Balm-Lavender, **0** castillo-parts. (e) is
  the only variant besides the floor (b) that both passes this test and
  splits Q006736.
- Sample-verified clean rates under (e), run 4: aftershave 29/30 clean
  (1 partial), blade 12/15 clean (3 questionable), razor 11/12 clean
  (1 partial), fragrance 2/2 clean, soap 9/12 clean (2 false, 1 questionable
  — hence holding soap).

Variant (f) (subset allowed) is rejected: 995 rows but aftershave only ~80%
clean, soap ~40% clean, razor ~20% clean (handle annotations). Variants
(a)/(d)/(d2) (subset-rev allowed) are rejected: they fail the B&M killer
test outright (45 LLC rows false-split into Lime + Lavender + Captain Nemo's
Castillo) and false-split Q006710.

## 1. Why comma was excluded, and what changed

The P-25 analysis (§7.4) excluded comma because sampled strict passes in
aftershave were only ~5/9 clean under G0–G6 — the systematic failure being
B&M scent-name commas (`Barrister and Mann - Lime, Lavender, and Cedarwood -
Aftershave` false-splits into three wrong attributions). This scoping
confirms that failure mode is real and lethal for loose variants — but shows
it disappears entirely under exact/normalized-only part resolution, because
the false third part (`and Cedarwood - Aftershave` → Castillo) only resolves
via subset-rev. The carve-out is therefore viable **only** in the strict
discipline; the whole question reduces to whether the strict discipline can
still split Q006736, which needs two narrow, justified exemptions (§4).

## 2. Method

Harness `catalog/work/comma_carveout_harness.py` mirrors the built P-25
split (`match_all.py` `_p25_try_split` / `_p25_resolve_part`) and reuses the
module's own `_p25_preprocess`, `_p25_whole_is_product`, `_p25_is_junk`,
`_p25_rev_via_composite`, `_match_with_index`, `INDEXES` / `MID_INDEXES`.
Differences from P-25: separator is a paren-aware comma (commas at paren
depth 0 only — required: the Q006736 string has a comma *inside*
`(Green Tea, Oatmeal)`), parts go through part variants (as-is,
paren-stripped, truncated at first ` (`), and the guard variants below
replace P-25's method set. Verification script
`catalog/work/comma_carveout_verify.py` quantifies the B&M test and emits
seeded samples (`comma_carveout_samples.txt`); every sample quoted here was
manually classified CLEAN / FALSE / PARTIAL / QUESTIONABLE. Results:
`comma_carveout_results.json`. Full dataset: 241,319 rows.

Guard variants:

| variant | definition |
|---|---|
| (a) | G0–G6 as-is, comma added; all methods (exact/normalized/subset/subset-rev) |
| (b) | comma + parts resolve via exact/normalized ONLY |
| (c) | comma + subset allowed, no subset-rev |
| (d) | (a) + alum fallback + P5 paren rule |
| (d2) | (a) + alum fallback + stripped-first part variants |
| (e) | **(b) + alum fallback + weak-only P5, both exempt from the method filter** |
| (f) | (c) + alum fallback + weak-only P5, both exempt |

Runs: run 1 (variants a–d2), run 2 (added e/f; found two harness defects —
see §7), run 3 (defects fixed; found the exempt-paren leak — see §7),
run 4 (leak fixed; **final numbers**). All counts below are run 4 unless
stated. "incr" = rows not already split by P-25 separators; that is the
added yield of the carve-out.

## 3. Split counts (run 4, incremental rows)

| field | (a) | (b) | (c) | (d)/(d2) | **(e)** | (f) |
|---|---|---|---|---|---|---|
| aftershave | 1118 | 303 | 682 | 1249 | **357** | 802 |
| soap | 54 | 12 | 35 | 54 | **12** | 35 |
| blade | 92 | 45 | 86 | 92 | **45** | 86 |
| razor | 174 | 11 | 68 | 174 | **12** | 68 |
| fragrance | 6 | 2 | 4 | 6 | **2** | 4 |
| **total rows** | **1444** | **373** | **875** | **1575** | **428** | **995** |
| total part attributions | 3250 | 782 | 1938 | 3534 | **892** | 2196 |

Pools (rows containing a paren-aware comma, whole string not a product):
aftershave 10,924; soap 3,903; blade 2,663; razor 8,246; fragrance 1,985.
Note (f) = (c) + 120 aftershave rows (the alum-fallback/P5 rows — the
exemptions only fire in aftershave); (e) = (b) + 54 aftershave rows + 1
razor row. (e) gross vs incr is 429 vs 428 (1 row already split by P-25).

## 4. The Q006736 edge cases — decided

### 4a. Alum-block ambiguity → alum fallback (recommended option O2)

`Alum Block` tier-1 resolves **ambiguous between exactly two entries**:
`aftershave/osma-alum-block` and `aftershave/parker-alum-block` (both
product `Alum Block`). Under G1 an ambiguous part fails the split.

Options considered: O1 fail the split (string stays whole, still
mis-attributed to Green — contradicts the ruling); O2 fall back to the
attested generic alum entry when the ambiguity is only between branded
variants of the same substance (**recommended**); O3 treat the alum part as
junk (undercounts alum); O4 resolve to the more popular branded block
(false precision, violates P-24).

O2 as implemented: when tier-1 ambiguity fires and **every** ambiguous entry
is an alum-block entry and the part contains `alum`, resolve tier-2 — which
lands on `unverified/aftershave/alum` (attested, 97 uses / 27 authors) via
subset. The result is marked exempt from the method filter. P-24
implications spelled out: this is P-24-*compliant*, not a P-24 exception —
resolving to Osma or Parker would BE folding alum into a branded block;
the fallback keeps bare alum on its attested entry, exactly as P-24
requires. A branded block still resolves to itself when named
(`Osma Alum Block` → `osma-alum-block`, exact — seen in the (e) samples).
The fallback is alum-specific and does not generalize: any other ambiguous
part still fails the split.

### 4b. Proraso scent-note parenthetical → P5 paren-dependence rule (weak-only)

Part-cleaning variants tested on `Proraso After Shave Balm (Green Tea, Oatmeal).`
(trailing period included):

| variant | resolves to |
|---|---|
| as-is | **Proraso GREEN** (`aftershave/proraso-green`, subset) — WRONG; the token `Green` inside `(Green Tea, Oatmeal)` matches the Green line. Green is menthol/eucalyptus; green tea & oat is White's scent. |
| paren-stripped | **Proraso WHITE** (`aftershave/proraso-white-sensitive`, subset-rev) — correct |
| truncated at first ` (` | White as well (same stripped form, minus the trailing period) |

P5 rule: when the as-is and stripped resolutions disagree AND the as-is
resolution is weak (subset/subset-rev) AND the matched entry's smallest
witness alias uses a token present only inside the parenthetical, prefer
the stripped resolution. Weak-only: a strong (exact/normalized) as-is hit
is never overridden. Verified by probe: `_match_depends_on_parens` is True
for the Q006736 case (the Green witness alias rests on the token `Green`,
which appears only inside the parens).

**Known P5 misfire (residual risk, §8):** `Proraso Aloe & Vitamin E
Protettivo balm (blue)` — as-is resolves correctly to `proraso-blue`
(Aloe & Vitamin E *is* Blue's scent), but P5 overrides it to generic
`proraso` because the Blue witness uses `blue`, which appears only inside
the parens. P5 cannot distinguish "(Green Tea, Oatmeal)" (a scent
description whose color word falsely matches another line) from "(blue)"
(the product's own color word). Cost: one Blue attribution goes generic.
The trade favors P5 — the Q006736 class (35 rows of the exact string) is
larger than the `(blue)` class — but it is a real, documented imperfection.
A future refinement could exempt the override when the paren token is the
*whole* parenthetical and equals the matched line's color word; not
attempted here.

## 5. B&M scent-name killer test

979 B&M aftershave comma rows; 58 LLC-pattern rows
(`Barrister and Mann - Lime, Lavender, and Cedarwood - Aftershave`, mostly
trythatsoap markdown links); 5 Shave-Balm-Lavender rows
(`Barrister and Mann - Shave Balm, Lavender`).

| variant | B&M splits | LLC | ShaveBalmLav | castillo-parts |
|---|---|---|---|---|
| (a) | 113 | 45 | 5 | 44 |
| (b) | 20 | 0 | 0 | 0 |
| (c) | 49 | 0 | 0 | 0 |
| (d)/(d2) | 120 | 45 | 5 | 44 |
| **(e)** | **23** | **0** | **0** | **0** |
| (f) | 56 | 0 | 0 | 0 |

The 23 (e) B&M splits are genuine two-product rows (e.g. `Thayers -
Unscented Facial Toner, Barrister and Mann - 42 splash`; `Alum, B&M
Arctique`; `B&M Reserve Spice, L'Occitane Cade Balm`). (a)/(d)/(d2) fail
the killer test: 44% of their B&M splits are the known scent-name traps.

## 6. The five unresolvable composites — which does the carve-out help?

| item | string | any variant splits it? |
|---|---|---|
| Q006736 | Cold Water, Alum Block, Proraso … (Green Tea, Oatmeal). | **YES — (d)/(d2)/(e)/(f) only, correctly** (alum → generic alum; Proraso → White). (a)/(b)/(c): no. |
| Q006649 | Thayers + menthol | No (all variants). `menthol` matches no entry; `+` is not comma. |
| Q041653 | Lucky Tiger - extra moisturizer | No (all variants). ` - ` is not comma. |
| Q006710 | Thayer's Facial Toner, Lily of the Desert Aloe Vera Gelly | **False-splits under (a)/(d)/(d2)** — Lily half → `dickinson-s-original-witch-hazel-pore-perfecting-toner` via subset-rev (alias pollution). Safe (no split) under (b)/(c)/(e)/(f). |
| Q045575 | Alum, Stirling Bay Laurel Witch Hazel, … Olive Oil | No (all variants). Olive oil is an ingredient, matches no entry; alum per P-24 never folds into the Stirling block. |

**Plainly: the carve-out helps exactly 1 of the 5 (Q006736).** The other
four are untouched by every variant, and under the loose variants one of
them (Q006710) is actively mis-handled. The carve-out is a fix for the
Q006736 *class* — routine-text + alum + real-product comma lists — plus
~400 other genuine two-product comma lists, not a general fix for the five.

## 7. Harness defects found and fixed (why runs 1–3 are superseded)

Two defects, both in `comma_carveout_harness.py` (the harness only —
`match_all.py` untouched):

1. **Exemption gating (run 2):** the alum fallback was gated on
   `exempt_fallback` alone instead of `(method in allowed or
   exempt_fallback)`, so under (d) (allowed = all, no exemption flag) it
   never fired; and the fallback's result (method `subset`) was then
   filtered out by `resolve_part`'s method check under (e). Fixed by
   passing `allowed` into `resolve_variant`, firing the fallback when
   `eid2 == GENERIC_ALUM and (m2 in allowed or exempt_fallback)`, marking
   fallback results `'exempt': True`, and letting `exempt` results through
   the method filter (stripped before returning so the key never leaks into
   stored output).
2. **Exempt-paren leak (run 3 → run 4):** `exempt_paren` was applied not
   only to the P5 override return but also to the stripped-variant fallback
   in `resolve_part`'s paren branch — so *any* paren-bearing part whose
   stripped form resolved by a disallowed method leaked through. Effect in
   run 3: razor/(e) grew 11 → 30 rows, of which 9/15 in the seeded sample
   were false — all `Gillette Slim, Gillette Silver Blue (N)` → Tatara
   Masamune via subset-rev on a composite alias (the blade name in the
   razor field). Fixed by removing `exempt_paren` from that fallback line;
   the exemption now applies **only** to the P5 override return. Verified
   by probe: Q006736 still splits under (e)/(f); the GSB trap now returns
   None under (e)/(f). Run 4 is the first run in which (e)/(f) mean what
   they were designed to mean. **The build must port the run-4 semantics,
   not the run-3 code.**

## 8. Manual sample verification (run 4, seeded samples)

Classification: CLEAN = two (or more) real products, each to the right
entry; FALSE = wrong entry or one product split in two / double-counted;
PARTIAL = right split, one attribution vague or one product uncredited;
QUESTIONABLE = cannot tell from the string alone.

**Variant (e) — recommended:**

| field | shown | clean | false | partial | questionable | notes |
|---|---|---|---|---|---|---|
| aftershave | 30 | 29 | 0 | 1 | 0 | Partial = Proraso Aloe & Vitamin E (blue) → generic `proraso` (P5 misfire, §4b). Q006736 appears 5×, all correct. |
| soap | 12 (all) | 9 | 2 | 0 | 1 | False: `Gillette Foamy Shaving Cream, Sensitive Skin` → Barbasol Sensitive Skin (descriptor as product); `Declaration, Santal Auster` → brand entry + soap (one product double-counted). Questionable: `Stirling Barbershop, Almond cream` → London Oatcake Almond Cream. |
| blade | 15 | 12 | 0 | 0 | 3 | All 3 questionable are the Super-Platinum restatement pattern: `Gillette 7 O'Clock Black, Super Platinum` and `Israeli Crystal, Super+ Platinum` (×2) — likely one blade split in two (7 O'Clock Black *is* the Super Platinum black pack; Crystal Super+ *is* the Israeli blade), second half routed to Zorrik Super Platinum. |
| razor | 12 (all) | 11 | 0 | 1 | 0 | Partial: `Hybrid, by Oneblade (+ Twig)` double-counts the OneBlade brand; Twig uncredited. GSB→Tatara trap gone. |
| fragrance | 2 (all) | 2 | 0 | 0 | 0 | |

**Variant (f) — rejected alternative:**

| field | shown | clean | false | partial | questionable | notes |
|---|---|---|---|---|---|---|
| aftershave | 30 | 24 | 2 | 3 | 1 | False: `Proraso — Crema Liquida Dopabarba, Blue` split in two (one product); `Leftover lather during cleanup, …` → leftover-lather joke entry (G5 gap: non-exact `leftover lather …` not junked). Partial: `Alum Block \| Combe, Inc - Aqua Velva…` (pipe inside part); Sir Irisch Moos multi-separator row; `Stetson Black cologne` → Stetson aftershave entry. |
| soap | 15 | 6 | 6 | 2 | 1 | False: `…, by Haslinger` (attribution double-counted to brand entry); `1 of 10` → entry `10`; Williams prose fragment → second Williams entry; `Proraso White, aka "…Green Tea and Oat…"` → Proraso Green; Foamy/Sensitive Skin → Barbasol; Red House Farms prose → Noble Otter Jasmine Green Tea. |
| blade | 15 | 10 | 3 | 0 | 2 | False: `platinum coated DE` → Gillette Platinum (descriptor); `GEM, by Persona` → `persona`; Personna Med Prep prose → `american`. Questionable: the two Super-Platinum patterns. |
| razor | 15 | 3 | 11 | 1 | 0 | False: handle annotations (`on iKon SE long handle` → `ikon`, `w/ Timeless titanium Crown handle` → `timeless`, Windrose/Timeless pass descriptions → `standard`/`timeless`/`rockwell`) — subset lets every handle mention through. |

For reference, run-1 tallies for the loose variants: (a) aftershave ~87%
clean, soap ~53%, blade ~67%, razor ~15%; (b) aftershave 30/30, razor
11/11 clean but cannot split Q006736.

## 9. Residual risks and follow-ups (not blockers for (e))

1. **Soap held, not shipped.** 12 rows, 2 known-false patterns
   (descriptor-as-product: `Sensitive Skin` → Barbasol; maker+scent as two
   products: `Declaration, Santal Auster` → brand entry + product). Both
   are guardable later: a descriptor-part guard (a part consisting only of
   skin-type/format descriptor tokens does not count as a product) and a
   brand-entry guard (a part resolving to a bare-brand entry while another
   part resolves to a product of that brand does not count as a second
   product). Shipping (e) without soap costs 9 clean attributions.
2. **Blade Super-Platinum restatement pattern.** ~9 of the 45 blade rows
   (by sample share) are the `X, Super Platinum` pattern; the 7 O'Clock
   Black case leans false (one blade split in two, second half to Zorrik).
   A G7 restatement guard (a part that is a bare variant word already
   present in the sibling part's entry name does not count) would kill it;
   scoped as follow-up, not required to ship.
3. **P5 misfire (§4b).** A small number of correct color-word matches
   (`(blue)`) get overridden to the generic entry. Bounded, accepted.
4. **Leftover-lather G5 gap.** `unverified/aftershave/leftover-lather` is
   a joke entry; non-exact forms (`leftover lather during cleanup`) are not
   junked and absorb routine text — but only under subset-allowing
   variants. (e) is safe from it; (f) is not. The entry itself is owed a
   not_a_product review (flagged in the P-25 analysis §9).
5. **Alias hygiene (§9 of the P-25 analysis) still the bigger lever.**
   Composite strings harvested as aliases cause the reverse-subset traps
   seen here (GSB → Tatara Masamune; Lily → Dickinson's). The carve-out
   works around them with strict methods; the alias pass would remove the
   traps at the source and would also lift P-25 razor/soap yield.
6. **A/B verification still owed before shipping** (same bar as P-25):
   run `match_all.py` with the carve-out on 2022/2024/2025/2026, flag-off
   comparison, zero split-caused regressions. Expected delta vs the P-25
   A/B: +416 rows split / +868 attributions under (e) (four fields).

## 10. Build notes (what to port into match_all.py)

- Separator: comma, per-field for aftershave, blade, razor, fragrance
  (soap held — see §9.1); brush excluded, same as P-25. Paren-aware split
  (commas at paren depth 0 only); reuse `_p25_preprocess` (HTML-unescape,
  `~~…~~` strip, markdown-link reduction, URL strip) first.
- Guards: G0 whole-string-first (unchanged); G1 every non-junk part must
  resolve — via **exact/normalized only**, except the two exemptions below;
  G2 distinct entries; G3 ≥3-token floor on subset-rev-only (moot under
  (e) except for exempted resolutions — keep it); G4 >80-char prose cap;
  G5 routine-phrase junk; G6 additive junk. Junk parts (`Cold Water`,
  `Cold rinse`, `rinse`) are dropped, not fatal.
- Part variants in order: as-is, paren-stripped, truncated at first ` (`.
  P5 (weak-only paren-dependence) picks between as-is and stripped as
  specified in §4b; **exempt_paren applies only to the P5 override return**
  (§7.2 — port the run-4 semantics).
- Alum fallback (§4a): tier-1 ambiguity solely between alum-block entries
  + `alum` in the part → generic attested alum entry, marked exempt from
  the method filter. No other fallback exists.
- Output schema: same as P-25 (`{'split': […], 'method':
  'composite-split', 'tier': best part tier}`); split parts carry the
  `exempt` provenance internally only — strip it before storing.
- `SPLIT_ENABLED` flag covers the carve-out as well (same kill switch).

## Appendix: files

- Harness: `catalog/work/comma_carveout_harness.py` (run-4 semantics)
- Verify + samples: `catalog/work/comma_carveout_verify.py`,
  `catalog/work/comma_carveout_samples.txt` (1003 lines, run 4)
- Results JSON: `catalog/work/comma_carveout_results.json` (run 4)
- P-25 analysis: `catalog/multi_item_field_analysis_2026-11-16.md`
  (§5 G0–G6, §7.4 comma exclusion, §8 table)
