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

The resulting D1 Panchadha-Maitri relationship matrix is reused for all seven Vargas. This follows BPHS computational notes that explicitly say compound relationships are to be taken from the Rashi chart rather than recalculated in the concerned divisional chart. It also reproduces a well-known B. V. Raman worked Saptavargaja table under the modern score profile.

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

This is the textual BPHS scoring sequence. The verses state that the same values occur for the other six divisional occupations.

Moolatrikona handling is deliberately split by chart type:

- **D1:** use the planet's BPHS Moolatrikona sign **and degree range**.
- **D2/D3/D7/D9/D12/D30:** use **Moolatrikona sign occupation only**. The normalized degree shown inside a higher Varga is not treated as a natal longitude for applying the D1 degree range.

This preserves the literal all-seven-Varga reading without inventing pseudo-longitude precision inside higher divisions.

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

This profile follows the widespread modern Panchadha-Maitri working table. Moolatrikona is applied only in D1; in the other six Vargas the placement is evaluated as own/friend/neutral/enemy according to the declared D1 relationship matrix.

## D1 Moolatrikona ranges

The BPHS degree ranges frozen for D1 are:

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
- profile metadata declares its Moolatrikona scope;
- the textual profile can reach 315 virupas when all seven placements are Moolatrikona under its declared reading;
- D1 uses exact Moolatrikona degree ranges;
- higher-Varga Moolatrikona in the textual profile is sign-based, not based on normalized Varga degrees;
- the modern profile limits Moolatrikona to D1;
- Panchadha-Maitri is derived from D1 and reused in the other Vargas;
- all seven required Vargas must be supplied;
- the D1 placement must agree with the D1 relationship chart;
- Rahu, Ketu, Uranus, Neptune and Pluto are rejected.

## References used to freeze this slice

- BPHS Saptavargaja verse/translation and textual dignity weights: https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/4
- BPHS chapter 27 computational notes: https://storage.yandexcloud.net/j108/library/hr6fkynz/Maharishi_Parashara_-_Brihat_Parasara_Hora_Sastra_%28Vol._1%29.pdf
- Higher-Varga Moolatrikona sign-only working convention: https://saravali.github.io/astrology/bala_sthana.html
- D1-only modern working table example: https://www.scribd.com/document/478806528/Shadbala-Performa-pdf
- D1 relationship reuse reconstruction against B. V. Raman: https://www.vinayakhora.in/post/tatkalika-maitri-varga-charts/

## Deliberately still withheld

- choosing one Saptavargaja profile as AstAi Standard;
- wiring Saptavargaja into the existing Shadbala foundation rows;
- complete Sthana Bala;
- any aggregate Shadbala score or required-strength ratio.

Those steps happen only after this corrected isolated slice is re-tested locally and the full regression suite remains green.
