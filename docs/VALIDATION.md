# AstAi Calculator Validation Standard

AstAi separates **astronomical/scientific validation**, **deterministic Jyotisha formula validation**, **cross-vendor compatibility**, and **astrological interpretation**.

Astronomy and deterministic mathematics can be tested for reproducibility and numerical agreement. Predictive astrological claims belong to a later interpretation layer and are not described as scientifically validated by this calculator.

## Validation axes

### 1. Input and civil-time correctness

- IANA historical timezone conversion is mandatory.
- DST-nonexistent local times are rejected.
- DST-ambiguous local times require explicit `timezone_fold`.
- Coordinates are authoritative; place names are metadata.
- Current calendar contract: proleptic Gregorian.

### 2. Ephemeris integrity

Production mode uses `ephemeris_policy="strict_swiss"`.

AstAi inspects Swiss Ephemeris return flags. If `pyswisseph` falls back to Moshier, strict mode fails rather than claiming a Swiss/JPL file backend.

### 3. Scientific/convention anchors

Tests include:

- Swiss Ephemeris Lahiri ayanamsa anchor.
- tropical-minus-ayanamsa sidereal consistency.
- sign/Nakshatra/Pada boundaries.
- exact Rahu/Ketu opposition.
- historical DST behavior.
- sunrise/sunset behavior.
- deterministic fingerprints.

### 4. House-framework validation

v0.5 freezes `sripati_bhava_chalit_v1`.

AstAi independently:

1. obtains Lahiri sidereal Porphyry cusps as Bhava Madhya,
2. derives Sripati Sandhi boundaries by midpoint construction,
3. compares those derived boundaries with Swiss Ephemeris native Sripati system `S`.

The internal cross-check is numerical and fails if it exceeds tolerance.

Tests also assert:

- 12 house spans close exactly to 360 degrees,
- half-open boundary membership is deterministic,
- Chalit changes Bhava house only, never Rashi sign,
- Whole Sign, Sripati and Placidus remain separate response structures.

See [`BHAVA_METHODS.md`](BHAVA_METHODS.md).

### 5. Shodashavarga formula validation

The classical set is:

`D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60`.

The default methodology is `parashara_traditional_v1`. D30 uses unequal traditional segments and D60 is explicitly sensitivity-audited.

See [`VARGA_METHODS.md`](VARGA_METHODS.md).

### 6. Vimshottari validation

v0.5 extends the deterministic timeline to:

- Mahadasha
- Antardasha
- Pratyantardasha
- birth timing path through Sookshma and Prana

Tests assert parent/child closure, contiguity, non-overlap, partial-at-birth theoretical starts and at least 120 configured dasha years of post-birth coverage.

Calendar dates use explicit `dasha_year_days` (default 365.25); the displayed Y/M/D balance uses the traditional 360-day balance convention. Those conventions are not silently mixed.

See [`DASHA_METHODS.md`](DASHA_METHODS.md).

### 7. External vendor astronomy compatibility

Public AstroSage fixtures currently cover several 1978/1979 reports. They are compatibility references, not astronomical truth.

Typical checks include sign/Nakshatra/Pada equality, displayed longitude tolerances, solar-event tolerances, ayanamsa display and Vimshottari birth balance.

### 8. Varga compatibility is separate from astronomy

High Vargas can flip after very small source-longitude changes. Vendor source longitudes are therefore fed into formula compatibility tests separately from ephemeris agreement.

### 9. Explicit AstroSage D7 compatibility

`astrosage_reference_compat_v1` exists only to reproduce a documented D7 selection behavior in two public reports. Exact `parashara_traditional` remains the default.

## Current status: v0.5

Implemented and regression-tested:

- astronomical core and audit metadata,
- D1 Whole Sign,
- Sripati Bhava/Chalit with Swiss native cross-check,
- separate Placidus cusps,
- full classical Shodashavarga,
- Panchanga with sunrise/sunset,
- Vimshottari MD/AD/PD and five-level birth path,
- external astronomy and varga fixtures.

Not yet certified:

- Ashtakavarga,
- Shadbala / Bhava Bala,
- KP subdivisions and significator logic,
- Jaimini / Arudha,
- Upagrahas.

Deep Vimshottari calendar-date compatibility with specific vendors is not claimed until fixtures documenting each vendor's year-length convention are added.
