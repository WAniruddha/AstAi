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

Set `ASTAI_EPHE_PATH` to verified Swiss Ephemeris data files for production.

### 3. Scientific/convention anchors

Tests include:

- Swiss Ephemeris Lahiri ayanamsa J2000 anchor (`23°51′25.5324″`).
- Tropical longitude minus recorded Lahiri ayanamsa reproduces physical-body sidereal longitude to floating-point precision.
- sign/Nakshatra/Pada boundary neighborhoods.
- exact Rahu/Ketu opposition.
- historical DST gap/ambiguity behavior.
- sunrise/sunset and sunrise-based Hindu weekday behavior.
- deterministic calculation fingerprinting.

### 4. Shodashavarga formula validation

v0.4 freezes the classical set:

`D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60`.

The default methodology is `parashara_traditional_v1`. D30 uses traditional unequal segments. D60 uses the explicitly named traditional "from sign" method; other D60 variants are not silently merged into it.

Formula tests use exact source longitudes and explicit half-open amsa boundaries `[start, end)`.

Each varga output stores its methodology, amsa index, source amsa bounds and distance to the nearest exact amsa boundary. D60 always carries a sensitivity warning.

See [`VARGA_METHODS.md`](VARGA_METHODS.md).

### 5. External vendor astronomy compatibility

Current public fixtures include AstroSage reports for:

1. 11 April 1979, Agra.
2. 23 August 1979, Delhi.
3. 23 August 1978, Delhi.

Vendor reports remain compatibility references, not astronomical truth.

Typical checks:

- exact sign/Nakshatra/Pada equality,
- displayed longitude within an explicitly stored cross-vendor tolerance,
- sunrise/sunset within an explicitly stored tolerance,
- displayed ayanamsa within a small rounding tolerance,
- Vimshottari balance under the selected date convention.

### 6. Varga mapping compatibility is tested separately from astronomy

This separation is essential.

For example, in the 1978 AstroSage report, the printed Mars longitude is about 98 arcseconds away from the development ephemeris result. That difference is still within the broad historical vendor longitude tolerance, but it crosses a D45 amsa boundary because D45 segments are only 40 arcminutes wide.

Therefore AstAi does **not** say "D45 formula failed" merely because two ephemerides place a body on opposite sides of a high-varga boundary.

Instead:

- astronomy compatibility compares the two source longitudes;
- varga-formula compatibility feeds the vendor's own printed source longitude into the AstAi varga transform and compares the resulting vendor table.

This prevents both false failures and fake agreement.

### 7. AstroSage D7 compatibility profile

Across two public AstroSage Brihat tables (1978 and 1979), the otherwise unexplained D7 differences are reproduced consistently when the within-sign degree is truncated to a whole degree **only for selecting the D7 amsa**.

AstAi therefore provides `astrosage_reference_compat_v1` for explicit compatibility testing. The default remains exact `parashara_traditional` using 30/7 degree divisions. The compatibility behavior is labeled and audited; it is never silently substituted for the classical method.

## Current status: v0.4

Implemented and regression-tested:

- astronomical core and audit metadata,
- D1 Whole Sign and separate Placidus cusps,
- Nakshatra/Pada/Star Lord,
- full classical Shodashavarga,
- Panchanga with sunrise/sunset and sunrise-based Vara,
- Vimshottari Mahadasha and Antardasha,
- three AstroSage astronomy fixtures,
- two full AstroSage Shodashavarga table fixtures,
- exact classical and explicit vendor-compatibility varga profiles.

Not yet certified:

- Bhava Chalit convention,
- Vimshottari Pratyantar and deeper levels,
- Shadbala / Bhava Bala,
- Ashtakavarga,
- KP subdivisions and significator logic,
- Upagrahas.
