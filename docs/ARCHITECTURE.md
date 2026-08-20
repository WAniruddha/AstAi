# AstAi Architecture

## Goal

AstAi is a reusable Jyotisha computation, verification and interpretation platform. The central rule is that deterministic astronomical and astrological calculations are separated from probabilistic language-model interpretation.

## Build order

### Layer 0 — Input and provenance

Birth date, time, coordinates, IANA timezone, ayanamsa, node model and methodology choices are explicit immutable inputs. Every derived value must be traceable to these inputs.

### Layer 1 — Deterministic calculation core

Swiss Ephemeris supplies astronomical positions. AstAi code derives the sidereal zodiac mapping, Nakshatra/Pada, houses and later divisional charts, Dashas, KP subdivisions, Jaimini, Arudha, strengths and other algorithmic systems.

This layer is the source of truth for computed chart data.

### Layer 2 — Verification and audit

Golden-reference fixtures compare AstAi results with trusted reference software or independently verified data. Calculation disagreements are surfaced rather than hidden.

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

## Near-term module map

```text
src/astai/
  engine/
    astronomy.py        # implemented foundation
    houses.py           # next
    vargas.py           # later
    dasha.py            # later
    kp.py               # later
    jaimini.py          # later
    arudha.py           # later
    upagraha.py         # later
  knowledge/            # future source/rule retrieval
  llm/                  # future tool calling + synthesis
  audit/                # golden fixtures + consistency checks
  models.py             # stable shared contracts
  api.py                # FastAPI
streamlit_app.py        # development visualizer
```

## Recommended next milestones

1. Add golden astronomical fixtures and exact-degree comparison tolerances.
2. Make house-framework conventions explicit and separate Whole Sign, Bhava Chalit and KP cusps.
3. Add D9 and D10 as the first divisional engine tests.
4. Add Vimshottari Dasha with exact birth balance and date-boundary tests.
5. Add KP star/sub/sub-sub subdivision engine and Placidus cusps.
6. Add Jaimini and Arudha deterministic modules.
7. Only after those layers are stable, add document ingestion/RAG and LLM tool calling.
