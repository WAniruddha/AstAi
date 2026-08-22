# Saptavargaja Bala — isolated v0.8 validation slice

This module is intentionally **not yet integrated** into `ChartResponse`, the Streamlit UI, or complete Sthana Bala. It exists so the disputed Saptavargaja rules can be tested independently before they affect any aggregate strength.

## Seven Vargas

The calculation consumes already-derived placements for:

- D1 Rashi
- D2 Hora
- D3 Drekkana
- D7 Saptamsa
- D9 Navamsa
- D12 Dwadashamsa
- D30 Trimsamsa

The module does **not** decide how those Vargas are constructed. AstAi's audited divisional-chart engine remains the source of those placements when integration happens later.

## Relationship methodology

`d1_panchadha_maitri_reused_across_saptavargas_v1`

Natural friendship is combined with temporary friendship from the D1 planetary arrangement to produce the fivefold relationship:

- great friend / Adhimitra
- friend / Mitra
- neutral / Sama
- enemy / Shatru
- great enemy / Adhishatru

Temporary friends are planets in the 2nd, 3rd, 4th, 10th, 11th or 12th from the target planet in D1; the remaining relative houses are temporary enemies.

The resulting D1 Panchadha-Maitri relationship matrix is reused for all seven Vargas. This follows the working convention described in R. Santhanam's BPHS notes and V. P. Jain's Shadbala/Bhavabala teaching material rather than recomputing temporary friendship separately inside every divisional chart.

## Profile 1 — `bphs_textual_all_vargas_v1`

Scores in virupas:

| Dignity | Virupas |
| --- | ---: |
| Moolatrikona | 45 |
| Own | 30 |
| Great friend | 20 |
| Friend | 15 |
| Neutral | 10 |
| Enemy | 4 |
| Great enemy | 2 |

This is the literal BPHS scoring sequence given in the Saptavargaja verses. The same dignity sequence is applied across all seven Vargas in this profile because the verse states that the values similarly occur in the other six divisional occupations.

This is intentionally labelled a **literal textual reading**, not a claim that every working tradition applies Moolatrikona outside D1.

## Profile 2 — `modern_panchadha_d1_mt_v1`

Scores in virupas:

| Dignity | Virupas |
| --- | ---: |
| Moolatrikona | 45 |
| Own | 30 |
| Great friend | 22.5 |
| Friend | 15 |
| Neutral | 7.5 |
| Enemy | 3.75 |
| Great enemy | 1.875 |

This profile follows the widespread Panchadha-Maitri working table found in Shadbala teaching material and software-compatible examples. Moolatrikona is applied only in D1; in the other six Vargas the placement is evaluated as own/friend/neutral/enemy according to the declared D1 relationship matrix.

## Moolatrikona ranges

The BPHS degree ranges frozen for this slice are:

| Planet | Sign | Range |
| --- | --- | --- |
| Sun | Leo | 0°–20° |
| Moon | Taurus | 3°–30° |
| Mars | Aries | 0°–12° |
| Mercury | Virgo | 15°–20° |
| Jupiter | Sagittarius | 0°–10° |
| Venus | Libra | 0°–15° |
| Saturn | Aquarius | 0°–20° |

Intervals are implemented as half-open `[start, end)` to match AstAi's other exact-boundary calculations.

## Validation guarantees

The isolated tests require that:

- both scoring tables are emitted exactly and never silently converted;
- the textual profile can reach 315 virupas when all seven placements are Moolatrikona under its declared reading;
- the modern profile limits Moolatrikona to D1;
- Panchadha-Maitri is derived from D1 and reused in the other Vargas;
- all seven BPHS Moolatrikona degree ranges are boundary-tested;
- all seven required Vargas must be supplied;
- the D1 placement must agree with the D1 relationship chart;
- Rahu, Ketu, Uranus, Neptune and Pluto are rejected.

## References used to freeze this slice

- BPHS Saptavargaja verses and dignity weights: https://vedicspace.com/bphs/28
- BPHS Saptavargaja translation listing the seven Vargas: https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/4
- BPHS Moolatrikona ranges: https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/graha-gunas-planetary-qualities-ch3/53
- Modern Panchadha-Maitri/Shadbala working table and D1-only relationship matrix: https://pdfcoffee.com/shadbala-and-bhavabala-calculationpdf-pdf-free.html

## Deliberately still withheld

- choosing one Saptavargaja profile as AstAi Standard;
- wiring Saptavargaja into the existing Shadbala foundation rows;
- complete Sthana Bala;
- any aggregate Shadbala score or required-strength ratio.

Those steps happen only after the user runs the isolated test slice locally and the full regression suite remains green.
