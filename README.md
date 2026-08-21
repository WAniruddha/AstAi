# AstAi

AstAi is being built as a **deterministic, auditable Jyotisha calculation engine first**, with knowledge/RAG and LLM interpretation layered on top later.

## Calculator v0.5.1

v0.5.1 is a product-input and presentation hotfix on top of the v0.5 calculator engine.

### India-first birth input

The Streamlit calculator now asks normal users for:

- name
- date of birth
- time of birth, including seconds when known
- country (India in this product phase)
- State / Union Territory
- city / town from an offline starter gazetteer

Latitude and longitude are filled automatically from the selected city and shown as locked decimal-degree fields. An optional **Use exact birth coordinates** checkbox unlocks latitude, longitude and elevation for an authoritative override. The India-only UI constrains latitude to 6–38° N and longitude to 68–98° E, with six-decimal display precision. `Asia/Kolkata` is resolved automatically.

The starter catalog covers all 36 Indian States/UTs and more than 100 major population centres. This requires **no external geocoding API**. A later India gazetteer release can expand the local place catalog without changing the astronomical engine or `BirthData` contract.

### Date-input fix

The UI declares an explicit birth-date range from `01/01/1900` through the current date and displays dates as `DD/MM/YYYY`. This removes Streamlit's implicit ±10-year limit around the initial widget value.

### Automatic ephemeris mode

Normal users no longer select Swiss/JPL versus Moshier.

- If `ASTAI_EPHE_PATH` is configured, AstAi automatically uses `strict_swiss` production mode.
- If it is not configured, the local development UI automatically allows the audited Moshier fallback and reports the actual backend in chart metadata.

Production deployment should still configure verified Swiss Ephemeris data files.

### Product chart presentation

- `ASC (Ascendant)` is the first row in **Planetary positions**.
- Uranus, Neptune and Pluto are always included by the Streamlit product as non-classical chart bodies and therefore propagate through D1, Bhava/Chalit and the divisional-chart placement tables.
- Traditional algorithms remain free to restrict themselves to their declared classical contributors; outer planets are not silently treated as classical planets.
- The D1 tab is labelled **Lagna (D1)**.
- The Moon-sign house is marked with `★` and the Ascendant/Lagna is stated in a small footnote below the D1 table.

## Calculator v0.5 capabilities

- Swiss Ephemeris integration with Lahiri sidereal mode
- historical IANA timezone handling with DST ambiguity/gap checks
- Sun through Saturn, Mean/True Rahu-Ketu, plus product-level Uranus/Neptune/Pluto placements
- exact Ascendant and Midheaven
- D1 Whole Sign houses
- Sripati Parashari Bhava/Chalit as a separate framework
- separate Lahiri sidereal Placidus cusps retained for the future KP engine
- Nakshatra, Pada and Nakshatra Lord
- all 16 classical Shodashavarga charts
- Panchanga with sunrise/sunset
- Vimshottari MD/AD/PD and five-level birth timing path
- deterministic calculation fingerprint and audit metadata
- FastAPI endpoint and Streamlit calculation lab

## House frameworks

AstAi intentionally keeps these separate:

1. `whole_sign` — primary D1/Parashari Rashi framework.
2. `sripati` — Parashari Bhava/Chalit framework.
3. `placidus` — separate cusp framework retained for the future KP module.

See [`docs/BHAVA_METHODS.md`](docs/BHAVA_METHODS.md), [`docs/VARGA_METHODS.md`](docs/VARGA_METHODS.md), [`docs/DASHA_METHODS.md`](docs/DASHA_METHODS.md), and [`docs/VALIDATION.md`](docs/VALIDATION.md).

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
streamlit run streamlit_app.py
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
streamlit run streamlit_app.py
```

FastAPI remains available separately:

```bash
uvicorn astai.api:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## Production ephemeris

For professional deployment:

```bash
export ASTAI_EPHE_PATH=/absolute/path/to/verified/swisseph/data
```

AstAi treats external astrology software as compatibility references, not astronomical truth. No LLM is allowed to invent planetary degrees, Vargas, cusps, Nakshatras, house placements or dasha dates.
