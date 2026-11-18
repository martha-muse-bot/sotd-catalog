# Tech attribute-fold project (queued 2026-10-28, P-17)

Fold Gillette Tech variant clusters as attributes (aliases) on the verified
model entry `razor/gillette-tech` — do NOT create variant entries.

## Why (P-17)
A maker's named model is one entry; variant dimensions are attributes.
Tech has 9,121 posts, only 1,477 (16%) bare — the rest specify variants
across SEVERAL dimensions at once (era × handle × finish × country), which
entries cannot cover without combinatorial explosion.

## Attribute dimensions for Tech
- era: pre-war (triangle slots) / post-war (oval slots)
- handle: fat / ball-end / travel / solid / thin
- finish: gold / nickel / silver
- country: English / Canadian / US
- base plate: flat-bottom / oval-slot / triangle-slot
- year: date codes (Y3, K4, Z-4, B1, ...) as a year attribute, not a variant

## Scope
Orphan clusters to fold as aliases on `razor/gillette-tech`: flat-bottom
family, fat-handle family, ball-end family, pre-war / post-war families,
gold families, travel families, English / Canadian families, spiral tech
(English Tech handle variant per knowledge base), contract tech, and
handle-swap composites (resolve to the HEAD entry; the third-party handle
is an attribute value, never a handle entry — zero-handle settlement
stands). The clusters are already pending in the validation queue;
validators resolve them as attribute-aliases, not entries.

## EXCLUDED — do not fold without a further ruling
- **Ranger Tech / Milord** — sold under distinct model names but
  Tech-based. RESOLVED 2026-10-28 (Jim): own verified entry
  `razor/gillette-ranger-tech`; Milord as variant alias; clusters folded.
  NOT a Tech fold.
- **Other makers' Tech-styles** — Baili Tech copy, RazoRock Teck II, iKon
  Tek and similar stay separate entries. Brand is a hard boundary;
  attributes never cross makers.
- **Parallel distinct designs** — WR1 vs WR2, Timeless slant vs straight
  heads, etc. stay separate entries. P-17 covers revisions/variants of
  one model only.

## Status
Queued for the validator loop. Bare "Gillette Tech" posts need no
loose-alias treatment: bare means attributes unspecified, and bare is the
minority (16%) here, unlike Mongoose (99%).
