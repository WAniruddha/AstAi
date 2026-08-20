# AstAi Architecture

## Goal

AstAi is a reusable Jyotisha computation, verification and interpretation platform. The central rule is that deterministic astronomical and astrological calculations are separated from probabilistic language-model interpretation.

## Build order

### Layer 0 — Input and provenance

Birth date, time, coordinates, IANA timezone, ayanamsa, node model and methodology choices are explicit inputs. Every derived value must be traceable to them. Birth-time uncertainty is stored when supplied rather than converted into an invented confidence score.

### Layer 1 — Deterministic calculation core

Swiss Ephemeris supplies the astronomical basis. AstAi derives sidereal zodiac mapping, Nakshatra/Pada, D1 Whole Sign houses, separate sidereal Placidus cusps, the classical Shodashavarga set and Vimshottari Mahadasha/Antardasha.

Later deterministic modules include Bhava/Chalit, deeper Dashas, strengths, KP subdivisions, Jaimini, Arudha and Upagrahas.

This layer is the source of truth for computed chart data.

### Layer 2 — Verification and audit

Golden-reference fixtures compare AstAi results with trusted reference software or independently verified data. Calculation disagreements are surfaced rather than hidden.

Astronomy compatibility and high-varga formula compatibility are tested separately because very small source-longitude differences can cross narrow divisional boundaries.

### Layer 3 — Knowledge layer

Books, rule catalogues and carefully curated PDFs can be indexed for retrieval. They answer questions such as: "Which classical or KP rule applies to this already-calculated placement?"

They do not replace astronomical calculation.

### Layer 4 — LLM orchestration

An LLM receives structured chart data and retrieved rules, then writes explanations, comparisons and synthesis. It may call deterministic AstAi modules as tools. It must never invent missing planetary degrees, cusps, subdivisions or Dasha boundaries.

### Layer 5 — Product interfaces

FastAPI exposes stable machine-readable endpoints. Streamlit is the current development visualizer. A dedicated web/mobile client can replace Streamlit later without changing the calculation core.

## Why not microservices yet?

The first production shape is a modular monolith: one Python codebase with clear internal module boundaries. This is easier to test and change while calculation conventions are still being finalized.

Split a module into a separate service only when there is an observed reason, such as independent scaling, separate security boundaries, different deployment cadence or a measured performance bottleneck.

Redis, an API gateway, a graph database and vector database are possible later additions, not foundation requirements.

## Role of PDFs

There are two useful PDF categories.

### Reference/teaching PDFs

Texts about Parashari, KP, Jaimini, Dashas and related traditions are candidates for a future RAG knowledge base. Each extracted rule should preserve source, edition/page or section, school, conditions, exceptions and methodology notes.

### Generated birth-chart PDFs

A trusted astrology-software PDF can be useful as a validation fixture or imported external chart record. It should be labelled `IMPORTED` or `REFERENCE`, not silently treated as a computed AstAi result.

A PDF is not a substitute for the calculation engine because it is a presentation of someone else's calculations. Parsing it can reproduce those displayed values, but it does not make the underlying method independently auditable.

## Current module map

```text
src/astai/
  engine/
    astronomy.py        # implemented: ephemeris, time normalization, Lagna, cusps
    vargas.py           # implemented: full classical Shodashavarga + named compatibility profile
    dasha.py            # implemented: Vimshottari MD/AD; deeper levels next
    panchanga.py        # implemented core Panchanga + solar events
    calculator.py       # canonical chart assembly + audit metadata
    houses.py           # next: explicit Bhava/Chalit convention
    strengths.py        # later: Shadbala/Bhava Bala/Ashtakavarga
    kp.py               # later: star/sub/sub-sub and significators
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

1. Add Vimshottari Pratyantar and deeper timing levels with boundary tests.
2. Freeze and implement the Parashari Bhava/Chalit convention separately from KP Placidus cusps.
3. Add Ashtakavarga and then Shadbala/Bhava Bala with independent fixtures.
4. Build the KP deterministic engine: cusps, star lord, sub lord, sub-sub lord and significators.
5. Add Jaimini, Arudha and Upagraha modules with explicit methodology identifiers.
6. Only after the deterministic and audit layers are stable, add document ingestion/RAG and LLM tool calling.
