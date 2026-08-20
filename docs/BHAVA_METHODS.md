# Bhava / Chalit Methodology

## Frozen v0.5 method

AstAi v0.5 uses:

`sripati_bhava_chalit_v1`

This is explicitly separate from Whole Sign D1 houses and from Placidus/KP cusps.

## Mathematical construction

1. Calculate Lahiri sidereal Porphyry house cusps.
2. Interpret those Porphyry cusps as **Bhava Madhya**:
   - Bhava 1 Madhya = Ascendant.
   - Bhava 10 Madhya = Midheaven.
   - the four ecliptic quadrants are trisected.
3. For each Bhava, calculate its starting **Sandhi** as the forward zodiac midpoint between the previous Bhava Madhya and the current Bhava Madhya.
4. The ending Sandhi is the next Bhava's starting Sandhi.
5. House membership uses half-open intervals `[start, end)`.
6. A tiny `1e-10°` equality epsilon assigns a point numerically indistinguishable from a boundary to the incoming house.

This corresponds to the traditional Sripati construction documented by Swiss Ephemeris.

## Independent computational cross-check

AstAi derives the Sandhi boundaries from Porphyry Madhyas and independently compares them with Swiss Ephemeris native house system `S` (Sripati).

A calculation fails if the maximum difference exceeds the internal cross-check tolerance.

Swiss Ephemeris documentation identifies:
- `O` = Porphyry
- `S` = Sripati

and describes Sripati as Porphyry quadrants followed by moving each house cusp to the midpoint between the previous and current Porphyry cusp.

## Chalit rule

Bhava Chalit does **not** move a planet to another zodiac sign.

AstAi therefore stores both:

- `rasi_sign` / Whole-Sign house
- `bhava_house`

A `shifted=true` flag means only the Bhava house changed.

## What v0.5 does not claim

AstAi does not yet claim that every commercial application's label “Bhava Chalit” uses the same Sripati convention. Vendor-specific compatibility must be established with explicit fixtures, not assumed.
