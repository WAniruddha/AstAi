from __future__ import annotations

import hashlib
import json

import swisseph as swe

from astai import __version__
from astai.engine.ashtakavarga import calculate_raw_ashtakavarga
from astai.engine.ashtakavarga_reductions import calculate_ashtakavarga_reductions
from astai.engine.astronomy import calculate_astronomy
from astai.engine.dasha import calculate_vimshottari
from astai.engine.dig_bala import calculate_dig_bala_all
from astai.engine.houses import calculate_sripati_bhava
from astai.engine.panchanga import calculate_panchanga
from astai.engine.shadbala import calculate_shadbala_foundation
from astai.engine.vargas import calculate_core_vargas, calculate_shodashavarga
from astai.models import (
    Ashtakavarga,
    AshtakavargaContribution,
    AshtakavargaPindaProfile,
    AshtakavargaPindaResult,
    AshtakavargaReductions,
    AuditItem,
    Bhinnashtakavarga,
    BirthData,
    CalculationMetadata,
    ChartResponse,
    ReducedBhinnashtakavarga,
    ShadbalaFoundation,
    ShadbalaPlanetStrength,
)


CLASSICAL_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
SHADBALA_SAPTAVARGA_CODES = ("D1", "D2", "D3", "D7", "D9", "D12", "D30")


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
        if planet.body in CLASSICAL_PLANETS
    }
    raw = calculate_raw_ashtakavarga(ascendant.sign_index, classical_signs)
    reductions = calculate_ashtakavarga_reductions(raw, classical_signs)
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
        reductions=AshtakavargaReductions(
            methodology=reductions.methodology,
            occupancy_semantics=reductions.occupancy_semantics,
            standard_pinda_profile=reductions.standard_pinda_profile,
            bhinna=[
                ReducedBhinnashtakavarga(
                    planet=row.planet,
                    raw_points_by_sign=list(row.raw_points_by_sign),
                    trikona_points_by_sign=list(row.trikona_points_by_sign),
                    ekadhipatya_points_by_sign=list(row.ekadhipatya_points_by_sign),
                )
                for row in reductions.bhinna
            ],
            pinda_profiles=[
                AshtakavargaPindaProfile(
                    profile=profile.profile,
                    rasi_multipliers=list(profile.rasi_multipliers),
                    graha_multipliers=dict(profile.graha_multipliers),
                    results=[
                        AshtakavargaPindaResult(
                            planet=result.planet,
                            rasi_pinda=result.rasi_pinda,
                            graha_pinda=result.graha_pinda,
                            shodhya_pinda=result.shodhya_pinda,
                        )
                        for result in profile.results
                    ],
                )
                for profile in reductions.pinda_profiles
            ],
        ),
    )


def _shadbala_model(
    ascendant,
    planets,
    shodashavarga,
    bhava_chalit,
    source_varga_profile: str,
) -> ShadbalaFoundation:
    classical_by_name = {
        planet.body: planet for planet in planets if planet.body in CLASSICAL_PLANETS
    }
    missing_planets = [planet for planet in CLASSICAL_PLANETS if planet not in classical_by_name]
    if missing_planets:
        raise ValueError("Missing classical planet(s) for Shadbala: " + ", ".join(missing_planets))

    charts_by_code = {chart.varga: chart for chart in shodashavarga}
    missing_vargas = [code for code in SHADBALA_SAPTAVARGA_CODES if code not in charts_by_code]
    if missing_vargas:
        raise ValueError("Missing Shadbala Saptavarga chart(s): " + ", ".join(missing_vargas))

    saptavarga_positions_by_planet: dict[str, dict[str, tuple[int, float]]] = {}
    for planet_name in CLASSICAL_PLANETS:
        positions: dict[str, tuple[int, float]] = {}
        for code in SHADBALA_SAPTAVARGA_CODES:
            placement = next(
                (
                    row
                    for row in charts_by_code[code].placements
                    if row.body == planet_name
                ),
                None,
            )
            if placement is None:
                raise ValueError(f"Missing {planet_name} placement in {code} for Shadbala.")
            positions[code] = (placement.sign_index, placement.varga_degree)
        saptavarga_positions_by_planet[planet_name] = positions

    planet_longitudes = {
        name: classical_by_name[name].longitude_sidereal for name in CLASSICAL_PLANETS
    }
    planet_sign_indexes = {
        name: classical_by_name[name].sign_index for name in CLASSICAL_PLANETS
    }
    planet_sign_degrees = {
        name: classical_by_name[name].sign_degree for name in CLASSICAL_PLANETS
    }
    navamsa_sign_indexes = {
        name: saptavarga_positions_by_planet[name]["D9"][0] for name in CLASSICAL_PLANETS
    }

    result = calculate_shadbala_foundation(
        ascendant_sign_index=ascendant.sign_index,
        planet_longitudes=planet_longitudes,
        planet_sign_indexes=planet_sign_indexes,
        planet_sign_degrees=planet_sign_degrees,
        navamsa_sign_indexes=navamsa_sign_indexes,
        saptavarga_positions_by_planet=saptavarga_positions_by_planet,
    )

    if result.saptavargaja_profile is None or result.saptavargaja_relationship_methodology is None:
        raise RuntimeError("Complete Shadbala foundation unexpectedly returned partial Sthana Bala metadata.")

    bhava_madhyas = {
        house.house: house.madhya_longitude_sidereal
        for house in bhava_chalit.houses
        if house.house in {1, 4, 7, 10}
    }
    dig = calculate_dig_bala_all(planet_longitudes, bhava_madhyas)
    dig_by_planet = {row.planet: row for row in dig.rows}

    rows: list[ShadbalaPlanetStrength] = []
    for row in result.rows:
        if row.saptavargaja_bala_virupas is None or row.sthana_bala_total_virupas is None:
            raise RuntimeError(f"Complete Sthana Bala unexpectedly missing for {row.planet}.")
        dig_row = dig_by_planet[row.planet]
        rows.append(
            ShadbalaPlanetStrength(
                planet=row.planet,
                uccha_bala_virupas=row.uccha_bala_virupas,
                saptavargaja_bala_virupas=row.saptavargaja_bala_virupas,
                ojayugma_bala_virupas=row.ojayugma_bala_virupas,
                kendradi_bala_virupas=row.kendradi_bala_virupas,
                drekkana_bala_virupas=row.drekkana_bala_virupas,
                sthana_bala_total_virupas=row.sthana_bala_total_virupas,
                naisargika_bala_virupas=row.naisargika_bala_virupas,
                dig_bala_virupas=dig_row.dig_bala_virupas,
                dig_bala_weakest_house=dig_row.weakest_house,
                dig_bala_strongest_house=dig_row.strongest_house,
                dig_bala_weakest_point_longitude_sidereal=dig_row.weakest_point_longitude_sidereal,
                dig_bala_angular_distance_degrees=dig_row.angular_distance_degrees,
            )
        )

    return ShadbalaFoundation(
        methodology=result.methodology,
        unit="virupa",
        aggregation_status="complete_sthana_dig_naisargika_other_shadbala_components_pending",
        saptavargaja_profile=result.saptavargaja_profile,
        saptavargaja_relationship_methodology=result.saptavargaja_relationship_methodology,
        source_varga_profile=source_varga_profile,
        dig_bala_methodology=dig.methodology,
        dig_bala_zero_point_source=dig.zero_point_source,
        rows=rows,
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
    shadbala = _shadbala_model(
        astronomy["ascendant"],
        planets,
        shodashavarga,
        bhava_chalit,
        data.varga_profile,
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
                "the Delhi-1979 golden fixture matches the published AstroSage table exactly."
            ),
        ),
        AuditItem(
            code="ASHTAKAVARGA_REDUCTIONS",
            status="METHODOLOGY_DEPENDENT",
            message=(
                "Trikona and Ekadhipatya Shodhana use the declared bphs_common_v1 profile and preserve "
                "the raw v0.6 values unchanged. Ekadhipatya occupancy counts only Sun through Saturn. "
                "Shodhya Pinda is emitted under explicit multiplier profiles because circulated BPHS tables "
                "and working software traditions disagree on some Rasi/Graha multipliers."
            ),
        ),
        AuditItem(
            code="SHADBALA_STHANA",
            status="METHODOLOGY_DEPENDENT",
            message=(
                "v0.8 computes complete Sthana Bala for Sun through Saturn as Uchcha + Saptavargaja + "
                "Ojayugma + Kendradi + Drekkana. Saptavargaja uses the explicit "
                f"{shadbala.saptavargaja_profile} profile with {shadbala.saptavargaja_relationship_methodology}; "
                f"its seven divisional inputs come from the chart's {data.varga_profile} Varga profile."
            ),
        ),
        AuditItem(
            code="SHADBALA_DIG",
            status="METHODOLOGY_DEPENDENT",
            message=(
                f"Dig Bala uses {shadbala.dig_bala_methodology} with zero points from "
                f"{shadbala.dig_bala_zero_point_source}. The 1st/4th/7th/10th sidereal Sripati "
                "Bhava Madhyas are used as directional angular points; whole-sign centers are not substituted."
            ),
        ),
        AuditItem(
            code="SHADBALA_PARTIAL",
            status="NOT_COMPUTED",
            message=(
                "Sthana Bala, Dig Bala and Naisargika Bala are available. Kala, Chesta and Drik Bala, "
                "aggregate Shadbala and required-strength ratios remain intentionally withheld."
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
        shadbala=shadbala,
        audit=audit,
    )
