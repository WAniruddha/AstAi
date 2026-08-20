# AstAi

AstAi is being built as a **deterministic, auditable Jyotisha calculation engine first**, with knowledge/RAG and LLM interpretation layered on top later.

## Calculator v0.5

Implemented and regression-tested:

- Swiss Ephemeris integration with Lahiri sidereal mode
- actual ephemeris-backend detection and strict rejection of silent Moshier fallback
- historical IANA timezone handling with DST ambiguity/gap checks
- Sun through Saturn, Mean/True Rahu-Ketu, optional outer planets
- exact Ascendant and Midheaven
- D1 Whole Sign houses
- **Sripati Parashari Bhava/Chalit** as a separate framework
- separate Lahiri sidereal Placidus cusps retained for the future KP engine
- Nakshatra, Pada and Nakshatra Lord
- all 16 classical Shodashavarga charts: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60
- explicit varga methodology/profile metadata and amsa-boundary distances
- traditional unequal D30 and D60 sensitivity warnings
- Panchanga: sunrise-aware Vara, Tithi, Paksha, Karana, Yoga, sunrise and sunset
- Vimshottari Mahadasha, Antardasha, **Pratyantardasha**, plus the five-level birth timing path through Sookshma and Prana
- deterministic calculation fingerprint
- FastAPI endpoint and Streamlit calculation lab
- independent astronomy, house-system and varga-mapping validation tracks

## House frameworks

AstAi does **not** treat every house table as interchangeable:

1. `whole_sign` — primary D1/Parashari Rashi framework.
2. `sripati` — Parashari Bhava/Chalit framework. Planetary signs remain unchanged; only house membership can shift.
3. `placidus` — a separate cusp framework retained for the future KP module.

The frozen Sripati method is documented in [`docs/BHAVA_METHODS.md`](docs/BHAVA_METHODS.md).

## Varga profiles

Default:

```json
"varga_profile": "parashara_traditional"
```

This uses exact source longitude and the frozen `parashara_traditional_v1` formulas documented in [`docs/VARGA_METHODS.md`](docs/VARGA_METHODS.md).

An explicit `astrosage_reference_compat_v1` profile exists only for the documented D7 behavior in two public AstroSage tables. It is never substituted silently.

## Vimshottari

The dasha sequence/proportions are deterministic. Calendar dates use the explicit `dasha_year_days` input, default `365.25`. Displayed birth balance Y/M/D remains based on a 360-day dasha year. See [`docs/DASHA_METHODS.md`](docs/DASHA_METHODS.md).

## Important ephemeris requirement

For professional production use:

```bash
export ASTAI_EPHE_PATH=/absolute/path/to/verified/swisseph/data
```

and keep:

```json
"ephemeris_policy": "strict_swiss"
```

Strict mode fails instead of silently changing the astronomical backend.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn astai.api:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

```bash
streamlit run streamlit_app.py
pytest -q
```

## Validation

See [`docs/VALIDATION.md`](docs/VALIDATION.md).

AstAi treats external astrology software as **compatibility references**, not astronomical truth. No LLM is allowed to invent planetary degrees, Vargas, cusps, Nakshatras, house placements or dasha dates.
