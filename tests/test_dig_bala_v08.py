from __future__ import annotations

import pytest

from astai.engine.dig_bala import (
    CLASSICAL_PLANETS,
    DIG_BALA_METHODOLOGY,
    DIG_BALA_ZERO_POINT_SOURCE,
    STRONG_DIRECTION_HOUSES,
    WEAK_DIRECTION_HOUSES,
    calculate_dig_bala,
    calculate_dig_bala_all,
)


@pytest.mark.parametrize("planet", CLASSICAL_PLANETS)
def test_dig_bala_is_zero_at_planet_specific_weak_point(planet):
    assert calculate_dig_bala(planet, 123.456, 123.456) == pytest.approx(0.0)


@pytest.mark.parametrize("planet", CLASSICAL_PLANETS)
def test_dig_bala_is_sixty_exactly_opposite_weak_point(planet):
    assert calculate_dig_bala(planet, 303.456, 123.456) == pytest.approx(60.0)


def test_dig_bala_midpoint_is_thirty_on_either_side():
    assert calculate_dig_bala("Sun", 100.0, 10.0) == pytest.approx(30.0)
    assert calculate_dig_bala("Sun", 280.0, 10.0) == pytest.approx(30.0)


def test_dig_bala_wraps_cleanly_across_zero_degrees():
    assert calculate_dig_bala("Moon", 10.0, 350.0) == pytest.approx(20.0 / 3.0)


def test_bphs_directional_house_mapping_is_frozen():
    assert WEAK_DIRECTION_HOUSES == {
        "Sun": 4,
        "Mars": 4,
        "Jupiter": 7,
        "Mercury": 7,
        "Moon": 10,
        "Venus": 10,
        "Saturn": 1,
    }
    assert STRONG_DIRECTION_HOUSES == {
        "Sun": 10,
        "Mars": 10,
        "Jupiter": 1,
        "Mercury": 1,
        "Moon": 4,
        "Venus": 4,
        "Saturn": 7,
    }


def test_known_moon_worked_example_matches_64_degrees_divided_by_three():
    # Published working example: Moon 3 Taurus = 33°, meridian = 97°.
    assert calculate_dig_bala("Moon", 33.0, 97.0) == pytest.approx(64.0 / 3.0)


def test_all_planets_use_their_declared_weak_bhava_madhyas():
    madhyas = {1: 15.0, 4: 105.0, 7: 195.0, 10: 285.0}
    planets = {
        "Sun": 105.0,
        "Moon": 285.0,
        "Mars": 105.0,
        "Mercury": 195.0,
        "Jupiter": 195.0,
        "Venus": 285.0,
        "Saturn": 15.0,
    }
    result = calculate_dig_bala_all(planets, madhyas)

    assert result.methodology == DIG_BALA_METHODOLOGY
    assert result.zero_point_source == DIG_BALA_ZERO_POINT_SOURCE
    assert result.unit == "virupa"
    assert [row.planet for row in result.rows] == list(CLASSICAL_PLANETS)
    assert all(row.dig_bala_virupas == pytest.approx(0.0) for row in result.rows)


def test_all_planets_reach_sixty_at_opposite_directional_angle():
    madhyas = {1: 15.0, 4: 105.0, 7: 195.0, 10: 285.0}
    planets = {
        "Sun": 285.0,
        "Moon": 105.0,
        "Mars": 285.0,
        "Mercury": 15.0,
        "Jupiter": 15.0,
        "Venus": 105.0,
        "Saturn": 195.0,
    }
    result = calculate_dig_bala_all(planets, madhyas)
    assert all(row.dig_bala_virupas == pytest.approx(60.0) for row in result.rows)


def test_all_planets_require_all_four_angular_bhava_madhyas():
    planets = {planet: 0.0 for planet in CLASSICAL_PLANETS}
    with pytest.raises(ValueError, match="10"):
        calculate_dig_bala_all(planets, {1: 0.0, 4: 90.0, 7: 180.0})


@pytest.mark.parametrize("planet", ["Rahu", "Ketu", "Uranus", "Neptune", "Pluto"])
def test_non_classical_bodies_are_rejected(planet):
    with pytest.raises(ValueError):
        calculate_dig_bala(planet, 0.0, 0.0)
