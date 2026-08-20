from datetime import date, time
import json
from pathlib import Path

from fastapi.testclient import TestClient

from astai.api import app
from astai.engine import calculate_chart
from astai.engine.astronomy import EphemerisUnavailableError, zodiac_point
from astai.models import BirthData

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "astrosage_public_1979.json"


def load_reference() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def astro_sage_fixture() -> BirthData:
    data = load_reference()["birth_data"]
    hh, mm, ss = map(int, data["time"].split(":"))
    yyyy, mo, dd = map(int, data["date"].split("-"))
    return BirthData(
        name="AstroSage public sample",
        place_name=data["place"],
        date_of_birth=date(yyyy, mo, dd),
        time_of_birth=time(hh, mm, ss),
        latitude=data["latitude"],
        longitude=data["longitude"],
        timezone=data["timezone"],
        ephemeris_policy="allow_moshier",
    )


def angular_diff(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def test_zodiac_boundaries() -> None:
    assert zodiac_point(0.0).nakshatra == "Ashwini"
    assert zodiac_point(13 + 20 / 60).nakshatra == "Bharani"
    assert zodiac_point(359.999999).sign == "Pisces"


def test_astrosage_public_reference_chart_matches_categories_and_degrees() -> None:
    reference = load_reference()
    chart = calculate_chart(astro_sage_fixture())
    tolerance = reference["cross_vendor_tolerance_degrees"]

    by_name = {p.body: p for p in chart.planets}
    for name, expected in reference["reference"]["planets"].items():
        actual = by_name[name]
        assert actual.sign == expected["sign"]
        assert actual.nakshatra == expected["nakshatra"]
        assert actual.pada == expected["pada"]
        assert angular_diff(actual.longitude_sidereal, expected["longitude"]) <= tolerance

    expected_asc = reference["reference"]["ascendant"]
    assert chart.ascendant.sign == expected_asc["sign"]
    assert chart.ascendant.nakshatra == expected_asc["nakshatra"]
    assert chart.ascendant.pada == expected_asc["pada"]
    assert angular_diff(chart.ascendant.longitude_sidereal, expected_asc["longitude"]) <= tolerance

    panchanga = reference["reference"]["panchanga"]
    assert chart.panchanga.weekday == panchanga["weekday"]
    assert chart.panchanga.tithi_name == panchanga["tithi"]
    assert chart.panchanga.paksha == panchanga["paksha"]
    assert chart.panchanga.yoga_name == panchanga["yoga"]
    assert chart.panchanga.karana == panchanga["karana"]

    balance = chart.vimshottari.balance_at_birth
    expected_balance = reference["reference"]["dasha_balance"]
    assert (balance.lord, balance.years, balance.months, balance.days) == (
        expected_balance["lord"],
        expected_balance["years"],
        expected_balance["months"],
        expected_balance["days"],
    )


def test_d1_d9_d10_are_present_and_complete() -> None:
    chart = calculate_chart(astro_sage_fixture())
    assert [v.varga for v in chart.vargas] == ["D1", "D9", "D10"]
    assert all(len(v.placements) == len(chart.planets) for v in chart.vargas)


def test_navamsa_and_dasamsa_reference_rules() -> None:
    from astai.engine.vargas import _varga_sign_and_degree

    assert _varga_sign_and_degree(0.0, 9, "D9")[0] == 0
    assert _varga_sign_and_degree(30.0, 9, "D9")[0] == 9
    assert _varga_sign_and_degree(60.0, 9, "D9")[0] == 6
    assert _varga_sign_and_degree(0.0, 10, "D10")[0] == 0
    assert _varga_sign_and_degree(30.0, 10, "D10")[0] == 9


def test_mean_node_opposition_is_exact() -> None:
    chart = calculate_chart(astro_sage_fixture())
    by_name = {p.body: p for p in chart.planets}
    assert angular_diff((by_name["Rahu"].longitude_sidereal + 180) % 360, by_name["Ketu"].longitude_sidereal) < 1e-10


def test_strict_swiss_rejects_silent_moshier_fallback_when_files_absent(monkeypatch) -> None:
    monkeypatch.delenv("ASTAI_EPHE_PATH", raising=False)
    data = astro_sage_fixture().model_copy(update={"ephemeris_policy": "strict_swiss"})
    try:
        chart = calculate_chart(data)
    except EphemerisUnavailableError:
        return
    assert chart.metadata.actual_ephemeris_backend in {"swiss", "jpl"}


def test_api_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "0.4.0"


def test_dst_ambiguous_time_requires_explicit_fold() -> None:
    data = BirthData(
        date_of_birth=date(2024, 11, 3),
        time_of_birth=time(1, 30),
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York",
        ephemeris_policy="allow_moshier",
    )
    try:
        calculate_chart(data)
    except ValueError as exc:
        assert "DST-ambiguous" in str(exc)
    else:
        raise AssertionError("Ambiguous historical civil time must not be guessed")


def test_dst_gap_is_rejected() -> None:
    data = BirthData(
        date_of_birth=date(2024, 3, 10),
        time_of_birth=time(2, 30),
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York",
        ephemeris_policy="allow_moshier",
    )
    try:
        calculate_chart(data)
    except ValueError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("Nonexistent historical civil time must not be guessed")


def test_vimshottari_periods_are_ordered_and_non_overlapping() -> None:
    chart = calculate_chart(astro_sage_fixture())
    periods = chart.vimshottari.mahadashas
    assert periods
    for current, nxt in zip(periods, periods[1:]):
        assert current.end == nxt.start
        assert current.start < current.end
