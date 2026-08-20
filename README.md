# AstAi

AstAi is being built as a **deterministic, auditable Jyotisha calculation engine first**, with LLM/RAG interpretation layered on top later.

## Calculator v0.2

Implemented now:

- Swiss Ephemeris integration with Lahiri sidereal mode
- actual ephemeris-backend detection
- strict mode that refuses silent Moshier fallback
- historical IANA timezone handling with DST ambiguity checks
- Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
- Mean or True Rahu/Ketu
- optional Uranus, Neptune, Pluto
- exact Ascendant and Midheaven
- D1 Whole Sign houses
- separate Lahiri sidereal Placidus cusps
- Nakshatra, Pada and Nakshatra Lord
- D9 Navamsa
- D10 Dasamsa
- basic Panchanga: Vara, Tithi, Paksha, Karana, Yoga
- Vimshottari Mahadasha + Antardasha and birth balance
- FastAPI endpoint
- Streamlit calculation lab
- external-reference validation tests

## Important ephemeris requirement

`pyswisseph` can fall back to the built-in Moshier ephemeris if Swiss data files are unavailable.

For professional production use, configure:

```bash
export ASTAI_EPHE_PATH=/absolute/path/to/verified/swisseph/data
```

and keep the API input default:

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

Streamlit:

```bash
streamlit run streamlit_app.py
```

Tests:

```bash
pytest -q
```

## Validation

See [`docs/VALIDATION.md`](docs/VALIDATION.md).

The first external golden fixture is a public AstroSage sample report. AstAi distinguishes external-software compatibility from strict astronomical conformance; it does not treat any astrology website as the source of astronomical truth.

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
