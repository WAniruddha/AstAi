# AstAi Calculator Validation Standard

AstAi separates **astronomical/scientific validation** from **astrological interpretation**.

The astronomy and deterministic mathematics can be tested scientifically for reproducibility and numerical agreement. Predictive astrological claims are a separate interpretive layer and are not described as scientifically validated by this calculator project.

## Validation tiers

### Tier 1: input-time correctness

- IANA historical timezone conversion is mandatory.
- DST-nonexistent local times are rejected.
- DST-ambiguous times require an explicit `timezone_fold`.
- Coordinates are authoritative; place names are display metadata only.

### Tier 2: ephemeris integrity

Production mode uses `ephemeris_policy="strict_swiss"`.

AstAi inspects the return flags from Swiss Ephemeris. If the runtime silently falls back to the built-in Moshier ephemeris, strict mode fails rather than pretending Swiss/JPL files were used.

Set `ASTAI_EPHE_PATH` to a verified Swiss Ephemeris data directory for strict production calculations.

Development and cross-vendor tests may use `ephemeris_policy="allow_moshier"`; the actual backend is always included in the output and audit.

### Tier 3: deterministic Jyotisha invariants

Tests cover:

- Lahiri sidereal zodiac mapping
- sign and degree boundaries
- 27 Nakshatras and 4 Padas
- Nakshatra lord mapping
- exact 180° Rahu/Ketu opposition
- whole-sign D1 houses
- sidereal Placidus cusps as a separate framework
- D9 Navamsa mapping
- D10 Dasamsa mapping
- Panchanga Tithi/Paksha/Karana/Yoga from exact Sun/Moon longitudes
- Vimshottari birth balance and MD/AD generation

### Tier 4: external compatibility fixtures

External vendor reports are treated as compatibility references, not as astronomical truth.

The first golden fixture is the public AstroSage Career Report sample for 11 April 1979, 18:23:24, Agra. AstroSage publishes Lahiri ayanamsa, Virgo Ascendant, planetary positions, Panchanga values, and Moon dasha balance in Appendix-A.

Because vendors can use different ephemeris generations, ayanamsa implementations, rounding and display conventions, cross-vendor tests use two standards:

1. **Categorical equality:** sign, Nakshatra and Pada must agree exactly.
2. **Longitude compatibility tolerance:** currently 0.05° (3 arcminutes) for the public AstroSage fixture.

This tolerance is deliberately separate from internal ephemeris conformance. Internal Swiss/JPL validation must be much tighter.

## Current status

Calculator v0.2 implements the hardened core:

- Sun through Saturn
- Mean or True Rahu/Ketu
- optional Uranus/Neptune/Pluto
- precise Lahiri Ascendant and Midheaven
- D1 Whole Sign
- Lahiri sidereal Placidus cusps
- Nakshatra/Pada/Star Lord
- D9
- D10
- basic Panchanga
- Vimshottari Mahadasha and Antardasha
- backend audit metadata

Not yet certified in v0.2:

- full Shodashvarga
- sunrise/sunset dependent Panchanga items
- Bhava Chalit convention
- Shadbala / Bhava Bala
- Ashtakavarga
- KP ayanamsa and KP subdivisions
- Upagrahas

Those modules should be added only with their own formula specification and reference fixtures.
