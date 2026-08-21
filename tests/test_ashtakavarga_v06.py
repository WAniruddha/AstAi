from __future__ import annotations

import json
from datetime import date, time
from pathlib import Path

from astai.engine import calculate_chart
from astai.engine.ashtakavarga import (
    CLASSICAL_PLANETS,
    CONTRIBUTORS,
    EXPECTED_BAV_TOTALS,
    calculate_raw_ashtakavarga,
)
from astai.models import BirthData

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "astrosage_ashtakavarga_1979.json"


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _calculate_fixture_raw():
    data = _fixture()
    source = data["source_sign_indexes_0_based"]
    planets = {planet: source[planet] for planet in CLASSICAL_PLANETS}
    return calculate_raw_ashtakavarga(source["Ascendant"], planets)


def _decode_prastara(encoded: str) -> list[int]:
    assert len(encoded) == 12
    assert set(encoded) <= {"0", "1"}
    return [int(value) for value in encoded]


def _rotate(values: list[int] | tuple[int, ...], amount: int) -> list[int]:
    amount %= len(values)
    if amount == 0:
        return list(values)
    return list(values[-amount:]) + list(values[:-amount])


def test_delhi_1979_matches_full_astrosage_raw_ashtakavarga() -> None:
    fixture = _fixture()
    reference = fixture["reference"]
    result = _calculate_fixture_raw()

    assert list(result.sign_order) == fixture["methodology"]["sign_order"]
    assert result.methodology == fixture["methodology"]["name"]
    assert result.reduction_status == "unreduced"

    for bav in result.bhinna:
        expected = reference["bhinna"][bav.planet]
        assert list(bav.points_by_sign) == expected["points_by_sign"]
        assert bav.total == expected["total"]

        actual_rows = {row.contributor: list(row.points_by_sign) for row in bav.prastara}
        assert list(actual_rows) == list(CONTRIBUTORS)
        for contributor in CONTRIBUTORS:
            assert actual_rows[contributor] == _decode_prastara(
                expected["prastara"][contributor]
            )

    assert list(result.sarva_points_by_sign) == reference["sarvashtakavarga"]["points_by_sign"]
    assert result.sarva_total == reference["sarvashtakavarga"]["total"] == 337


def test_raw_ashtakavarga_invariants() -> None:
    result = _calculate_fixture_raw()

    assert len(result.bhinna) == 7
    assert len(result.sarva_points_by_sign) == 12
    assert result.sarva_total == 337

    for bav in result.bhinna:
        assert bav.total == EXPECTED_BAV_TOTALS[bav.planet]
        assert sum(bav.points_by_sign) == bav.total
        assert len(bav.prastara) == 8
        assert [row.contributor for row in bav.prastara] == list(CONTRIBUTORS)
        for row in bav.prastara:
            assert len(row.points_by_sign) == 12
            assert set(row.points_by_sign) <= {0, 1}
            assert sum(row.points_by_sign) == row.total
        reconstructed = [
            sum(row.points_by_sign[index] for row in bav.prastara)
            for index in range(12)
        ]
        assert reconstructed == list(bav.points_by_sign)

    reconstructed_sav = [
        sum(bav.points_by_sign[index] for bav in result.bhinna)
        for index in range(12)
    ]
    assert reconstructed_sav == list(result.sarva_points_by_sign)


def test_raw_ashtakavarga_is_zodiac_rotation_invariant() -> None:
    fixture = _fixture()
    source = fixture["source_sign_indexes_0_based"]
    baseline = _calculate_fixture_raw()
    shift = 5

    rotated_planets = {
        planet: (source[planet] + shift) % 12 for planet in CLASSICAL_PLANETS
    }
    rotated = calculate_raw_ashtakavarga(
        (source["Ascendant"] + shift) % 12,
        rotated_planets,
    )

    for original, shifted in zip(baseline.bhinna, rotated.bhinna, strict=True):
        assert shifted.planet == original.planet
        assert list(shifted.points_by_sign) == _rotate(original.points_by_sign, shift)
        for original_row, shifted_row in zip(original.prastara, shifted.prastara, strict=True):
            assert shifted_row.contributor == original_row.contributor
            assert list(shifted_row.points_by_sign) == _rotate(
                original_row.points_by_sign, shift
            )

    assert list(rotated.sarva_points_by_sign) == _rotate(
        baseline.sarva_points_by_sign, shift
    )


def test_chart_response_contains_typed_raw_ashtakavarga() -> None:
    data = BirthData(
        name="AstroSage Brihat 1979 reference",
        place_name="Delhi, India",
        date_of_birth=date(1979, 8, 23),
        time_of_birth=time(23, 53, 18),
        latitude=28.6666666667,
        longitude=77.2166666667,
        timezone="Asia/Kolkata",
        node_model="mean",
        ephemeris_policy="allow_moshier",
    )
    chart = calculate_chart(data)

    assert chart.ashtakavarga.methodology == "classical_raw_ashtakavarga_v1"
    assert chart.ashtakavarga.reduction_status == "unreduced"
    assert chart.ashtakavarga.sarva_points_by_sign == [
        30, 36, 40, 22, 20, 23, 28, 25, 28, 24, 27, 34
    ]
    assert chart.ashtakavarga.sarva_total == 337
    sun = next(bav for bav in chart.ashtakavarga.bhinna if bav.planet == "Sun")
    assert sun.points_by_sign == [5, 5, 5, 3, 3, 4, 2, 4, 3, 3, 5, 6]
    assert any(item.code == "ASHTAKAVARGA_RAW" for item in chart.audit)
