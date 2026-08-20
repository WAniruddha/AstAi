from fastapi import FastAPI, HTTPException

from astai.engine import calculate_chart
from astai.engine.astronomy import EphemerisUnavailableError
from astai.models import BirthData, ChartResponse

app = FastAPI(
    title="AstAi Calculator API",
    version="0.2.0",
    description="Deterministic Jyotisha calculation API. Interpretation and LLM layers remain separate.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "astai-calculator", "version": "0.2.0"}


@app.post("/v1/chart/calculate", response_model=ChartResponse)
def chart_calculate(payload: BirthData) -> ChartResponse:
    try:
        return calculate_chart(payload)
    except EphemerisUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Chart calculation failed. No astrological values were guessed.",
        ) from exc
