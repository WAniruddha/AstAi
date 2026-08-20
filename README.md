# AstAi

AstAi is being built as a **deterministic, auditable Jyotisha calculation engine first**, with knowledge/RAG and LLM interpretation layered on top later.

## Calculator v0.4

Implemented and regression-tested:

- Swiss Ephemeris integration with Lahiri sidereal mode
- actual ephemeris-backend detection and strict rejection of silent Moshier fallback
- historical IANA timezone handling with DST ambiguity/gap checks
- Sun through Saturn, Mean/True Rahu-Ketu, optional outer planets
- exact Ascendant and Midheaven
- D1 Whole Sign houses and a separate Lahiri sidereal Placidus cusp framework
- Nakshatra, Pada and Nakshatra Lord
- **all 16 classical Shodashavarga charts:** D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60
- explicit varga methodology/profile metadata and amsa-boundary distances
- traditional unequal D30 (Trimsamsa)
- explicit D60 birth-time sensitivity warning
- Panchanga: sunrise-aware Vara, Tithi, Paksha, Karana, Yoga, sunrise and sunset
- Vimshottari Mahadasha + Antardasha and birth balance
- deterministic calculation fingerprint
- FastAPI endpoint and Streamlit calculation lab
- independent astronomy and varga-mapping validation tracks

### Varga profiles

Default:

```json
"varga_profile": "parashara_traditional"
```

This uses exact source longitude and the frozen `parashara_traditional_v1` formulas documented in [`docs/VARGA_METHODS.md`](docs/VARGA_METHODS.md).

For compatibility testing with the two public AstroSage Brihat reports, an explicit profile is also available:

```json
"varga_profile": "astrosage_reference_compat_v1"
```

It changes **only D7 amsa selection** using an empirically observed whole-degree selection behavior that reproduces those published tables. It is not treated as the classical default.

## Important ephemeris requirement

`pyswisseph` can fall back to the built-in Moshier ephemeris if Swiss data files are unavailable.

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

AstAi treats external astrology software as **compatibility references**, not astronomical truth. High divisional charts can change sign after arcsecond-level source-longitude differences, so ephemeris agreement and varga-formula agreement are tested independently.

## Architecture principle

```text
Birth data
  -> historical civil-time normalization
  -> astronomical ephemeris
  -> canonical sidereal chart data
  -> deterministic Jyotisha transformations
  -> validation/audit
  -> later: knowledge/RAG + LLM interpretation
```

No LLM is allowed to invent planetary degrees, Vargas, cusps, Nakshatras or dasha dates.
