# Aṣṭakavarga reductions — v0.7

v0.7 adds **audited reduction layers** on top of the v0.6 raw/unreduced BAV and SAV data. Raw values remain preserved and are never overwritten.

## AstAi Standard reduction profile

`bphs_common_v1`

### Trikoṇa Śodhana

For each BAV row, process the four trines:

- Aries / Leo / Sagittarius
- Taurus / Virgo / Capricorn
- Gemini / Libra / Aquarius
- Cancer / Scorpio / Pisces

Subtract the smallest value in each trine from all three members. If the smallest value is zero, that trine is unchanged. This implementation is cross-checked against the published AstroPDF 2015 sample's full post-Trikoṇa table.

### Ekādhipatya Śodhana

After Trikoṇa Śodhana, process the five dual-ownership pairs:

- Mars: Aries / Scorpio
- Venus: Taurus / Libra
- Mercury: Gemini / Virgo
- Jupiter: Sagittarius / Pisces
- Saturn: Capricorn / Aquarius

Sun and Moon do not participate because they each own one sign.

For `bphs_common_v1`, a sign is considered occupied when at least one of the seven classical planets (Sun through Saturn) is in that sign. Rahu, Ketu, Uranus, Neptune, Pluto and the Ascendant do not count as occupancy.

Rules used:

1. If either paired sign has zero after Trikoṇa, do nothing.
2. If both signs are occupied, do nothing.
3. If both are unoccupied and unequal, assign the smaller value to both.
4. If both are unoccupied and equal, reduce both to zero.
5. If one is occupied and the other empty, keep the occupied value unchanged and reduce the empty value by the occupied value, with a floor of zero.

This is the common BPHS rule family and is independently consistent with the open-source Maitreya implementation. Some Phaladeepika/Mantreśvara-derived software uses a different Ekādhipatya convention; AstAi does not silently mix that variant into the standard profile.

## Śodhya Piṇḍa

Piṇḍa is calculated only from the **post-Ekādhipatya** BAV values.

For every target BAV:

- `Rāśi Piṇḍa` = sum of each reduced sign value × that sign's declared multiplier.
- `Graha Piṇḍa` = for each of Sun through Saturn, take the reduced value in the planet's natal sign × that planet's declared multiplier, then sum.
- `Śodhya Piṇḍa` = Rāśi Piṇḍa + Graha Piṇḍa.

The common Graha multiplier table emitted by v0.7 is:

| Graha | Multiplier |
| --- | ---: |
| Sun | 5 |
| Moon | 5 |
| Mars | 8 |
| Mercury | 5 |
| Jupiter | 10 |
| Venus | 7 |
| Saturn | 5 |

## Why Piṇḍa profiles are explicit

Circulated BPHS translations contain internal inconsistencies between prose and parenthetical multiplier tables, and working software traditions also differ. AstAi therefore records the multiplier profile instead of hiding the choice.

### `bphs_parenthetical_v1` — AstAi Standard

Rāśi multipliers in Aries→Pisces order:

`7, 10, 8, 4, 10, 6, 7, 8, 9, 5, 11, 12`

This follows the commonly printed parenthetical *Rāśiman Chakra* table.

### `legacy_virgo5_v1` — compatibility/reference profile

Rāśi multipliers:

`7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 11, 12`

This differs only at Virgo and reproduces the published Piṇḍa arithmetic in the AstroPDF 2015 sample when applied to that vendor's own post-Ekādhipatya rows.

## Validation fixture

`tests/fixtures/astropdf_ashtakavarga_reductions_2015.json`

Source: `https://astropdf.com/files/sample-english-south.pdf`, pages containing the Aṣṭakavarga reduction tables and Piṇḍa summary.

The fixture is deliberately split by methodology status:

- raw BAV: transcribed reference evidence;
- after Trikoṇa: exact validation target for AstAi's common Trikoṇa algorithm;
- published after Ekādhipatya: retained as vendor evidence, **not** asserted to equal `bphs_common_v1`;
- published Piṇḍa: used to validate the `legacy_virgo5_v1` arithmetic against the vendor's supplied post-Ekādhipatya rows.

This distinction prevents vendor-specific reduction conventions from being mistaken for universal classical rules.

## Audit guarantees

v0.7 requires that:

- raw v0.6 BAV/SAV values remain unchanged;
- Trikoṇa never increases any sign value;
- common Ekādhipatya never increases a Trikoṇa value;
- every Śodhya Piṇḍa equals Rāśi Piṇḍa + Graha Piṇḍa;
- reduction and multiplier methodology are present in structured output;
- nodes and outer planets do not leak into the classical reduction occupancy or Graha Piṇḍa calculation.
