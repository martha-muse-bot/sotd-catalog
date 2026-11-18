# World notes: formats, stores, events, conventions

- **Event months on r/Wetshaving**: Austere August (August) and Lather
  Games (October) run TWO SOTD threads per day. April 1 threads may be
  disguised (2025's ran as the "MOTD Thread"). Source: dataset build
  2026-10. Established.
- **Weck Sextoblade** razors take hair-shaper blades (e.g. Diane);
  **Valet AutoStrop** razors take the FHS-pattern blade. Source: catalog
  research 2026-10-20. Established.
- **A77** is a 62mm single-edge "cabinet blade" format (longest shavette
  blade; wide/narrow variants; brands Cloud, Antelope, Rhinoceros Swiss,
  Snow Mountain Wolf) — sellers substitute A77 brands freely. Source:
  catalog research 2026-10-20. Established.
- **razorbladesclub.com** is a key source for international blades but is
  poorly search-indexed — its own site search (live browser) works.
  Source: user tip + catalog work 2026-10-20. Established.
- **Cuchillería Moreno** (cuchilleriamoreno.com, Spain) is a useful EU retailer for primary store evidence on Barrister and Mann lines — carries B&M products (e.g. Marilyn aftershave) that are gone from the maker site; product pages render for automation. Source: catalog validation 2026-10-21 (used as primary evidence for aftershave/barrister-and-mann-marilyn). Confidence: established.
- **Declaration Grooming's own site can return 402** to automated
  fetches, and the company has been reported to be winding down —
  time-sensitive for evidence capture. Source: brush catalog team
  2026-10-20. Confidence: lead (verify current status).
- **[catalog] Kismet hair-shaper blades — German barber-supply brand
  (established 2026-10-21).** Stainless ("Rostfrei"), polymer-coated
  hair-shaper blades sold from Germany (posters order them from
  Germany; wrapper's full name: "Kismet Haarschneide-, Effilier- und
  Rasiermesser"); fit the Weck Sextoblade and other hair-shaper
  shavettes; Kismet also sells a branded shavette (German
  barber-supply retailers). Community consensus rates them smoother
  than Personna hair-shaper blades. Alias cluster in
  product_aliases.md. Source: dataset mining + B&B SABRE/shavette
  threads + nmrs correct_matches. Confidence: established.
  **Maker attribution (established 2026-10-22):** Kismet is a
  professional-hairdressing trade line carried in Comair's German
  catalog (Comair brand est. 1970; part nos. 3050178 replacement
  blades 6-pack, 3050179 razor incl. 6 blades) and supplied by
  Sinelco in the Nordics (Danish retailer lists "Producent: Sinelco",
  2026-10-23). Brand of record
  stays Kismet (P-04). The 1910/1921 F. Koeller & Co. (Solingen-
  Ohligs) 'Kismet' blade mark is a real historical record but a
  coincidence, not a continuation (working verdict). Full detail +
  catalog guidance in product_aliases.md.
  **ADDENDUM 2026-10-28 [catalog]:** Comair = **Comair Germany GmbH,
  Viersen** (own terms + EU trademark record); Sinelco Group =
  Belgium-based salon wholesale distributor (Sally Beauty
  acquisition, ~€25.5m; exclusive labels Sibel/Ultron/Bob Tuo) —
  its 1943 Denhaerynck → Sibel → Prosibel founding chain is
  single-source LEAD only (see refinement below).
  **ADDENDUM 2026-11-02 [catalog] — spine established, name stays
  lead:** the spine now has independent corroboration —
  PitchBook company profile (affiliate "sinelco international
  bvba, Ronse, Belgium, founded 1943"; HQ Oudenaarde; acquired by
  Sally Beauty Holdings 17-Dec-2009) + prospeo.io (HQ Ronse,
  founded 1943) + three retailer brand copies ("Sibel, since
  1964"). ESTABLISHED: Ronse founding 1943, Oudenaarde HQ, Sibel
  brand since 1964, Sally Beauty ownership (Dec 2009). STILL LEAD
  (wapalli-only): the "Albert Denhaerynck" founder name, hair-net
  family firm, 1952 move, 1964 Prosibel rename, 1997
  Nelson-absorption/Bob Tuo. Never cite the founder name or
  pre-1964 narrative as established. Residual: check sinelco.com
  for a company-history page. **CORRECTION:** "retailers include Witte
  Solingen" is withdrawn — the sole basis is one ambiguous 2025
  string (`Witte Kismet shavette`, SuperLuck5116, no channel named)
  and Solingen holds three distinct Wittes (Witte & Co. 1922,
  Rich. Witte 1925, Kurt-Reiner Witte today); never cite Witte as a
  Kismet retailer. Comair catalog sweep negative: no Kismet SKU
  beyond 3050178/3050179 found.
  **ADDENDUM 2026-11-07 [catalog] — exclusive-brands SOTD
  cross-check RESOLVED (learner run): NONE of Sinelco's three
  exclusive-label brands appears in the SOTD datasets as a
  product.** Full-corpus census (sotd_2016–2026_full.json,
  240,951 rows, all product fields + notes): Sibel = 1 hit, a
  FALSE POSITIVE — MalbecApologist's 2021-02-23 "other" field
  links a Sibelius Violin Concerto soundtrack, not the brand;
  Bob Tuo = 0; Ultron = 0; Sinelco = 0. Catalog: zero entries
  for any of the four names (catalog_merged.json grep = 0;
  catalog.db id/brand LIKE queries empty). The absence is
  structural, not a data gap: all three are hairdressing-trade
  brands with no shaving products — Sibel = salon-support brand
  since 1964, 2,000+ products (combs, capes, brushes, salon
  furniture, nail formulas); Bob Tuo = hairdresser Bob Tuo's
  cutting-collar brand (launched 1997 via the Nelson
  absorption; capes/collars); Ultron = hair-tools brand
  (dryers/styling tools, launched 2002; ultronhair.com, "part
  of the sinelco group"). Trade press corroborates the trio as
  the exclusive-label core (Happi, Sally Beauty acquisition
  2009: ~85% of Sinelco revenues from Sibel/Ultron/Bob Tuo;
  RocketReach: "private labels Sibel, Ultron and Bob Tuo...
  distributed across the whole of Europe"). Catalog: NO
  entries owed for any of the three; never create one on a
  future bare "Sibel"/"Ultron" string without a shaving-product
  sighting. Guards: "Sibel" in a dataset string is the composer
  Sibelius (soundtrack field), never the brand; "Ultron" has
  zero dataset presence (and is a Marvel false friend in web
  search only, not in the corpus).

## nmrs/sotd-pipeline — live corroboration source [established, 2026-10-20, user ruling]
- Independent MIT-licensed pipeline over the same r/Wetshaving SOTD data (github.com/nmrs/sotd-pipeline), cloned at ~/workspace/sotd/external/sotd-pipeline. User ruling 2026-10-20: treat as a LIVE source (actively curated — commits as recent as 2026-10-20; data work lands in bursts around monthly report cycles), NOT a one-time pull.
- Role: SEMI-VALIDATION. Their correct_matches/*.yaml (human-confirmed raw string -> brand+product) and data/*.yaml catalogs resolve IDENTITY and corroborate existence, recorded as corroboration on our entries. RULING (user, 2026-10-20): corroboration sets status "corroborated" — a real tier between unverified and verified — and NEVER auto-promotes: verified still requires primary evidence under the standing standard, no matter the attestation count.
- Measured 2026-10-20: exact-string correct_matches hits on 5,438 of our unverified entries in covered categories (razor 40.1%, brush 23.7%, soap 20.0%); blades undermeasured (their blade files nest format->brand->model; fix matching at integration). Their blades.yaml is format-first (A77/AC/...), independently matching our taxonomy; soaps.yaml carries wsdb_slug cross-refs; intentionally_unmatched.yaml = known non-product strings; brush_splits.yaml = composite brush splitting data.
- Sync plan (post-SQLite): weekly job — git pull, diff against last-synced commit (stored in DB meta), corroborate new mappings, flag our items whose upstream mapping changed or vanished.
- CORROBORATION RULE (user, 2026-10-20, refined): an entry reaches status "corroborated" via EITHER an nmrs match OR attestation by 3+ distinct authors (crowd attestation is itself confirmation). Corroborated never auto-promotes to verified; verified requires primary evidence. Measured at ruling: 1,899 unverified entries have >=3 authors; ~31,700 are single-author (the long tail neither path reaches).
- TAXONOMY UPDATE (user, 2026-10-20): 3+ distinct authors = ATTESTED (existence established, name unconfirmed), a fourth status between corroborated and verified — supersedes the earlier note framing attestation as a corroboration path. Attested does not unlock set cross-validation; identity-disputed clusters cannot be attested.

- **[catalog] Brand-of-record / user-intent primacy (user ruling, 2026-10-21)**:
  catalog identity follows the brand the user intends (brand of record).
  Manufacture/lineage is an attribute, never identity — a brand owner can move
  production to another manufacturer and the product-as-bought stays the same.
  Grounds: Parker Injector (AccuTec-made, Parker entry), Rex/Tatra (Czech
  Blades manufacture in notes). Unbranded packaging does NOT defeat brand of
  record: Ted Pella injector blades are their own entry (Personna manufacture
  noted) because posters consistently record the purchase as "Ted Pella"
  (user reversal, 2026-10-21). Confidence: established.

- **[catalog] Maggard Razors is a first-check attribution source (user,
  2026-10-21)**: maggardrazors.com product pages carry reliable brand
  attribution across a wide artisan range — check Maggard early when a
  product's brand or existence is in question. A Maggard product page is a
  store product page = primary evidence. (User-supplied example: their Ted
  Pella injector listing settled the Ted Pella entry's verification.)
  Confidence: established.

- **trythatsoap.com's brand-status field is stale — do not trust it for
  alive/dead (learned 2026-10-22).** The site still lists Storybook
  Soapworks as an active brand even though the brand closed September
  25, 2020 (community member scarpux flagged this in a 2021-06-29
  dataset note: "TTS is out of date since they still show it as
  active"). The collection/product pages are still useful as product-
  naming evidence (they name the scents), but the status metadata is
  not. Source: dataset mining sotd_2021_full.json. Confidence:
  established.
- **storybooksoapworks.com liveness UNCONFIRMED (lead, 2026-10-22).**
  Sandbox DNS interception (all domains resolve to the 198.18.x.x
  blocked range) and blocked outbound DNS mean maker-site checks cannot
  be done from this VM; the charter also bars the live browser for this
  task. Needs an independent check: is the domain dead, parked, or
  squatted? Wayback last-capture date for the maker product pages is
  also wanted by validators. [catalog]

## Blade manufacture geography

- **[catalog] Van Der Hagen DE blades = made by Giesen & Forsthoff
  (Timor), Solingen — the "Solingen" maker RESOLVED (2026-10-23,
  backlog lead).** VDH's own site (quoted by Sharpologist's long-handle
  review): *"Van Der Hagen blades are manufactured in Solingen,
  Germany, a city renowned for fine blade production. The stainless
  steel blades are ice tempered for sharpness and flexibility."*
  Retail copy repeats it (Target 2024: "made in Germany from ice
  tempered stainless steel"). The maker is **Giesen & Forsthoff**, the
  Solingen family house behind the **Timor** blade brand ('Timor'
  registered 1921; family business since 1920, 4th-generation
  Katharina Giesen + mother Christiane Giesen per a 2026 distributor
  page; still Solingen-producing).
  - Six independent community firsthand sources name Timor: B&B 456402
    p.2 #27 ("I thought that the VdH blades were unbranded Timor
    blades"); B&B 478283 #18 ("Timor is what they use for the Van Der
    Hagen is it not?"); B&B 626825 #6 ("ice tempered blades which I
    believe are made by Timor in Germany"); DFS RayClem ("In the past
    Timor produced 'ice tempered' blades. I believe they also produced
    the 'ice tempered' blades for Merkur and Van der Hagen"); DFS
    archive poster ("pretty certain... both made by Timor since they
    were made in Solingen and are ice tempered just as the Timor
    blades").
  - DECISIVE: the B&B **Blade Sharpness Research Project** (652790,
    updated 2026-10-11) — a current blade-forensics effort measuring
    laser print and edge geometry — states: *"Timor and Van Der
    Hagen, which are made in the same Solingen plant, are also marked
    'Ice Tempered.'"* The same mark, the same plant.
  - Sharpologist's "perhaps sourced from Merkur?" speculation is
    SUPERSEDED: per RayClem, the OLD Merkur ice-tempered blades were
    ALSO Timor-produced — the community was tasting the same Solingen
    Timor-made blade under two house labels, which is what spawned the
    Merkur guess.
  - The 2017 bestmensshaver teardown fits the profile: ice-tempered,
    Teflon-coated, individually wrapped blades — "not the sharpest,"
    the classic Timor-ice-tempered report.
  Sources: VDH's own copy (via Sharpologist); B&B/DFS threads above;
  B&B Blade Sharpness Research Project; G&F/Timor corporate pages
  (bonherre.com distributor, BladeHQ); Target 2024 listing. Confidence:
  established (strong corroborated: 6+ independent community sources
  + the 2026 blade-research project's same-plant statement + the
  maker's own Solingen/ice-tempered copy). The only missing primary:
  a G&F or VDH statement naming the private-label contract (such
  contracts are rarely disclosed).
  **Catalog impact [catalog]:** per P-04, brand of record stays "Van
  Der Hagen" — record Solingen / Giesen & Forsthoff (Timor-made,
  ice-tempered) as a manufacture ATTRIBUTE on the VDH blade entries
  (nmrs maps 5 dataset strings under Van Der Hagen / Stainless; ~80
  dataset strings total). Do NOT merge VDH blades with Timor or
  Merkur. "Made in Germany" / "(German)" descriptors fold as
  attributes. The 2025 V Razor still ships "Ice Tempered German
  blades" (launch press, third-news.com) — German-blade sourcing
  continues.
  **Method note:** the B&B Blade Sharpness Research Project (652790)
  is now a first-class blade-attribution source — it compares blade
  laser print/markings and edge measurements across brands
  (updated 2026-10-11). Check it before speculating on any Solingen
  blade's maker.

- **[catalog] Astra Superior Platinum (green) — "formerly Czech, now
  Russia" CONFIRMED, with a 2023+ correction (resolved 2026-10-22,
  backlog item; original claim: spazztik88 dataset note, 2022-06-03).**
  Full geography timeline for the green Astra:
  1. **1967–2004: Jevíčko, Czechoslovakia → Czech Republic.** The
     Jevíčko razor-blade works (Svitavy district — blade production was
     concentrated there in 1949). 1967: first "Astra Superior"
     stainless blades, then "Astra" and "Astra Superior Platinum"
     (ceramic-coated). Privatized in the early 90s under the name
     "Astra"; Gillette bought 100% in late 1996. (Czech-made Astras —
     green AND blue — were in circulation in the early 90s: B&B 277731
     #5, 2012, "when the blade was made in Czeckoslavkia".)
  2. **2004–2022: PPI St. Petersburg, Russia.** Dec 2003 decision:
     moving stainless-blade production to St. Petersburg was cheaper;
     290 Jevíčko workers released during 2004. Carbon blades for
     industrial/agricultural purposes stayed in Jevíčko — as of 2008
     made by **Czech Blades s.r.o.** (brands Tiger, Tatra, Leon, Sokol,
     mostly sold in Africa).
  3. **2023+: India (Europe/US markets); Russia continues for
     non-sanctioning markets.** After the 2022 invasion, P&G wound down
     PPI; Sharpologist (2025-06-30 transition table): Astra SP
     Russia→India; B&B 666085 (mod-edit Mar 2025): "The Astra for
     Europe are instead produced in India"; Turkey-market Russian packs
     (production date 12/20/2024) still circulate. Dataset check:
     "Astra Green (Indian)" strings first appear **2023-11-03** and
     ramp 2024–2026 (1,047 total) — independent confirmation of the
     transition timing.
  Sources: B&B thread 422882 (2014, quoting the Jevíčko plant history —
  primary-ish for the Czech chapter); B&B 277731 #5 (Czech-era
  firsthand); Sharpologist "When Russian-Made Razor Blades Move"
  (2025-06-30); B&B 666085; dataset mining sotd_2023–2026_full.json.
  Confidence: established (Czech era + move date + Russia era +
  India transition; the exact month India production started is
  bracketed by the dataset, not pinned).
  **Catalog impact [catalog]:** ONE product across all three eras —
  per P-04 manufacture is an ATTRIBUTE, never identity. Validators:
  "Astra SS (Czechoslovakian)" / "(Russian)" / "Astra Green (Indian)"
  strings are era attributes on the same entries; and "now Russia" was
  true in 2022 but is STALE for Europe/US stock — never treat Russia
  as the current origin. Corroborates the product_aliases.md Tatra
  note independently (B&B 422882 names Tatra among Czech Blades
  s.r.o.'s brands).
  **CORRECTION 2026-11-01 (blue-Astra run): the backlog's "current =
  India (Baddi)" parenthetical is UNCITED — no source names the Indian
  Astra plant.** Gillette India Ltd runs plants at Bhiwadi (Rajasthan)
  and Baddi (Himachal Pradesh) (tradebrains.in), and P&G sources razor
  STEEL from Jindal Stainless (Reuters, Dec 2024 — steel strip, not
  blade manufacture), but nothing says which plant makes Astra blades.
  Treat "Baddi" as an unpinned lead, never as an established origin
  attribute. The established claim is country-level only: India.
- **[catalog] Astra Superior Stainless (blue) — full geography timeline
  RESOLVED 2026-11-01 (backlog item; the green's 2026-10-22 entry is its
  twin).** The blue follows the same three-era arc as the green:
  1. **Czech era (Jevíčko) — ESTABLISHED.** B&B 277731 (Feb 22, 2012,
     firsthand): "I found Astra as a great blade almost right from the
     start in the early 1990`s when the blade was made in Czeckoslavkia...
     I bought over 2000 Astra blades with a mix of Astra Platinum- green
     and Astra Stainless- blue" — both colors in Czech-era circulation.
     Physical-blade confirmation: B&B 606414 "Challenge PIF — Astra
     Superior Stainless Blades - Then And Now" (multi-participant,
     ~2021) shaved "Vintage Astra SS (Czech)" blades head-to-head
     against "Astra SS (Modern Russian)" — the vintage Czech blue SS is
     a real, held-in-hand artifact, not lore.
  2. **Russia/PPI era — ESTABLISHED.** Same B&B 606414 challenge names
     the modern blade "Astra SS (Modern Russian)"; B&B 637908 #28 (Sept
     2023): "since they decided to make Astras in Russia around 2005"
     (community dating of the move; the Dec-2003-decision/2004-move
     plant history from the green entry covers the brand's stainless
     line). JoelB's 2025 "(Russian)"-tagged blue strings (11 posts,
     Sept–Oct 2025, single author) = old-stock Russian packs in 2025,
     destash pattern.
  3. **India era — ESTABLISHED.** B&B 637908 #28 (Sept 2023): "P&G
     moving the production of both models to India" — both = SP and SS,
     community voice. Retailer-primary: The Razor Company's Astra
     collection page (live 2026-11-01) lists both Superior Platinum and
     Superior Stainless with collection copy "Made in India" for the
     current assortment.
  **Transition timing asymmetry (new finding):** the blue's India move
  LAGS the green's. Dataset has ZERO "blue Astra (Indian)" tags (the
  one apparent hit is a combo-string false positive — "Gillette
  Wilkinson Sword (India)" inside a Mentioned_Videos blade rotation);
  and an eBay seller (mysalonsupplies, via B&B 458761 p.228, Oct 2026)
  still sells Russian-made Astra SS while reporting "currently I do
  not have Made in India inventory for Astra Superior Stainless."
  So: green India stock since ~Nov 2023 (dataset-bracketed); blue India
  stock confirmed at retail (TRC) but still scarce enough that a blade
  seller has none — and Russian blue packs (incl. Turkish-market
  production dated 12/20/2024, per B&B 666085) keep circulating.
  Exact first-India-production date for the blue is unpinned.
  **Catalog impact [catalog]:** ONE blue product across all three eras
  (origin = era attribute, P-04) — same as the green. Validators: the
  blue's India era is real (TRC), so "Made in India" on a blue pack is
  current-stock, not a mismatch; "Russia" on a blue pack is old stock
  (2025 JoelB strings = destash). Never treat either origin as a
  product split.
- **[catalog] Gillette Minora — South African brand bought by Gillette;
  modern blades made in RUSSIA, not Egypt (resolved 2026-11-05,
  backlog item "Minora razor company buyout").** Minora was an old
  South African blade brand that Gillette acquired — two independent
  B&B voices agree (B&B 598248 #17: "Minora was an old South African
  brand that Gillette acquired... Gillette started manufacturing
  operations in South Africa in 1954"; "Around the World in 80
  Blades" journal, Blade #48: "before Gillette bought the brand, and
  were made in Gillette's factory there in the 1950s"). Production
  geography since: France in the 1950s, Latin America, Russia (PPI,
  St. Petersburg — the current era), and "supposedly" Canada
  (B&B 598248 #17; the Canadian leg is dataset-attested but
  date-uncertain — USS-SpongeBob's 2019 note describes "WW2-era
  Canadian-made Minora blades" from his grandfather's drugstore stock;
  poster-dated, unpinned, and it tensions the 1950s acquisition story).
  **CORRECTION:** the modern Minora Stainless blade is RUSSIAN-made
  (PPI), not Egyptian — the 2026-10-22 "Egyptian Minora Stainless"
  gloss in hardware_lore.md is retired. Sources: Razor Blades Club
  (live 2026-11-05, the catalog entry's own evidence: "double edge
  blades made in Russia by Gillette"); B&B 598248 ("Stainless (yellow)
  Minoras made in Russia"; "The pink-packaged Minoras were made by PPI
  too"); B&B Russian Blade Games list ("Gillette Minora (PPI)"); B&B
  Blade Sharpness Research ("Gillette Minora Stainless Russia");
  kind_simian's dataset notes 2021 ("Minora Stainless (0.1, Russia
  🇷🇺)"). The "Egyptian" gloss likely conflated Minora with Shark/Lord
  (Egyptian Gillette blades) — never cite Egypt for Minora. Yellow-pack
  Stainless is the NEWER product (B&B 598248, published 2020-11-12:
  "Trickling onto the market"; pink Platinum "have been around for
  years"); Razor Blades Club still lists the Stainless InStock
  2026-11-05 ($0.39). Post-2022 PPI wind-down: B&B 648167 lists
  Minora among the brands that "might not move at all" (Asian/African
  markets); whether current stock is still Russian-made is unpinned.
  The brand is still marketed and sold in South Africa (journal, Blade
  #48 — reportedly a proprietary eponym there, the generic word for
  razor blades), and Volza import data shows "DISP RAZOR MINORA 11
  GILLETTE" disposables still shipping from South Africa to Lesotho
  in 2025.
  **Catalog impact [catalog]:** origin is an era attribute (P-04) on
  the two verified blade entries (`DE/gillette-minora-stainless`,
  `DE/gillette-minora-platinum`) — never a product split; never cite
  Egypt. The Minora-stamped English NEW razors are Gillette-made
  razors with a Minora brand stamp (see hardware_lore.md Minora
  addendum) — fold their strings into verified `razor/gillette-new`.

- **[catalog] HEMA (Dutch variety-store house brand) DE blades =
  rebranded Personna — RESOLVED 2026-11-09 (backlog item
  2026-10-24; the Taconic half of that item stays open — see
  lineages.md Taconic addenda).** HEMA is the Dutch department-store
  chain; its house-brand DE blades are the European supermarket
  generic line, i.e. Personna/Energizer-made, brand of record HEMA
  per P-04 with Personna as manufacture attribute — never fold into a
  Personna-branded entry.
  - **Second independent voice (2013 era):** El Judio Bravo, B&B
    51858 #226, 2013-05-21: "Tesco, Boots, ASDA, and on the
    continent, HEMA, seem to sell the same blades." Context pins the
    referent: the post sits directly after #223 (ASDA Personna
    blister pack, photo: "Personna blister pack with Tesco-style
    blade box containing the plain single wrapped blank blades") and
    #224 ("this decisively links the Tesco and Boots blades with the
    Personna name"). The "same blades" = the Israeli-made
    Personna/Energizer generic store-brand DE blades (plain
    single-wrapped blank blades; German twin "Streamline", €1.89,
    "distributed by Personna UK" per #227 Cholli).
  - **Firsthand dataset voice (2026 era):** Greyzer, SOTD note
    2026-03-22: "Hema blades (rebranded Personna)" — packed for a
    3-week travel kit with a Gillette Ball End Tech. Two voices, 13
    years apart, same verdict.
  - **Dataset scope (full corpus, 240,987 rows):** 8 product-field
    Hema hits — blade field ×1 (VenkHeerman 2023-10-20, "HEMA", with
    a Yaqi TFC adjustable) + aftershave field ×7 (see below); notes
    field: handoverthecoffee 2017-05-06 ("Parker sr 1 Hema blade" —
    half-DE in a shavette) and 2019-02-25 ("Gillette Tech ball end
    Hema blade"), VenkHeerman 2023-10-20 ("The HEMA stuff is all
    pretty good"). HEMA blades were in use 2017–2019 and 2023–2026,
    bridging the two attestation eras.
  - **Era split (do not flatten):** the 2013-era HEMA blade is the
    ISRAELI-made Personna generic (Nazareth plant). The current-era
    blade's plant is a lead-grade inference only — the Israeli plant
    is gone and the generic line now runs from Edgewell Solingen
    (B&B 658492 p.2: "at least 2 different models made in Germany.
    One is the Personna Platinum blue for Europe, the other is the
    generic store brand"; BSRP tested the modern generic as
    "Edgewell Solingen By Amazon", test 305). Greyzer's 2026
    "(rebranded Personna)" is consistent with the Solingen generic,
    but no HEMA pack photo or "Made in Germany" read exists yet —
    never cite Israel for a post-~2020 HEMA blade. Verification
    route: a current HEMA pack/blade photo (country of origin +
    blade print).
  - **CORRECTION to the backlog:** the "(Impressive_Donut114 2025)"
    citation is NOT corroborated — zero Hema rows for that author in
    any field of the full corpus; the claim's dataset attestation is
    Greyzer only. The backlog's "Greyzer 2021" was the Everclear
    note below, not a Personna claim — the Personna claim is Greyzer
    2026-03-22.
  - **Vintage separate product — "Everclear Blue Blades":** Greyzer,
    SOTD note 2021-05-21: an unopened pack of 25 "Everclear Blue
    Blades (generic Dutch store brand from Hema)" in his
    grandfather's kit (≥35 years old, so pre-~1986). "Everclear"
    appears nowhere else in the corpus (all other hits are the band /
    the alcohol). Own vintage entry, maker UNPINNED — never fold
    into the modern Personna-generic HEMA blade; the pre-1986 HEMA
    blade supplier predates the Personna-generic era.
  - **HEMA aftershave (same house brand, different product):**
    7 aftershave-field rows / 2 authors — handoverthecoffee
    2019-12-15 → 2020-02-15 ("Hema after shave balm", "Hema 2 in 1
    after shave balm") and VenkHeerman 2023-06-24 → 2023-08-11
    ("Hema aftershave/day cream"). A HEMA house-brand aftershave
    balm / day cream is a real product; never fold into the blade
    entry.
  - **Current retail status UNPINNED:** no HEMA DE-blade listing
    surfaced on hema.nl or bol.com via search (site:hema.nl query
    empty; hema.nl homepage live 2026-11-09); last in-use evidence
    is Greyzer 2026-03-22, which does not say he just bought them.
    Do not cite HEMA as a current DE-blade source until a live
    listing is found.
  Sources: B&B 51858 p.12 #223/#224/#226/#227 (2013-05-21, raw-HTML
  read for author/date: El Judio Bravo #226); B&B 658492 p.2 (generic
  store-brand model); B&B Blade Sharpness Research Project index
  (test 305, Edgewell Solingen By Amazon); dataset censuses above.
  Confidence: established (two independent community voices across
  eras + the documented supermarket-generic pattern + firsthand
  dataset use); the current-era plant is a lead, the vintage Everclear
  maker is unpinned.
  **Catalog impact [catalog]:** ZERO hema/everclear keys exist in
  catalog_merged.json — entries owed: (1) a HEMA DE blade entry
  (own entry, Personna manufacture attribute, era attribute for
  Israel vs Solingen); (2) a HEMA aftershave balm / day-cream entry
  (aftershave format); (3) an Everclear Blue Blades vintage entry
  (maker unpinned, never folded into (1)). "HEMA" blade-field
  strings fold to (1); "Hema aftershave balm / 2 in 1 / day cream"
  strings fold to (2).

## Retailers

- **ShoeBox Shave Shop (shoeboxshaveshop.com) — early US wet-shaving
  online retailer (established 2026-10-26, backlog item).** Active at
  least 2009–2017: B&B starter-kit recommendations name it as a
  favourite store (2009–2010, "Gary" the proprietor — first name
  only, surname unpinned); 2012 PREP/3P sale posts; June 2014 scalp-
  brush purchase; The Gadgeteer gift guide (Nov 2017) still lists
  ShoeBox Mühle shaving sets at $99. Stock profile was broad
  drugstore/European: GEM stainless + Blue Star, PAL, Treet and
  LOOK single-edge blades; Mühle sets; the Simpson Fifty series
  (regular stock, per a B&B review); Alpa Fougère; JM Fraser /
  Booster "Jake's" cologne ("Gary over at the Shoebox ShaveShop
  has started carrying this", B&B 140335).
  - **The backlog question is ANSWERED on the product side:** the
    product if0rg0t2remember bought out on clearance at ShoeBox
    was **Arko After Shave Cream** (his 2021-01-25 SOTD note:
    "discontinued some time around 2013 and I bought out several
    tubes in multiple scents when ShoeBox Shave Shop (the original
    iteration not whatever the hell it is now) was clearing their
    inventory"; his field that day: "Arko Citrus After Shave
    Cream"). See the Arko Men After Shave Cream entry in
    product_lines.md for the date correction: the documented change
    is Arko's 2015 relaunch, not a 2013 discontinuation.
  - **The "original iteration" remark itself is UNRESOLVED (lead).**
    No closure, rename, or new-owner announcement for ShoeBox
    surfaced in search, and the shop was still being listed in
    2017 — so do NOT record a ShoeBox closure date or ownership
    change on that evidence alone. What changed by 2021 (site
    redesign? ownership? assortment?) is unpinned.
  - **Current site state VERIFIED 2026-10-26 (live-browser check,
    12:07–12:08 CDT): shoeboxshaveshop.com is DEAD as a shop.**
    The domain redirects via a ww38 loading interstitial ("We're
    getting things ready") to kineticharbor.com, whose page
    carries the banner "Information about shoeboxshaveshop.com:
    Buy this domain." The domain is offered for sale; there is
    no ShoeBox storefront, product categories, cart, or checkout
    at the address. Validators: maker-site evidence route for
    ShoeBox-era listings is dead — use Wayback snapshots and
    forum-era listings instead. (The earlier text-fetch DNS
    failure the same day is consistent with this, but the
    live-browser redirect chain is the evidence cited.)
  - **FALSE FRIEND — do not fold:** Shoebox Barbershop, Flushing
    MI (Steve & Carmen Peek, opened Jan 2023, 1949–51 Shoebox
    Fords theme, Genesee County View Jan 25, 2024) is an unrelated
    physical barbershop that happens to share the name. Never use
    it as ShoeBox Shave Shop evidence.
  - Catalog relevance: ShoeBox is evidence-route history, not a
    brand — "ShoeBox" is never a product string; its clearance
    sale is the provenance for a poster's Arko hoard, and its
    early-2010s listings are a dating source for drugstore stock.
  Sources: sotd_2021_full.json (if0rg0t2remember 2021-01-25);
  B&B 127309, 140335, 283583, 405386; the-gadgeteer.com gift
  guide (Nov 2017); geneseecountyview.com (Jan 25, 2024).
  Confidence: retailer existence + 2009–2017 activity established;
  "original iteration" change + current site state = leads.

- **The Shave Supply, formerly The HandleBar Supply — Thousand Oaks,
  CA retailer (established 2026-10-26, correcting the 2026-10-22
  Ethos entry; [catalog] for retailer-name folding).** Traditional
  barbershop + shaving-supply retailer at 2219 E. Thousand Oaks
  Blvd, Thousand Oaks, CA (barbershop still styled "The HandleBar
  Barbershop and Apothecary" on the live contact page; contact
  Gareth@TheShaveSupply.com — note the spelling Gareth, not Garret).
  Self-description: "Retailer of men's grooming products since
  2012. Formerly named The HandleBar Supply." The rename predates
  June 2021 (WiReY_GuY's 2021-06-21 SOTD note already calls it "The
  Shave Supply, formerly The Handlebar Supply" and links the old
  thehandlebarsupply.com Ethos collection page); exact rename date
  unpinned (lead). Stockist of Ethos Grooming Essentials by 2021
  (the same note; Frank shipped a replacement for a cracked tub
  bought there — retailer vs maker, two parties). Still active
  (live site + contact page fetched 2026-10-26).
  - Catalog guidance: fold "The HandleBar Supply" → "The Shave
    Supply" as ONE retailer group; NEVER fold either name into
    Ethos Grooming Essentials (the 2026-10-22 merge caution is
    superseded — see lineages.md correction). "The Handlebar
    Supply Caribbean Snow" soap strings (20 hits, one author,
    Jul–Aug 2016) are NOT folded into a retailer house brand
    without a maker source; "Handlebar Shaving Company" razor
    strings (Dali, Oberon; one author, 2017) are a different name
    and NOT folded into this retailer.
  - **ADDENDUM 2026-10-28 — Caribbean Snow maker RESOLVED
    [catalog]: Queen Charlotte Soaps (QCS).** Two Aug 2013 B&B
    Head Shaver's Check-In posts (thread 259639, pp. 52/55) from
    posters holding shop samples: #1,021 — "a sample of QCS
    Caribbean Snow" picked up "at The Handlebar Barbershop
    (KodiakAttack's shop)"; #1,091 — "The HandleBar Caribbean
    Snow (by QCS)", "sample I picked up from The HandleBar
    Barbershop", described as a very firm croap (cream/soap),
    mentholated, "a rich coconut base, with a nice sweet lime
    riding on top." Dataset scope corrected: 21 soap-field
    strings, ALL darkfox45, Jul 12–Aug 9, 2016 (20 plain + the
    Jul 12 combo string with Dapper Dragon Signature / LASSCo
    Vert Noir); his notes frame it as a "Barbershop soap" and he
    finishes it by Aug 9. Catalog: create/fold into QCS
    Caribbean Snow; the catalog currently holds QCS Vostok /
    Esquire / Rose Otto / Green Irish Tweed / Celestial Woods /
    Cubano Breeze clusters but NO Caribbean Snow entry — the
    Handlebar strings are its attestation. Lead left: whether
    Caribbean Snow was a QCS catalog scent or a shop exclusive
    QCS made for the barbershop; and KodiakAttack's identity
    (B&B handle for the shop's proprietor — do NOT assume it is
    Gareth of the contact page without a source).
  Sources: sotd_2021_full.json (WiReY_GuY 2021-06-21); retailer
  self-description via search index; theshavesupply.com contact
  page (fetched 2026-10-26). Confidence: retailer identity +
  rename + Thousand Oaks base established; exact rename date lead.

- **Hoffritz for Cutlery — retailer identity ESTABLISHED 2026-10-29 [catalog]:**
  New York specialty cutlery retailer, founded 1932 by Edwin Jay Hoffritz
  (Ridgewood, Queens; started as "Hoffritz & Boschen" ~1928, sole-name shop
  by 1932 — trademark HOFFRITZ first use 1931-11-30, Class 008 covers razors).
  Grew to 23 stores mid-1970s, peaked at 110 stores in 33 states in the early
  1990s, then bankruptcy 1994 and defunct 1996; successor Lifetime Hoan
  (Lifetime Brands owns the HOFFRITZ mark today — Justia 73464510, registered
  1985). Sources: Wikipedia "Hoffritz for Cutlery"; USPTO/Justia trademark
  records. Retailer-brand hardware sold under the Hoffritz name: Merkur-made
  slants (the "Merkur 37" vintage slant, pre-~1970 tooling — see
  hardware_lore.md) and the Merkur-made heavy-toothed open comb that is
  Ian Fleming's literary James Bond razor ("Hoffritz on Madison Avenue for
  one of their heavy, toothed Gillette-type razors" — "007 in New York",
  1963; "He always used a Hoffritz safety razor patterned on the
  old-fashioned heavy-toothed Gillette type" — The Man with the Golden Gun,
  1965), plus Solingen-made straights (maker unpinned). Dataset: 107
  Hoffritz razor posts / 18 authors (slant-dominated); the 7 cowzilla3
  "Hoffritz of New York OC" posts (2023–2026) are the Bond open comb, NOT
  slant strings — the catalog's de-oc cluster currently mis-keys them to
  product "Slant" (see hardware_lore.md Bond-OC addendum [catalog]). Leads:
  exact Hoffritz OC model code (unpinned); straight-razor maker (unpinned).
- **Airline amenity kits genuinely included safety razors in the golden
  age** — Simple Flying's amenity-kit history (aviation writer Elle,
  2024-04-15) lists "solid brass single-blade safety razors (according
  to PanAm)" among pre-1950s/60s kit contents (alongside matchbooks,
  sewing kits, glass mouthwash bottles). This corroborates the ERA of
  the Personna BBS-0 airline-giveaway story (hardware_lore.md) but ties
  nothing to Personna. The razor's MAKER is unpinned everywhere: the
  Delta Flight Museum documents a 1950 Pan Am "President Special"
  shaving kit (small metal tube; "Care in the air" blog, 2024-10-23)
  with no maker named. BOAC's only fully documented 1949 kit is the
  Elizabeth Arden Speedbird Beauty Kit for WOMEN (cleanser, Velva
  Cream, Skin Lotion, Illusion Powder, Flower Mist, toothpaste,
  toothbrush, tissues/pads — NO razor); men's "Speedbird Overnight
  Bag" contents are undocumented (cosmeticsandskin.com, rev.
  2026-10-20).
  Wegian's coinage "Airline Tech" (2023-04-04, wegianwetshaving.com)
  for an English-made aluminium-handle Tech from classifieds was a
  TENTATIVE ID by the Nook forum — no airline branding on its sleeve —
  so the Gillette's airline story is owner lore too, same standing as
  the Personna's. Source: simpleflying.com (aviation press) +
  wegianwetshaving.com + deltamuseum.org. Learned 2026-10-29.
  Confidence: established (era practice); the Personna tie remains a lead.
  **ADDENDUM 2026-10-29 ~14:30 CDT — airline follow-ups (2) and (3)
  [catalog]: (2) did Gillette or Schick ever make an airline-marketed
  razor variant? NEGATIVE: targeted searches (Pan Am/TWA airline razor,
  "airline"-branded safety razor, airline-collectible press/forums,
  eBay-style listings) surface NO airline-branded or airline-marketed
  Gillette or Schick razor anywhere. Gillette's travel marketing was
  consumer-directed (1920s travel kits, Tuckaway sets, the WWI Khaki Set
  Army contract) — sold to travelers, never airline-co-branded; no
  evidence of an airline contract like the Army's. (3) what razor brands
  appear in vintage first-class kit unboxings on collector forums?
  None: collector press (AntiquesQ&A, "wings"/B.O.A.C. guides) names
  kit razors only GENERICALLY ("kits can also contain razors, toothpaste
  and shampoo"); BOAC/TWA/Pan Am memorabilia guides list travel kits
  without contents. The ONE maker-named airline-razor fact anywhere is
  MODERN and is a standard retail product, not an airline variant:
  **Etihad Airways' first-class men's amenity kit, launched 12 May
  2011, carried the standard Schick Xtreme 3 disposable + shaving cream**
  (luxuo.com; abudhabicityguide.com with VP Product quote; first-
  class cabins Abu Dhabi↔London/Paris/Geneva/Sydney/Melbourne). Later
  Etihad kits (e.g. Christian Lacroix era, 2016) mention a shaving kit
  with no brand named. VERDICT: no cataloged product traces to airline
  marketing — airlines stocked bulk/unbranded amenity razors in the
  golden age (brand unpinned) and standard retail disposables in the
  modern era; "airline razor" is never a catalog identity. Source:
  web searches 2026-10-29 + luxuo.com (2011-05-12) +
  simpleflying.com + antiquesqa.blogspot.com. Confidence: established
  (negative verdict: no variant found across targeted searches; Etihad
  fact primary-press). Backlog item "Airline amenity-razor follow-ups
  (2)+(3)" closed; (1) Delta museum photo read remains a live-browser
  job.

- **Lather Games 2026 ran in OCTOBER 2026** (established, dataset:
  "October 21 - Lather Games 2026 - Day 21" through "October 31 -
  Lather Games 2026 - Day 31: Halloween and Goodbye"). Themed days
  included Wild Thing Wednesday, Sheep-ruh Shursday, Stacking Day,
  Fougere Friday, Monster Mash (Oct 24), Reckoning Day (Oct 25), The
  Time Warp, Morning Wood Day, Graveyard Day (Oct 29), Halloween and
  Goodbye. The Oct 20–31 notes window is dominated by theme-day posts:
  closure/discontinuation claims cluster on Graveyard Day and several
  posts are in-character brand fiction (see product_aliases.md
  "Lather-Games fiction brands" — The Shave Repository, Grave Robber
  Soap Co.). Validator implication: late-October 2026 brand-status
  claims and one-off brand names from this window need the fiction
  check before any catalog action. (Learner run 2026-11-03.)
- **scsurffishing.com is dead** (established, Violanza firsthand,
  2026-10-29): the whole fishing forum is gone — "closed
  indefinitely," even old threads inaccessible. The dataset's
  "Fishing Forum Member's Homemade Shaving Soap" bare-maker cluster
  now has no provenance route; stays P-11 unresolved. (Learner run
  2026-11-03.)
- **vshod.com — "Shave Community - AU", Australian online shaving shop
  (established 2026-11-07, learner run).** Active and live Nov 2026
  (homepage + product pages read live; product pages crawled within
  days). AUD prices, free shipping in Australia; contact
  shave@vshod.com. Stock profile: Zenith (its own nav category
  "Zenith Products"), RazoRock, Omega, Proraso, Saponificio Varesino,
  Barrister and Mann, Martin de Candre, Fine Accoutrements, Haslinger,
  Mitchell's Wool Fat, Valobra, Mike's Natural. Community attestation:
  Madflava81's 2021-06-28 SOTD note ("an online shop called VSHOD...
  known for extremely fast - and free - shipping"); mammothben
  2024-03-29 links a vshod.com B&M Lavanille label image — the shop
  doubles as a label-photo source for validators. House line: numbered
  "CUSTOM MANCHURIAN SHAVING BRUSH 01–048" at $199.95 (lead: maker /
  knot identity unpinned).
  - **Catalog relevance [catalog]:** vshod's SEO titles coin "Zenith
    Barbers" for ordinary Zenith brushes with barber-style handles —
    neither a Zenith sub-brand nor a vshod private label; never create
    a "Zenith Barbers" entry (see hardware_lore.md Zenith run addendum
    2026-11-07). Sources: vshod.com homepage + Blue Cobalt product
    page (live 2026-11-07); sotd_2021_full.json, sotd_2024_full.json.
    Confidence: retailer existence + assortment established; "CUSTOM
    MANCHURIAN" maker = lead.
  - **Addendum 2026-11-09 (learner run):** line STILL LISTED — homepage
    (live read 2026-11-07; cached crawl 2026-04-21 re-read this run) shows
    all 48 numbered brushes, 01–048, each $199.95. But it has NO individual
    product pages: two Wayback CDX filtered queries over the full
    `vshod.com/shave-brushes/*` directory (validated after one
    "Temporarily Offline" reload each) returned 10 Manchurian URLs (all
    Zenith) + 21 Custom URLs (all generic custom-handle/synthetic) and
    ZERO numbered CUSTOM MANCHURIAN pages — the line is homepage-only.
    The generic `Custom-Shaving-Brush-Australia.html` page is a synthetic
    24mm brush, not this line. Maker/knot/handle identity stays UNPINNED
    (no maker attribution on the site; Manchurian badger by name only).
    Dataset: ZERO "manchurian 01/02" strings and zero vshod product
    strings in the full corpus (241,022 rows) — no entries owed.
    **GUARD [catalog]:** the 9 bare "Custom Manchurian" brush-field rows
    are NOT this line — enormoshob ×5 (2017, "Elite custom Manchurian
    26mm") and jmoney_84 ×4 (2018, "Custom manchurian (badger)", his
    2018-04-24 note ties it to a DG B5 knot). Never fold them into a
    vshod entry.

## Run 2026-11-15 ~11:06 CST — LATHERED Expo + 2026 industry moves (leads)

- **LATHERED Expo, Brooklyn (2026) [catalog]:** 215 wet-shaving and
  fragrance enthusiasts; "a NYC club vibe, with music playing, wine
  flowing and hors d'oeuvres"; Italian barber Daniele Maullu flew in from
  Rome to demonstrate. Hearth & Altar were invited participants. Source:
  The Lather Ledger, Nov 10, 2026 (full read). Established as an event;
  the 2026 date is the Ledger's year-in-review framing (exact day
  unpinned — lead).
- **Schick/Edgewell US blade-plant closure — LEAD (single podcast
  source):** Sharpologist WST ep. 200 (Jan 20, 2026): Schick is closing
  its Connecticut manufacturing plant for blades ("about 300 people are
  going to be laid off... making blades there for about 50 years");
  injector blades/cartridges unaffected (already made in China). Needs a
  news second source before established. New lead (c4-narrow-139).
- **The Holy Black, New York → Texas — LEAD (single podcast source):**
  Sharpologist WST ep. 200 (Jan 20, 2026): "the Holy Black is moving
  from New York to Texas." Host: "Not much information online yet."
  Needs a second source (maker announcement, retailer note). New lead
  (c4-narrow-140).
- **Mitchell's Wool Fat closure rumor — PERSISTS in trade press; verdict
  STANDS:** the same Jan 20, 2026 episode says "Mitchell's Woolfat
  closed up last year" — the same conflation the knowledge base already
  refuted (company ALIVE, Companies House Active, current retail stock;
  what ended ~2022 was the tallow formula). Do NOT re-open on the
  podcast claim alone; the established verdict is the citable fact.

## Run 2026-11-15 ~13:06 CST — WST ep. 200 leads resolved (see lineages.md run section)

- **Schick/Edgewell US blade-plant closure — PROMOTED TO ESTABLISHED (c4-narrow-139) [catalog]:** supersedes the lead entry above. WARN filed Nov 13, 2025; Milford, CT plant (10 Leighton Road) closes permanently by Dec 31, 2027; 293 jobs; part of consolidating four NA sites into one automated plant. Schick manufacturing in Milford since 1961 (64 years at announcement — the podcast's "about 50 years" understates it). Sources: Norwich Bulletin Nov 18, 2025 + Manufacturing Dive Feb 3, 2026. Catalog: US-made Schick blade era ends Dec 31, 2027.
- **The Holy Black, New York → Texas — DOWNGRADED, contradicted maker-side (c4-narrow-140) [catalog]:** supersedes the lead entry above. No second source; the maker's own homepage (live 2026-11-15) still says "based in Lindenhurst, New York" / "Made in NY"; dataset has zero move mentions (one false positive: Texas cedar). Do NOT cite a move. Re-open only on a maker announcement or a Texas address.

## Run 2026-11-15 ~15:06 CST — Schick Milford SKU map (see lineages.md run section)

- **Schick Milford SKU map — ESTABLISHED (c4-narrow-144) [catalog]:** Milford makes the **Hydro family blades** (Hydro 5 / Hydro 3 / Hydro Silk — "crafted and honed in the USA" from imported steel; cartridge assembly split: Hydro Connect 5 assembled in Milford per Schick's 2017 ITC counsel statement, Hydro Silk cartridges assembled in China with US-made blades) and **Xtreme3 Eco disposables** (company statement, 2012). **NOT Milford:** Quattro (blades Germany, Wilkinson Sword GmbH Solingen; razor assembled China/Mexico), injector blades "Chick" (China), Schick DE blades (Germany, Solingen — same factory as Wilkinson Sword), Proline B-20/P-30 (Japan). **CORRECTION to the 13:06 run:** the podcast's "cartridges unaffected (already made in China)" is CONTRADICTED for cartridges — only injector/Quattro/DE/Proline are unaffected by the Dec 31, 2027 closure. Dataset grounding: blade field is injector-dominated; only 54 Schick DE rows; modern systems negligible in the razor field — the map is era guidance, not matching volume. Hydro 5 standard cartridge assembly stays lead-grade (conflicting sources); Slim Twin / Exacta / standard Xtreme3 origin unpinned (c4-narrow-146/147/148/149).
