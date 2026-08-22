# Shadbala foundation — v0.8

v0.8 begins the classical Shadbala engine with components whose formula and inputs are frozen independently before any aggregate strength is emitted.

## Scope of the first slice

Computed for Sun through Saturn only:

- Uchcha Bala
- Ojayugma Rashi-amsha Bala
- Kendradi Bala
- Drekkana Bala
- Naisargika Bala

Deliberately **not yet computed**:

- Saptavargaja Bala
- complete Sthana Bala
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

## Frozen formulas

### Uchcha Bala

BPHS 27.1: measure the shortest angular distance from the planet's deep debilitation point, limited to 180 degrees, and divide by 3.

Therefore:

- deep debilitation = 0 virupas
- 90 degrees from deep debilitation = 30 virupas
- deep exaltation = 60 virupas

Deep exaltation/debilitation degrees use the standard seven-planet values listed in Phaladeepika 1.6.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/1
https://vedicpupil.in/library/phaladeepika-book-by-mantreswara/rashi-zodiac-signs-ch1/6

### Ojayugma Rashi-amsha Bala

BPHS 27.2/27.5:

- Moon and Venus receive 15 virupas for an even Rashi and another 15 for an even Navamsha.
- Sun, Mars, Mercury, Jupiter and Saturn receive 15 for an odd Rashi and another 15 for an odd Navamsha.

Range: 0, 15 or 30 virupas.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/5

### Kendradi Bala

BPHS 27.5:

- Kendra houses 1/4/7/10 = 60 virupas
- Panaphara houses 2/5/8/11 = 30 virupas
- Apoklima houses 3/6/9/12 = 15 virupas

AstAi v0.8 uses the primary Parashari Whole Sign Lagna house for this component. It does not substitute Sripati or Placidus houses.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/5

### Drekkana Bala

BPHS 27.6:

- male planets Sun, Mars, Jupiter receive 15 virupas in the first 10 degrees
- hermaphrodite planets Mercury, Saturn receive 15 virupas in the middle 10 degrees
- female planets Moon, Venus receive 15 virupas in the final 10 degrees

Otherwise the component is zero.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/6

### Naisargika Bala

BPHS 27.14: divide 60 by 7 and multiply by 1 through 7 for Saturn, Mars, Mercury, Jupiter, Venus, Moon and Sun respectively.

This produces fixed chart-independent values.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/14

## Why Saptavargaja is withheld

The text/source evidence and modern working software traditions disagree on the exact dignity weights used for Adhimitra/Sama/Shatru/Adhishatru categories.

One BPHS translation gives:

`45, 30, 20, 15, 10, 4, 2`

for Moolatrikona, own, great friend, friend, neutral, enemy and great enemy.

Several modern implementations use proportional half-step values:

`45, 30, 22.5, 15, 7.5, 3.75, 1.875`.

There are also implementation differences around compound friendship and D2/Hora convention. AstAi will not silently choose one and then publish a complete Sthana Bala as if the convention were universal.

Until that profile is frozen, the engine exposes only `sthana_known_subtotal_virupas` and leaves both `saptavargaja_bala_virupas` and `sthana_bala_total_virupas` unset.

Reference:
https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/2

## Audit rule

A v0.8 foundation result is valid only when:

- exactly seven classical planetary rows are present;
- Uchcha Bala remains in [0, 60];
- Ojayugma is one of 0/15/30;
- Kendradi is one of 15/30/60;
- Drekkana is one of 0/15;
- Naisargika values are the fixed 60/7 sequence;
- no complete Sthana Bala or Shadbala total is emitted while Saptavargaja remains unresolved.
