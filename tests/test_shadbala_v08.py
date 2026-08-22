from __future__ import annotations

import pytest

from astai.engine.saptavargaja import SAPTAVARGA_CODES, calculate_saptavargaja_bala
from astai.engine.shadbala import (
    ASTAI_STANDARD_SAPTAVARGAJA_PROFILE,
    CLASSICAL_PLANETS,
    calculate_drekkana_bala,
    calculate_kendradi_bala,
    calculate_naisargika_bala,
    calculate_ojayugma_bala,
    calculate_shadbala_foundation,
    calculate_uccha_bala,
)


@pytest.mark.parametrize(
    ("planet", "debilitation", "exaltation"),
    [
        ("Sun", 190.0, 10.0),
        ("Moon", 213.0, 33.0),
        ("Mars", 118.0, 298.0),
        ("Mercury", 345.0, 165.0),
        ("Jupiter", 275.0, 95.0),
        ("Venus", 177.0, 357.0),
        ("Saturn", 20.0, 200.0),
    ],
)
def test_uccha_bala_exact_extremes(planet, debilitation, exaltation):
    assert calculate_uccha_bala(planet, debilitation) == pytest.approx(0.0)
    assert calculate_uccha_bala(planet, exaltation) == pytest.approx(60.0)


def test_uccha_bala_midpoint_is_30_virupas():
    assert calculate_uccha_bala("Sun", 100.0) == pytest.approx(30.0)


@pytest.mark.parametrize("house", [1, 4, 7, 10])
def test_kendradi_kendra_is_60(house):
    assert calculate_kendradi_bala(house) == 60.0


@pytest.mark.parametrize("house", [2, 5, 8, 11])
def test_kendradi_panaphara_is_30(house):
    assert calculate_kendradi_bala(house) == 30.0


@pytest.mark.parametrize("house", [3, 6, 9, 12])
def test_kendradi_apoklima_is_15(house):
    assert calculate_kendradi_bala(house) == 15.0


def test_ojayugma_uses_rasi_and_navamsa_parity():
    # Moon/Venus prefer even signs; the other five prefer odd signs.
    assert calculate_ojayugma_bala("Moon", 1, 3) == 30.0
    assert calculate_ojayugma_bala("Venus", 1, 2) == 15.0
    assert calculate_ojayugma_bala("Sun", 0, 2) == 30.0
    assert calculate_ojayugma_bala("Saturn", 1, 3) == 0.0


def test_drekkana_bala_matches_bphs_gender_order():
    # BPHS 27.6: male -> 1st, hermaphrodite -> 2nd, female -> 3rd.
    assert calculate_drekkana_bala("Sun", 5.0) == 15.0
    assert calculate_drekkana_bala("Mars", 15.0) == 0.0
    assert calculate_drekkana_bala("Mercury", 15.0) == 15.0
    assert calculate_drekkana_bala("Saturn", 25.0) == 0.0
    assert calculate_drekkana_bala("Moon", 25.0) == 15.0
    assert calculate_drekkana_bala("Venus", 5.0) == 0.0


def test_naisargika_bala_is_fixed_60_over_7_sequence():
    expected_factors = {
        "Saturn": 1,
        "Mars": 2,
        "Mercury": 3,
        "Jupiter": 4,
        "Venus": 5,
        "Moon": 6,
        "Sun": 7,
    }
    for planet, factor in expected_factors.items():
        assert calculate_naisargika_bala(planet) == pytest.approx(60.0 * factor / 7.0)


def _foundation_inputs():
    planet_longitudes = {
        "Sun": 10.0,
        "Moon": 33.0,
        "Mars": 298.0,
        "Mercury": 165.0,
        "Jupiter": 95.0,
        "Venus": 357.0,
        "Saturn": 200.0,
    }
    planet_sign_indexes = {
        planet: int(longitude // 30.0)
        for planet, longitude in planet_longitudes.items()
    }
    planet_sign_degrees = {
        planet: longitude % 30.0
        for planet, longitude in planet_longitudes.items()
    }
    navamsa_sign_indexes = {
        "Sun": 0,
        "Moon": 1,
        "Mars": 0,
        "Mercury": 5,
        "Jupiter": 3,
        "Venus": 11,
        "Saturn": 6,
    }
    return (
        planet_longitudes,
        planet_sign_indexes,
        planet_sign_degrees,
        navamsa_sign_indexes,
    )


def _synthetic_saptavarga_positions(planet_sign_indexes, planet_sign_degrees):
    return {
        planet: {
            code: (planet_sign_indexes[planet], planet_sign_degrees[planet])
            for code in SAPTAVARGA_CODES
        }
        for planet in CLASSICAL_PLANETS
    }


def test_foundation_is_seven_classical_planets_only_and_refuses_fake_total():
    (
        planet_longitudes,
        planet_sign_indexes,
        planet_sign_degrees,
        navamsa_sign_indexes,
    ) = _foundation_inputs()

    result = calculate_shadbala_foundation(
        ascendant_sign_index=0,
        planet_longitudes=planet_longitudes,
        planet_sign_indexes=planet_sign_indexes,
        planet_sign_degrees=planet_sign_degrees,
        navamsa_sign_indexes=navamsa_sign_indexes,
    )

    assert [row.planet for row in result.rows] == list(CLASSICAL_PLANETS)
    assert "saptavargaja_pending" in result.aggregation_status
    assert result.saptavargaja_profile is None
    for row in result.rows:
        assert row.saptavargaja_bala_virupas is None
        assert row.sthana_bala_total_virupas is None
        assert row.sthana_known_subtotal_virupas == pytest.approx(
            row.uccha_bala_virupas
            + row.ojayugma_bala_virupas
            + row.kendradi_bala_virupas
            + row.drekkana_bala_virupas
        )


def test_complete_sthana_uses_astai_standard_saptavargaja_and_excludes_naisargika():
    (
        planet_longitudes,
        planet_sign_indexes,
        planet_sign_degrees,
        navamsa_sign_indexes,
    ) = _foundation_inputs()
    positions_by_planet = _synthetic_saptavarga_positions(
        planet_sign_indexes, planet_sign_degrees
    )

    result = calculate_shadbala_foundation(
        ascendant_sign_index=0,
        planet_longitudes=planet_longitudes,
        planet_sign_indexes=planet_sign_indexes,
        planet_sign_degrees=planet_sign_degrees,
        navamsa_sign_indexes=navamsa_sign_indexes,
        saptavarga_positions_by_planet=positions_by_planet,
    )

    assert result.aggregation_status == (
        "complete_sthana_bala_other_shadbala_components_pending"
    )
    assert result.saptavargaja_profile == ASTAI_STANDARD_SAPTAVARGAJA_PROFILE

    for row in result.rows:
        direct = calculate_saptavargaja_bala(
            row.planet,
            positions_by_planet[row.planet],
            planet_sign_indexes,
            ASTAI_STANDARD_SAPTAVARGAJA_PROFILE,
        )
        assert row.saptavargaja_bala_virupas == pytest.approx(direct.total_virupas)
        assert row.sthana_bala_total_virupas == pytest.approx(
            row.sthana_known_subtotal_virupas + row.saptavargaja_bala_virupas
        )
        assert row.sthana_bala_total_virupas != pytest.approx(
            row.sthana_known_subtotal_virupas
            + row.saptavargaja_bala_virupas
            + row.naisargika_bala_virupas
        )


def test_complete_sthana_allows_explicit_modern_profile_override():
    (
        planet_longitudes,
        planet_sign_indexes,
        planet_sign_degrees,
        navamsa_sign_indexes,
    ) = _foundation_inputs()
    positions_by_planet = _synthetic_saptavarga_positions(
        planet_sign_indexes, planet_sign_degrees
    )

    standard = calculate_shadbala_foundation(
        0,
        planet_longitudes,
        planet_sign_indexes,
        planet_sign_degrees,
        navamsa_sign_indexes,
        positions_by_planet,
    )
    modern = calculate_shadbala_foundation(
        0,
        planet_longitudes,
        planet_sign_indexes,
        planet_sign_degrees,
        navamsa_sign_indexes,
        positions_by_planet,
        saptavargaja_profile="modern_panchadha_d1_mt_v1",
    )

    assert modern.saptavargaja_profile == "modern_panchadha_d1_mt_v1"
    assert any(
        standard_row.sthana_bala_total_virupas
        != pytest.approx(modern_row.sthana_bala_total_virupas)
        for standard_row, modern_row in zip(standard.rows, modern.rows)
    )


def test_complete_sthana_requires_all_seven_planet_saptavarga_rows():
    (
        planet_longitudes,
        planet_sign_indexes,
        planet_sign_degrees,
        navamsa_sign_indexes,
    ) = _foundation_inputs()
    positions_by_planet = _synthetic_saptavarga_positions(
        planet_sign_indexes, planet_sign_degrees
    )
    positions_by_planet.pop("Saturn")

    with pytest.raises(ValueError, match="Saturn"):
        calculate_shadbala_foundation(
            0,
            planet_longitudes,
            planet_sign_indexes,
            planet_sign_degrees,
            navamsa_sign_indexes,
            positions_by_planet,
        )


@pytest.mark.parametrize("planet", ["Rahu", "Ketu", "Uranus", "Neptune", "Pluto"])
def test_non_classical_bodies_are_rejected(planet):
    with pytest.raises(ValueError):
        calculate_naisargika_bala(planet)
