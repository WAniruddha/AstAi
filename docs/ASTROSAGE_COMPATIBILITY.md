# AstroSage compatibility and benchmark policy

AstAi uses external astrology software as a **compatibility reference**, not as astronomical ground truth. The deterministic source of chart data remains the declared ephemeris and the frozen AstAi methodology.

## Saswad 2000 benchmark

v0.5.1 stores a user-supplied AstroSage **Traditional** screenshot as a named compatibility fixture:

- date: 27 August 2000
- time: 13:37:00
- place printed: Saswad
- ayanamsa printed: Lahiri
- longitude printed: `74.0.E`
- latitude printed: `18.32.N`
- Mean Rahu/Ketu in the supplied table

The screenshot provides an Ascendant plus positions for Sun through Saturn, Rahu/Ketu, Uranus, Neptune and Pluto.

## Coordinate notation is unresolved

The legacy dotted coordinate notation in the screenshot is preserved exactly as printed. AstAi does **not** currently treat `18.32.N` as proven decimal degrees or proven degrees/minutes.

Different interpretations can move the Ascendant by several arcminutes while leaving geocentric planetary longitudes essentially unchanged. Because the source screenshot does not independently establish the coordinate convention used by that legacy report, the Saswad Ascendant is currently marked:

`TRANSCRIBED_NOT_COORDINATE_VERIFIED`

It is retained for future investigation but is not used as a numerical pass/fail target.

This reverses an earlier experimental reproduction assumption that treated `18.32.N` as `18°32′ N`. That interpretation happened to bring the computed Ascendant close to the screenshot, but numerical agreement alone is not enough evidence to freeze a vendor coordinate convention.

## What remains useful in the benchmark

The planetary table is still valuable as a cross-vendor compatibility reference because the AstAi planetary positions are geocentric. The current test suite tracks the supplied Sun-through-Pluto values with separate tolerance bands for classical planets, nodes and outer planets.

The larger outer-planet differences are documented rather than hidden or corrected with arbitrary offsets.

## Mean versus True Rahu/Ketu

Mean and True nodes are different astronomical models. They are not display aliases.

For the Saswad date/time, Mean Rahu lies in late Gemini while True Rahu lies in early Cancer. Changing the node model therefore requires recalculation and can change sign, Nakshatra, house and divisional placements.

The Streamlit UI stores the last calculated chart. When a calculation-driving setting changes, it marks the existing result as stale and asks the user to **Recalculate Kundali**.

## What the AstroSage compatibility profile means

`astrosage_reference_compat_v1` is **not an AstroSage astronomy mode**.

It is a narrow D7/Saptamsa compatibility profile based on behavior observed in two public AstroSage Shodashavarga tables. It changes D7 amsa selection only.

It does not change:

- planetary astronomy
- Ascendant calculation
- D1
- D2
- D9
- D10
- other Vargas
- Rahu/Ketu model
- Panchanga
- Vimshottari

The product UI therefore calls this setting **AstroSage D7 published-table compatibility** instead of the broader label “AstroSage compatibility”.

## Why AstAi does not call AstroSage as its calculator

AstAi should remain reproducible and auditable without depending on a third-party web calculator. Vendor outputs are used as compatibility fixtures and discrepancy reports.

A future vendor-compatibility layer may reproduce additional AstroSage conventions, but each convention must be isolated, named and tested. AstAi will not silently distort Swiss/JPL-derived astronomy merely to make one vendor table match.
