# AstAi Architecture

## Goal

AstAi is a reusable Jyotisha computation, verification and interpretation platform. Deterministic astronomical and astrological calculations are separated from probabilistic language-model interpretation.

## Build order

### Layer 0 — Input and provenance

Birth date, time, coordinates, IANA timezone, ayanamsa, node model and methodology choices are explicit inputs. Birth-time uncertainty is stored when supplied rather than converted into an invented confidence score.

### Layer 1 — Deterministic calculation core

Implemented through v0.5:

- Swiss Ephemeris astronomical basis
- Lahiri sidereal zodiac and Nakshatra/Pada
- D1 Whole Sign
- Sripati Bhava/Chalit as a separate Parashari framework
- Lahiri sidereal Placidus cusps as a separate future-KP framework
- full classical Shodashavarga
- Panchanga core
- Vimshottari MD/AD/PD plus five-level birth timing path

Later deterministic modules include Ashtakavarga, Shadbala/Bhava Bala, KP subdivisions/significators, Jaimini, Arudha and Upagrahas.

This layer is the source of truth for computed chart data.

### Layer 2 — Verification and audit

Golden fixtures and mathematical invariants are separated by domain:

- astronomy / ephemeris
- civil time
- house methodology
- varga transformations
- dasha sequencing

Small source-longitude differences are not confused with formula failures.

### Layer 3 — Knowledge layer

Books, rule catalogues and curated PDFs can later be indexed for retrieval. They answer which interpretive rule applies to already-calculated chart data; they do not replace calculation.

### Layer 4 — LLM orchestration

An LLM receives structured chart data and retrieved rules, then explains and synthesizes. It must never invent missing planetary degrees, cusps, Vargas, house assignments or dasha boundaries.

### Layer 5 — Product interfaces

FastAPI exposes machine-readable endpoints. Streamlit remains the development visualizer. A dedicated TypeScript/web/mobile client can replace it later without changing the calculation core.

## House-framework rule

AstAi intentionally preserves three different structures:

```text
D1 Whole Sign
    !=
Sripati Bhava / Chalit
    !=
Placidus cusp framework (future KP)
```

Bhava Chalit never changes a planet's zodiac sign. It only derives its Bhava house.

## Why not microservices yet?

The production shape remains a modular monolith while calculation conventions are being frozen and validated. Services, Redis, graph databases and vector databases are later scaling choices, not prerequisites for mathematical correctness.

## Current module map

```text
src/astai/
  engine/
    astronomy.py        # ephemeris, time normalization, Lagna, house geometry
    houses.py           # Sripati Bhava/Chalit
    vargas.py           # full classical Shodashavarga
    dasha.py            # Vimshottari MD/AD/PD + deep birth path
    panchanga.py        # Panchanga + solar events
    calculator.py       # canonical chart assembly + audit
    strengths.py        # next: Ashtakavarga/Shadbala/Bhava Bala
    kp.py               # later: star/sub/sub-sub + significators
    jaimini.py          # later
    arudha.py           # later
    upagraha.py         # later
  knowledge/            # future source/rule retrieval
  llm/                  # future tool calling + synthesis
  validation.py         # compatibility/reference validation
  models.py             # stable shared contracts
  api.py                # FastAPI
streamlit_app.py        # development visualizer
```

## Recommended next milestones

1. Ashtakavarga with independent fixtures.
2. Shadbala and Bhava Bala.
3. KP deterministic engine: cusps, star lord, sub lord, sub-sub lord and significators.
4. Jaimini, Arudha and Upagraha modules with explicit methodology identifiers.
5. Only after deterministic/audit layers stabilize: document ingestion/RAG and LLM tool calling.
