from __future__ import annotations

import swisseph as swe

from astai.engine.astronomy import calculate_astronomy
from astai.engine.dasha import calculate_vimshottari
from astai.engine.panchanga import calculate_panchanga
from astai.engine.vargas import calculate_core_vargas
from astai.models import AuditItem, BirthData, CalculationMetadata, ChartResponse


def calculate_chart(data: BirthData) -> ChartResponse:
    astronomy = calculate_astronomy(data)
    planets = astronomy["planets"]
    backend = astronomy["actual_backend"]

    panchanga = calculate_panchanga(astronomy["local_dt"], planets)
    vargas = calculate_core_vargas(astronomy["ascendant"], planets)
    vimshottari = calculate_vimshottari(
        astronomy["local_dt"],
        planets,
        year_days=data.dasha_year_days,
    )

    audit = [
        AuditItem(
            code="ASTRONOMY_COMPUTED",
            status="COMPUTED",
            message=f"Planetary positions computed through Swiss Ephemeris library using the {backend} backend.",
        ),
        AuditItem(
            code="SIDEREAL_STANDARD",
            status="DERIVED",
            message="Sidereal positions use Lahiri ayanamsa; whole-sign houses are kept separate from Placidus cusps.",
        ),
        AuditItem(
            code="CORE_VARGAS",
            status="DERIVED",
            message="D1, D9 and D10 are deterministic mathematical derivations from sidereal longitudes.",
        ),
        AuditItem(
            code="VIMSHOTTARI",
            status="DERIVED",
            message=f"Vimshottari balance and MD/AD periods use the Moon's exact nakshatra position and {data.dasha_year_days} days per dasha year for timeline dates.",
        ),
    ]
    if backend == "moshier":
        audit.append(
            AuditItem(
                code="EPHEMERIS_FALLBACK",
                status="WARNING",
                message="Moshier fallback is active. Strict production mode should use verified Swiss/JPL ephemeris files.",
            )
        )

    local_dt = astronomy["local_dt"]
    offset = local_dt.utcoffset()
    return ChartResponse(
        input=data,
        metadata=CalculationMetadata(
            julian_day_ut=astronomy["jd_ut"],
            utc_datetime=astronomy["utc_dt"].isoformat(),
            local_datetime=local_dt.isoformat(),
            utc_offset_seconds=int(offset.total_seconds()) if offset else 0,
            ayanamsa="Lahiri",
            ayanamsa_degrees=astronomy["ayanamsa_degrees"],
            node_model="Mean Rahu/Ketu" if data.node_model == "mean" else "True Rahu/Ketu",
            ephemeris_library_version=swe.version,
            actual_ephemeris_backend=backend,
            ephemeris_policy=data.ephemeris_policy,
        ),
        ascendant=astronomy["ascendant"],
        midheaven=astronomy["midheaven"],
        planets=planets,
        whole_sign_houses=astronomy["whole_sign_houses"],
        placidus_cusps=astronomy["placidus_cusps"],
        panchanga=panchanga,
        vargas=vargas,
        vimshottari=vimshottari,
        audit=audit,
    )
