# AstAi Calculator Validation Standard

AstAi separates **astronomical/scientific validation** from **astrological interpretation**.

Astronomy and deterministic mathematics can be tested scientifically for reproducibility and numerical agreement. Predictive astrological claims belong to a separate interpretation layer and are not described as scientifically validated by this calculator.

## Validation tiers

### Tier 1: input-time correctness

- IANA historical timezone conversion is mandatory.
- DST-nonexistent local times are rejected.
- DST-ambiguous local times require explicit `timezone_fold`.
- Coordinates are authoritative; place names are display metadata only.
- Latitude/longitude use north/east positive convention.
- The current calendar contract is proleptic Gregorian.

### Tier 2: ephemeris integrity

Production mode uses `ephemeris_policy="strict_swiss"`.

AstAi inspects Swiss Ephemeris return flags. If the runtime silently falls back to the built-in Moshier ephemeris, strict mode fails rather than pretending Swiss/JPL files were used.

Set `ASTAI_EPHE_PATH` to a verified Swiss Ephemeris data directory for strict production calculations.

Development and cross-vendor tests may use `ephemeris_policy="allow_moshier"`; the actual backend is always recorded in metadata and audit output.

### Tier 3: scientific/convention anchors

Tests include an official Swiss Ephemeris Lahiri ayanamsa anchor at J2000 (JD 2451545.0 TT): `23°51′25.5324″`, plus the invariant that tropical longitude minus recorded Lahiri ayanamsa reproduces each physical body's sidereal longitude to floating-point precision.

Swiss Ephemeris reference: https://www.astro.com/swisseph-download/doc/swisseph.pdf

### Tier 4: deterministic Jyotisha invariants

Tests cover:

- all sign/Nakshatra/Pada boundary neighborhoods
- DMS display rollover safety
- exact 180° Rahu/Ketu opposition
- whole-sign D1 houses
- sidereal Placidus cusps as a separate framework
- D9 Navamsa mapping
- D10 Dasamsa mapping
- sunrise-aware Hindu weekday
- Tithi/Paksha/Karana/Yoga from exact Sun/Moon longitudes
- Vimshottari birth balance and ordered MD/AD generation
- deterministic calculation fingerprints

### Tier 5: external compatibility fixtures

External vendor reports are compatibility references, not astronomical truth.

Current golden fixtures:

1. AstroSage Career Report sample: 11 April 1979, 18:23:24, Agra.
2. AstroSage Brihat Horoscope sample: 23 August 1979, 23:53:18, Delhi.

The reports publish birth data, Lahiri ayanamsa, Ascendant, planetary positions, Panchanga, sunrise/sunset and Vimshottari balance. Fixtures preserve the source URL and page numbers.

Cross-vendor standards:

1. **Categorical equality:** sign, Nakshatra and Pada must agree exactly.
2. **Longitude compatibility:** currently within `0.05°` (3 arcminutes) for these historical AstroSage reports.
3. **Solar events:** sunrise/sunset within 60 seconds for the selected fixtures.
4. **Ayanamsa display:** within 5 arcseconds of the vendor's displayed rounded value.
5. **Dasha balance:** exact where the report and convention align, with an explicitly stored small day tolerance where legacy vendor rounding differs.

The relatively loose vendor longitude tolerance is **not** the scientific ephemeris tolerance. It exists because legacy astrology software can use different ephemeris generations, rounding and internal conventions. AstAi must not deliberately degrade Swiss Ephemeris precision merely to reproduce an older vendor's printed number.

## Current status: v0.3

Implemented and tested:

- Sun through Saturn
- Mean or True Rahu/Ketu
- optional Uranus/Neptune/Pluto
- precise Lahiri Ascendant and Midheaven
- D1 Whole Sign
- Lahiri sidereal Placidus cusps
- Nakshatra/Pada/Star Lord
- D9
- D10
- Panchanga with sunrise/sunset and sunrise-based Vara
- Vimshottari Mahadasha and Antardasha
- backend audit metadata
- calculation fingerprint
- two independent external golden fixtures

Not yet certified:

- full Shodashvarga
- Bhava Chalit convention
- Shadbala / Bhava Bala
- Ashtakavarga
- KP subdivisions and significator logic
- Upagrahas

Those modules are added only after their formula convention is frozen and their own reference fixtures exist.
