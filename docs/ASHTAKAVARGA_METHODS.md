# Aṣṭakavarga methodology — v0.6

v0.6 implements the **raw, unreduced classical Aṣṭakavarga foundation**. The purpose of this release is to make the contribution matrix deterministic, inspectable and reference-testable before any reduction or interpretive layer is added.

## Included in v0.6

- Bhinnāṣṭakavarga (BAV) for Sun, Moon, Mars, Mercury, Jupiter, Venus and Saturn.
- Eight Prastāra contributor rows inside every planetary BAV: Sun through Saturn plus Ascendant/Lagna.
- Sarvāṣṭakavarga (SAV) as the sign-wise sum of the seven unreduced planetary BAV rows.
- Explicit methodology and reduction-status metadata.
- Golden-reference validation against the published AstroSage Delhi-1979 Brihat Horoscope Aṣṭakavarga tables.

## Intentionally not included yet

v0.6 does **not** calculate:

- Trikoṇa Śodhana
- Ekādhipatya Śodhana
- Śodhya Piṇḍa
- Aṣṭakavarga transit interpretation
- prediction or strength narratives

Those are separate audited transformations and must not be mixed into the raw scores.

## Point semantics

The internal representation avoids the bindu/rekhā terminology ambiguity found across different texts and software.

- `1` = benefic/supporting contribution
- `0` = no benefic/supporting contribution

Every Prastāra row contains exactly 12 binary values in Aries-through-Pisces order. A BAV sign score is the sum of the eight contributor values for that sign.

## Classical contributors

The seven BAV target planets are:

1. Sun
2. Moon
3. Mars
4. Mercury
5. Jupiter
6. Venus
7. Saturn

For each target planet, the contributors are those same seven planets plus **Ascendant/Lagna**.

Lagna is therefore a contributor to every BAV, but AstAi does **not** create an eighth Lagna BAV and does not add one to the standard SAV.

Rahu, Ketu, Uranus, Neptune and Pluto are not contributors to this classical raw Aṣṭakavarga implementation. Their presence elsewhere in the chart does not change the raw BAV/SAV result.

## Counting convention

Benefic houses are counted **inclusively** from the contributor's natal rāśi/sign. If a rule includes house 1, the contributor's own sign receives that contribution. House 2 is the next sign, and so on cyclically through house 12.

This makes raw Aṣṭakavarga depend on the rāśi/sign positions of the seven classical planets and the Ascendant, not on their exact within-sign degree.

## Fixed invariants

The classical unreduced BAV totals used as hard calculation invariants are:

| BAV | Total |
| --- | ---: |
| Sun | 48 |
| Moon | 49 |
| Mars | 39 |
| Mercury | 54 |
| Jupiter | 56 |
| Venus | 52 |
| Saturn | 39 |

The standard unreduced SAV total is therefore **337**.

If any of these invariants fail, AstAi treats it as a calculation/rule-table error rather than silently emitting the result.

## Golden-reference validation

The fixture `tests/fixtures/astrosage_ashtakavarga_1979.json` transcribes the raw BAV, full Prastāra and SAV tables from the public AstroSage *Brihat Horoscope* Delhi-1979 sample, printed pages 123–130.

The regression suite requires exact agreement for:

- all 84 BAV sign values (7 × 12),
- all 672 binary Prastāra contribution cells (7 × 8 × 12),
- all 12 SAV sign totals,
- each fixed BAV total,
- the SAV total of 337.

It also checks reconstruction invariants and zodiac-rotation invariance.

`REFERENCE_MATCHED` in the audit trail means the deterministic calculation matches that published reference under the declared methodology. It does **not** mean astrological interpretation or predictive claims have been scientifically validated.
