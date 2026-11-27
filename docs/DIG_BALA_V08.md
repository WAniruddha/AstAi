# Dig Bala v0.8 — isolated methodology freeze

This slice implements **Dig Bala (directional strength)** as a standalone, auditable backend calculation. It is intentionally not yet added to `ChartResponse`, the Streamlit Shadbala table, or aggregate Shadbala.

## Frozen BPHS rule

BPHS 27.7 assigns each classical planet a directionally weakest angular house. Dig Bala is the angular separation from that weak point, folded into `0..180°`, divided by 3.

Therefore:

`Dig Bala virupas = shortest angular distance(planet, weak point) / 3`

The range is exactly `0..60` virupas.

| Planet(s) | Weak point | Full-strength point |
| --- | ---: | ---: |
| Sun, Mars | 4th Bhava Madhya | 10th Bhava Madhya |
| Jupiter, Mercury | 7th Bhava Madhya | 1st Bhava Madhya |
| Moon, Venus | 10th Bhava Madhya | 4th Bhava Madhya |
| Saturn | 1st Bhava Madhya | 7th Bhava Madhya |

At the weak point the score is `0`. Exactly 180° opposite it the score is `60`.

## AstAi angular-point source

Methodology id:

`bphs_dig_bala_bhava_madhya_v1`

Zero-point source id:

`sidereal_sripati_bhava_madhya_quadrants`

AstAi will use the already-audited **sidereal Sripati Bhava Madhya** longitudes for houses 1, 4, 7 and 10. These are the Ascendant, IC, Descendant and MC directional axes in the existing Bhava framework.

This deliberately avoids substituting whole-sign house centers. BPHS speaks in terms of the angular house points, and the working rule is continuous by longitude rather than a discrete house-membership score.

## Classical scope

Only Sun, Moon, Mars, Mercury, Jupiter, Venus and Saturn participate. Rahu, Ketu, Uranus, Neptune and Pluto are rejected by the standalone API.

## Validation frozen in this slice

The focused tests prove:

- zero strength exactly at each planet's weak point;
- 60 virupas exactly 180° opposite;
- 30 virupas at a 90° separation on either side;
- correct wraparound across 0°/360°;
- exact planet-to-direction mapping;
- the published Moon worked example `33°` versus meridian `97°` gives `64/3` virupas;
- all seven classical planets use the declared 1/4/7/10 Bhava Madhyas;
- all four angular Madhyas are required;
- nodes and outer planets are rejected.

## References used to freeze this slice

- BPHS 27.7 text and translation: https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/7
- Continuous angular Dig Bala explanation and Moon worked example: https://saravali.github.io/astrology/bala_dig.html

## Deliberately withheld

Until the user runs the isolated test slice locally, Dig Bala is **not** wired into:

- `ChartResponse.shadbala`;
- the Streamlit Shadbala inspection table;
- aggregate Shadbala;
- required-strength ratios or interpretation.
