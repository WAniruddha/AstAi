from __future__ import annotations

import hashlib
import json

import swisseph as swe

from astai import __version__
from astai.engine.astronomy import calculate_astronomy
from astai.engine.dasha import calculate_vimshottari
from astai.engine.panchanga import calculate_panchanga
from astai.engine.vargas import calculate_core_vargas, calculate_shodashavarga
from astai.models import AuditItem, BirthData, CalculationMetadata, ChartResponse


def _calculation_fingerprint(data: BirthData, backend: str) -> str:
    payload = {
        "input": data.model_dump(mode="json"),
        "engine_version": __version__,
        "swiss_ephemeris_version": swe.version,
        "actual_backend": backend,
        "zodiac": "sidereal",
        "ayanamsa": "Lahiri",
        "parashari_houses": "whole_sign",
        "secondary_cusps": "placidus",
        "position_model": "apparent_geocentric_ecliptic_of_date",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def calculate_chart(data: BirthData) -> ChartResponse:
    astronomy = calculate_astronomy(data)
    planets = astronomy["planets"]
    backend = astronomy["actual_backend"]

    panchanga = calculate_panchanga(
        astronomy["local_dt"],
        planets,
        astronomy["sunrise_local"],
        astronomy["sunset_local"],
    )
    vargas = calculate_core_vargas(
        astronomy["ascendant"], planets, profile=data.varga_profile
    )
    shodashavarga = calculate_shodashavarga(
        astronomy["ascendant"], planets, profile=data.varga_profile
    )
    vimshottari = calculate_vimshottari(
        astronomy["local_dt"], planets, year_days=data.dasha_year_days
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
            code="SHODASHAVARGA",
            status="DERIVED",
            message=(
                "All 16 classical Shodashavarga charts are derived from exact sidereal longitudes using "
                f"the {data.varga_profile} profile."
            ),
        ),
        AuditItem(
            code="VIMSHOTTARI",
            status="DERIVED",
            message=(
                "Vimshottari balance and MD/AD periods use the Moon's exact Nakshatra position and "
                f"{data.dasha_year_days} days per dasha year for timeline dates."
            ),
        ),
    ]

    if data.varga_profile == "astrosage_reference_compat_v1":
        audit.append(
            AuditItem(
                code="VARGA_COMPATIBILITY_PROFILE",
                status="WARNING",
                message=(
                    "AstroSage reference compatibility is enabled. D7 uses an empirically observed degree-truncation "
                    "rule from two public AstroSage reports; this is not the default exact Parashari method."
                ),
            )
        )

    uncertainty = data.birth_time_uncertainty_seconds
    if uncertainty is None:
        d60_message = (
            "D60 uses 0.5° source segments and is highly birth-time-sensitive, especially for the Ascendant. "
            "No birth-time uncertainty was supplied."
        )
    else:
        d60_message = (
            "D60 uses 0.5° source segments and is highly birth-time-sensitive, especially for the Ascendant. "
            f"Declared birth-time uncertainty: ±{uncertainty:g} seconds."
        )
    audit.append(AuditItem(code="D60_TIME_SENSITIVITY", status="WARNING", message=d60_message))

    if astronomy["sunrise_local"] is None:
        audit.append(
            AuditItem(
                code="SUNRISE_UNAVAILABLE",
                status="WARNING",
                message="No sunrise was found for the local civil date (possible polar condition); Panchanga weekday falls back to civil weekday.",
            )
        )
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
            calculation_fingerprint=_calculation_fingerprint(data, backend),
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
            varga_profile=data.varga_profile,
        ),
        ascendant=astronomy["ascendant"],
        midheaven=astronomy["midheaven"],
        planets=planets,
        whole_sign_houses=astronomy["whole_sign_houses"],
        placidus_cusps=astronomy["placidus_cusps"],
        panchanga=panchanga,
        vargas=vargas,
        shodashavarga=shodashavarga,
        vimshottari=vimshottari,
        audit=audit,
    )
