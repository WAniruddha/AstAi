from __future__ import annotations

import hashlib
import json

import swisseph as swe

from astai import __version__
from astai.engine.ashtakavarga import calculate_raw_ashtakavarga
from astai.engine.astronomy import calculate_astronomy
from astai.engine.dasha import calculate_vimshottari
from astai.engine.houses import calculate_sripati_bhava
from astai.engine.panchanga import calculate_panchanga
from astai.engine.vargas import calculate_core_vargas, calculate_shodashavarga
from astai.models import (
    Ashtakavarga,
    AshtakavargaContribution,
    AuditItem,
    Bhinnashtakavarga,
    BirthData,
    CalculationMetadata,
    ChartResponse,
)


def _calculation_fingerprint(data: BirthData, backend: str) -> str:
    payload = {
        "input": data.model_dump(mode="json"),
        "engine_version": __version__,
        "swiss_ephemeris_version": swe.version,
        "actual_backend": backend,
        "zodiac": "sidereal",
        "ayanamsa": "Lahiri",
        "parashari_houses": "whole_sign",
        "parashari_bhava": data.bhava_method,
        "secondary_cusps": "placidus",
        "position_model": "apparent_geocentric_ecliptic_of_date",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _ashtakavarga_model(ascendant, planets) -> Ashtakavarga:
    classical_signs = {
        planet.body: planet.sign_index
        for planet in planets
        if planet.body in {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    }
    raw = calculate_raw_ashtakavarga(ascendant.sign_index, classical_signs)
    return Ashtakavarga(
        methodology=raw.methodology,
        sign_order=list(raw.sign_order),
        point_semantics=raw.point_semantics,
        reduction_status=raw.reduction_status,
        bhinna=[
            Bhinnashtakavarga(
                planet=bav.planet,
                points_by_sign=list(bav.points_by_sign),
                total=bav.total,
                prastara=[
                    AshtakavargaContribution(
                        contributor=row.contributor,
                        points_by_sign=list(row.points_by_sign),
                        total=row.total,
                    )
                    for row in bav.prastara
                ],
            )
            for bav in raw.bhinna
        ],
        sarva_points_by_sign=list(raw.sarva_points_by_sign),
        sarva_total=raw.sarva_total,
    )


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
    bhava_chalit = calculate_sripati_bhava(
        astronomy["ascendant"],
        planets,
        astronomy["porphyry_madhyas"],
        astronomy["sripati_boundaries"],
    )
    vimshottari = calculate_vimshottari(
        astronomy["local_dt"], planets, year_days=data.dasha_year_days
    )
    ashtakavarga = _ashtakavarga_model(astronomy["ascendant"], planets)

    audit = [
        AuditItem(
            code="ASTRONOMY_COMPUTED",
            status="COMPUTED",
            message=f"Planetary positions computed through Swiss Ephemeris library using the {backend} backend.",
        ),
        AuditItem(
            code="SIDEREAL_STANDARD",
            status="DERIVED",
            message=(
                "Sidereal positions use Lahiri ayanamsa. Whole Sign, Sripati Bhava/Chalit, "
                "and Placidus cusps are kept as separate house frameworks."
            ),
        ),
        AuditItem(
            code="SRIPATI_BHAVA_CHALIT",
            status="CROSS_VERIFIED",
            message=(
                "Parashari Bhava/Chalit uses sripati_bhava_chalit_v1. Porphyry cusps are "
                "treated as Bhava Madhya and adjacent Madhyas define Sripati Sandhi boundaries. "
                "The independently derived boundaries match Swiss Ephemeris native Sripati "
                f"within {bhava_chalit.swiss_sripati_crosscheck_max_arcseconds:.9g} arcsec."
            ),
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
                "Vimshottari balance, MD/AD/PD periods, and the five-level birth timing path "
                "(through Sookshma and Prana) use the Moon's exact Nakshatra position and "
                f"{data.dasha_year_days} days per dasha year for calendar dates."
            ),
        ),
        AuditItem(
            code="ASHTAKAVARGA_RAW",
            status="REFERENCE_MATCHED",
            message=(
                "Raw classical Ashtakavarga computes the seven planetary Bhinnashtakavargas, "
                "all eight Prastara contributor rows for each planet, and Sarvashtakavarga. "
                "The fixed BAV totals are 48/49/39/54/56/52/39 and the unreduced SAV total is 337; "
                "the Delhi-1979 golden fixture matches the published AstroSage table exactly. "
                "Trikona Shodhana, Ekadhipatya Shodhana and Shodhya Pinda are intentionally not computed yet."
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
            parashari_bhava_system=data.bhava_method,
            varga_profile=data.varga_profile,
        ),
        ascendant=astronomy["ascendant"],
        midheaven=astronomy["midheaven"],
        planets=planets,
        whole_sign_houses=astronomy["whole_sign_houses"],
        bhava_chalit=bhava_chalit,
        placidus_cusps=astronomy["placidus_cusps"],
        panchanga=panchanga,
        vargas=vargas,
        shodashavarga=shodashavarga,
        vimshottari=vimshottari,
        ashtakavarga=ashtakavarga,
        audit=audit,
    )
