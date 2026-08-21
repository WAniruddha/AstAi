from __future__ import annotations

from datetime import date, time
import json
from pathlib import Path

import pytest

from astai.engine import calculate_chart
from astai.models import BirthData

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "astrosage_saswad_2000.json"


def _load_reference() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _angular_diff_arcseconds(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0) * 3600.0


def _birth_data(reference: dict, **updates) -> BirthData:
    """Build a chart input for geocentric planetary compatibility checks.

    The legacy AstroSage screenshot does not establish an unambiguous decimal
    coordinate convention. The literal numeric interpretation below is used
    only to satisfy the BirthData contract; the tests in this file do not use
    the Ascendant as a numerical pass/fail target.
    """

    birth = reference["birth_data"]
    yyyy, mm, dd = map(int, birth["date"].split("-"))
    hh, minute, ss = map(int, birth["time"].split(":"))
    values = {
        "name": reference["reference_name"],
        "place_name": birth["place"],
        "date_of_birth": date(yyyy, mm, dd),
        "time_of_birth": time(hh, minute, ss),
        "latitude": 18.32,
        "longitude": 74.0,
        "timezone": birth["timezone"],
        "node_model": birth["node_model"],
        "include_outer_planets": True,
        "ephemeris_policy": "allow_moshier",
    }
    values.update(updates)
    return BirthData(**values)


@pytest.fixture(scope="module")
def reference() -> dict:
    return _load_reference()


@pytest.fixture(scope="module")
def chart(reference: dict):
    return calculate_chart(_birth_data(reference))


def test_saswad_2000_planet_categories_match_supplied_astrosage_reference(
    reference: dict,
    chart,
) -> None:
    by_name = {planet.body: planet for planet in chart.planets}
    for body, expected in reference["reference"]["planets"].items():
        actual = by_name[body]
        assert actual.sign == expected["sign"]
        assert actual.nakshatra == expected["nakshatra"]
        assert actual.pada == expected["pada"]
        if "retrograde" in expected:
            assert actual.retrograde is expected["retrograde"]


def test_saswad_2000_planet_longitudes_are_tracked_by_domain_tolerance(
    reference: dict,
    chart,
) -> None:
    tolerance = reference["tolerances_arcseconds"]
    by_name = {planet.body: planet for planet in chart.planets}
    classical = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    nodes = {"Rahu", "Ketu"}
    outer = {"Uranus", "Neptune", "Pluto"}

    for body, expected in reference["reference"]["planets"].items():
        if body in classical:
            allowed = tolerance["classical_planets"]
        elif body in nodes:
            allowed = tolerance["nodes"]
        elif body in outer:
            allowed = tolerance["outer_planets"]
        else:
            raise AssertionError(f"Unclassified reference body: {body}")

        assert (
            _angular_diff_arcseconds(
                by_name[body].longitude_sidereal,
                expected["longitude"],
            )
            <= allowed
        )


def test_saswad_ascendant_is_transcribed_but_not_coordinate_verified(reference: dict) -> None:
    expected = reference["reference"]["ascendant"]
    assert expected["sign"] == "Scorpio"
    assert expected["vendor_dms"] == "21-01-23"
    assert expected["validation_status"] == "TRANSCRIBED_NOT_COORDINATE_VERIFIED"
    assert reference["birth_data"]["coordinate_status"] == "ambiguous_legacy_vendor_notation"


def test_mean_and_true_rahu_are_materially_different_for_saswad_reference(
    reference: dict,
    chart,
) -> None:
    true_chart = calculate_chart(_birth_data(reference, node_model="true"))
    mean_rahu = next(p for p in chart.planets if p.body == "Rahu")
    true_rahu = next(p for p in true_chart.planets if p.body == "Rahu")

    assert mean_rahu.sign == "Gemini"
    assert true_rahu.sign == "Cancer"
    assert _angular_diff_arcseconds(
        mean_rahu.longitude_sidereal,
        true_rahu.longitude_sidereal,
    ) > 3600.0
