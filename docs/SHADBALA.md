# Shadbala foundation — v0.8

v0.8 builds the classical Shadbala engine in separately validated slices before any aggregate Shadbala strength is emitted.

## Current computed scope

Computed for Sun through Saturn only:

- Uchcha Bala
- Saptavargaja Bala
- Ojayugma Rashi-amsha Bala
- Kendradi Bala
- Drekkana Bala
- complete Sthana Bala
- Naisargika Bala as a separate Shadbala component

Still deliberately **not computed**:

- Dig Bala
- Kala Bala
- Chesta Bala
- Drik Bala
- aggregate Shadbala
- required-strength ratio
- planetary-war adjustment

No outer planet, Rahu, Ketu or Ascendant is allowed to enter the classical planetary-strength rows.

## Unit

All values are stored in **virupas**. Classical convention: 60 virupas = 1 rupa.

## Sthana Bala formula

AstAi v0.8 emits complete Sthana Bala only after all five constituent components are available:

`Sthana Bala = Uchcha + Saptavargaja + Ojayugma + Kendradi + Drekkana`

Naisargika Bala is **not** part of Sthana Bala. It remains a separate Shadbala component.

## Uchcha Bala

BPHS 27.1: measure the shortest angular distance from the planet's deep debilitation point, limited to 180 degrees, and divide by 3.

Therefore:

- deep debilitation = 0 virupas
- 90 degrees from deep debilitation = 30 virupas
- deep exaltation = 60 virupas

Deep exaltation/debilitation degrees use the standard seven-planet values listed in Phaladeepika 1.6.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/1
https://vedicpupil.in/library/phaladeepika-book-by-mantreswara/rashi-zodiac-signs-ch1/6

## Saptavargaja Bala

AstAi Standard is frozen as:

`bphs_textual_all_vargas_v1`

Scores in virupas:

`45 / 30 / 20 / 15 / 10 / 4 / 2`

for Moolatrikona, own, great friend, friend, neutral, enemy and great enemy.

Required Vargas:

- D1
- D2
- D3
- D7
- D9
- D12
- D30

Relationship methodology:

`d1_panchadha_maitri_reused_across_saptavargas_v1`

The compound relationship matrix is derived from D1 and reused across all seven Vargas.

Moolatrikona handling:

- D1 uses the exact Moolatrikona sign and degree range.
- D2/D3/D7/D9/D12/D30 use Moolatrikona sign occupation only under the textual profile.

The modern half-step profile remains available explicitly as:

`modern_panchadha_d1_mt_v1`

with scores:

`45 / 30 / 22.5 / 15 / 7.5 / 3.75 / 1.875`

It is not silently mixed into AstAi Standard.

The Saptavargaja calculation consumes the already-audited divisional charts. Therefore the ChartResponse also records `source_varga_profile`; if the D7 AstroSage compatibility setting is selected, the same selected D7 is used in Saptavargaja rather than calculating a hidden alternate D7.

See `docs/SAPTAVARGAJA_V08.md` for the full methodology notes.

## Ojayugma Rashi-amsha Bala

BPHS 27.2/27.5:

- Moon and Venus receive 15 virupas for an even Rashi and another 15 for an even Navamsha.
- Sun, Mars, Mercury, Jupiter and Saturn receive 15 for an odd Rashi and another 15 for an odd Navamsha.

Range: 0, 15 or 30 virupas.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/5

## Kendradi Bala

BPHS 27.5:

- Kendra houses 1/4/7/10 = 60 virupas
- Panaphara houses 2/5/8/11 = 30 virupas
- Apoklima houses 3/6/9/12 = 15 virupas

AstAi v0.8 uses the primary Parashari Whole Sign Lagna house for this component. It does not substitute Sripati or Placidus houses.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/5

## Drekkana Bala

BPHS 27.6:

- male planets Sun, Mars, Jupiter receive 15 virupas in the first 10 degrees
- hermaphrodite planets Mercury, Saturn receive 15 virupas in the middle 10 degrees
- female planets Moon, Venus receive 15 virupas in the final 10 degrees

Otherwise the component is zero.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/6

## Naisargika Bala

BPHS 27.14: divide 60 by 7 and multiply by 1 through 7 for Saturn, Mars, Mercury, Jupiter, Venus, Moon and Sun respectively.

This produces fixed chart-independent values.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/14

## ChartResponse integration

`ChartResponse.shadbala` now exposes a typed read-only calculation payload containing:

- methodology
- unit
- aggregation status
- Saptavargaja profile
- relationship methodology
- source Varga profile
- one row for each of Sun through Saturn
- all five Sthana Bala subcomponents
- complete Sthana Bala
- separate Naisargika Bala

The audit layer emits `SHADBALA_STHANA` with status `METHODOLOGY_DEPENDENT` because the Saptavargaja profile is an explicit convention choice.

No aggregate Shadbala value is present in the payload at this stage.

## Audit rules

A valid v0.8 Sthana payload requires that:

- exactly seven classical planetary rows are present;
- Uchcha Bala remains in [0, 60];
- Ojayugma is one of 0/15/30;
- Kendradi is one of 15/30/60;
- Drekkana is one of 0/15;
- Naisargika values are the fixed 60/7 sequence;
- Sthana Bala exactly equals the five declared Sthana components;
- Naisargika Bala is not included in Sthana Bala;
- the Saptavargaja and source Varga profiles are recorded;
- no aggregate Shadbala or required-strength ratio is emitted while Dig/Kala/Chesta/Drik remain pending.

## Current test gate

The typed ChartResponse integration must pass locally before the Streamlit Shadbala inspection tab is added. This keeps the UI dependent only on a payload that has already passed focused and full regression tests.
