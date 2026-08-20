# AstAi Shodashavarga Method Specification

Version: `parashara_traditional_v1`

This document freezes the deterministic calculation convention used by AstAi v0.4. It is a computation specification, not an interpretation guide.

## Shared rules

- Input is exact Lahiri sidereal longitude in `[0°, 360°)`.
- Within-sign longitude is in `[0°, 30°)`.
- Equal amsa boundaries use half-open intervals `[start, end)`.
- Output sign index is normalized modulo 12.
- Within-varga degree is derived from the exact source longitude and normalized to `[0°, 30°)`.
- D30 is unequal and uses its selected unequal segment for degree normalization.

## Classical set

| Code | Name | Frozen rule |
| --- | --- | --- |
| D1 | Rasi | Source sign |
| D2 | Hora | Traditional Sun/Moon Hora: odd signs Leo then Cancer; even signs Cancer then Leo |
| D3 | Drekkana | 1st, 5th, 9th from source sign |
| D4 | Chaturthamsa | 1st, 4th, 7th, 10th from source sign |
| D7 | Saptamsa | Odd signs count from source; even signs count from 7th from source |
| D9 | Navamsa | Movable from own sign; fixed from 9th; dual from 5th |
| D10 | Dasamsa | Odd signs from own sign; even signs from 9th |
| D12 | Dwadasamsa | Count from source sign |
| D16 | Shodasamsa | Movable from Aries; fixed from Leo; dual from Sagittarius |
| D20 | Vimsamsa | Movable from Aries; fixed from Sagittarius; dual from Leo |
| D24 | Chaturvimsamsa | Odd signs from Leo; even signs from Cancer |
| D27 | Saptavimsamsa | Fire from Aries; earth from Cancer; air from Libra; water from Capricorn |
| D30 | Trimsamsa | Traditional unequal Parashari segments |
| D40 | Khavedamsa | Odd signs from Aries; even signs from Libra |
| D45 | Akshavedamsa | Movable from Aries; fixed from Leo; dual from Sagittarius |
| D60 | Shashtiamsa | 60 half-degree segments counted from the source sign |

## D30 unequal segments

Odd zodiac signs:

- 0°-5° -> Aries
- 5°-10° -> Aquarius
- 10°-18° -> Sagittarius
- 18°-25° -> Gemini
- 25°-30° -> Libra

Even zodiac signs:

- 0°-5° -> Taurus
- 5°-12° -> Virgo
- 12°-20° -> Pisces
- 20°-25° -> Capricorn
- 25°-30° -> Scorpio

## D60 caution

AstAi v0.4 uses the explicitly named traditional **from-sign** D60 mapping. Software packages expose other D60 variants. AstAi will add alternate methods only as separately named conventions.

D60 has 0.5° source segments. The D60 Ascendant can therefore change quickly with birth time and must be interpreted only with adequate birth-time accuracy. AstAi records user-supplied birth-time uncertainty but does not invent a numerical confidence score.

## AstroSage reference compatibility profile

`astrosage_reference_compat_v1` leaves every varga above unchanged except D7 amsa selection.

Across two public AstroSage Brihat reports, all published D7 signs are reproduced when the integer degree within the source sign is used to select the D7 segment. This profile exists solely to make the compatibility behavior reproducible and auditable. It is not claimed to be the classical Parashari rule.

The default profile remains `parashara_traditional`.

## Validation sources

AstAi uses public vendor tables as compatibility fixtures, including:

- `https://www.astrosage.com/pdf/brihat-horoscope.pdf`
- `https://www.astrosage.com/pdf/poojasharmaE.pdf`

An independent open-source Jyotisha implementation (PyJHora) was also inspected as a cross-check for convention families. AstAi's implementation is independently written and does not import or copy that project's code.
