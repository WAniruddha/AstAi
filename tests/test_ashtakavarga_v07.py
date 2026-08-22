from __future__ import annotations

import json
from datetime import date, time
from pathlib import Path

from astai.engine import calculate_chart
from astai.engine.ashtakavarga import CLASSICAL_PLANETS
from astai.engine.ashtakavarga_reductions import (
    DEFAULT_PINDA_PROFILE,
    LEGACY_PINDA_PROFILE,
    apply_ekadhipatya_shodhana,
    apply_trikona_shodhana,
    calculate_pinda,
)
from astai.models import BirthData

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "astropdf_ashtakavarga_reductions_2015.json"


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_astropdf_2015_matches_trikona_stage_exactly() -> None:
    fixture = _fixture()["reference"]
    for planet in CLASSICAL_PLANETS:
        assert list(apply_trikona_shodhana(fixture["raw_bav"][planet])) == fixture[
            "after_trikona"
        ][planet]


def test_common_ekadhipatya_rule_cases() -> None:
    def row(aries: int, scorpio: int) -> list[int]:
        values = [0] * 12
        values[0] = aries
        values[7] = scorpio
        return values

    assert apply_ekadhipatya_shodhana(row(0, 4), set()) == tuple(row(0, 4))
    assert apply_ekadhipatya_shodhana(row(3, 5), set()) == tuple(row(3, 3))
    assert apply_ekadhipatya_shodhana(row(3, 3), set()) == tuple(row(0, 0))
    assert apply_ekadhipatya_shodhana(row(3, 5), {0, 7}) == tuple(row(3, 5))
    assert apply_ekadhipatya_shodhana(row(2, 5), {0}) == tuple(row(2, 3))
    assert apply_ekadhipatya_shodhana(row(5, 2), {0}) == tuple(row(5, 0))
    assert apply_ekadhipatya_shodhana(row(2, 2), {0}) == tuple(row(2, 0))


def test_astropdf_pinda_arithmetic_matches_explicit_legacy_profile() -> None:
    data = _fixture()
    planet_signs = data["classical_planet_sign_indexes_0_based"]
    reference = data["reference"]

    for planet in CLASSICAL_PLANETS:
        result = calculate_pinda(
            planet,
            reference["published_after_ekadhipatya"][planet],
            planet_signs,
            profile=LEGACY_PINDA_PROFILE,
        )
        expected = reference["published_pinda"][planet]
        assert result.rasi_pinda == expected["rasi"]
        assert result.graha_pinda == expected["graha"]
        assert result.shodhya_pinda == expected["shodhya"]


def test_pinda_profiles_are_explicit_about_virgo_multiplier() -> None:
    data = _fixture()
    planet_signs = data["classical_planet_sign_indexes_0_based"]
    mercury_vendor_row = data["reference"]["published_after_ekadhipatya"]["Mercury"]

    standard = calculate_pinda(
        "Mercury", mercury_vendor_row, planet_signs, profile=DEFAULT_PINDA_PROFILE
    )
    legacy = calculate_pinda(
        "Mercury", mercury_vendor_row, planet_signs, profile=LEGACY_PINDA_PROFILE
    )

    assert standard.rasi_pinda - legacy.rasi_pinda == 3
    assert standard.graha_pinda == legacy.graha_pinda


def test_chart_preserves_raw_ashtakavarga_and_exposes_reduction_layers() -> None:
    chart = calculate_chart(
        BirthData(
            name="Delhi reference",
            place_name="Delhi, India",
            date_of_birth=date(1979, 8, 23),
            time_of_birth=time(23, 53, 18),
            latitude=28.6666666667,
            longitude=77.2166666667,
            timezone="Asia/Kolkata",
            node_model="mean",
            ephemeris_policy="allow_moshier",
        )
    )

    assert chart.ashtakavarga.sarva_total == 337
    assert chart.ashtakavarga.reduction_status == "unreduced"
    reductions = chart.ashtakavarga.reductions
    assert reductions is not None
    assert reductions.methodology == "bphs_common_v1"
    assert reductions.standard_pinda_profile == DEFAULT_PINDA_PROFILE
    assert [profile.profile for profile in reductions.pinda_profiles] == [
        DEFAULT_PINDA_PROFILE,
        LEGACY_PINDA_PROFILE,
    ]

    raw_by_planet = {row.planet: row for row in chart.ashtakavarga.bhinna}
    for reduced in reductions.bhinna:
        assert reduced.raw_points_by_sign == raw_by_planet[reduced.planet].points_by_sign
        assert all(
            after <= before
            for before, after in zip(
                reduced.raw_points_by_sign,
                reduced.trikona_points_by_sign,
                strict=True,
            )
        )
        assert all(
            after <= before
            for before, after in zip(
                reduced.trikona_points_by_sign,
                reduced.ekadhipatya_points_by_sign,
                strict=True,
            )
        )

    for profile in reductions.pinda_profiles:
        for result in profile.results:
            assert result.shodhya_pinda == result.rasi_pinda + result.graha_pinda

    audit = next(item for item in chart.audit if item.code == "ASHTAKAVARGA_REDUCTIONS")
    assert audit.status == "METHODOLOGY_DEPENDENT"
