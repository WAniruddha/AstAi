from astai.engine.constants import SIGNS
from astai.engine.vargas import SHODASHAVARGA_SPECS, calculate_shodashavarga, varga_amsa
from astai.models import AngularPoint, DMS, PlanetPosition


def _dms_value(value: float) -> DMS:
    degrees = int(value)
    minutes_float = (value - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60
    return DMS(degrees=degrees, minutes=minutes, seconds=seconds, text="")


def _zodiac_fields(longitude: float) -> dict:
    longitude %= 360
    sign_index = int(longitude // 30)
    degree = longitude % 30
    return {
        "longitude_sidereal": longitude,
        "sign_index": sign_index,
        "sign": SIGNS[sign_index],
        "sign_degree": degree,
        "dms": _dms_value(degree),
        "nakshatra_index": 0,
        "nakshatra": "Ashwini",
        "pada": 1,
        "nakshatra_lord": "Ketu",
    }


def _asc(longitude: float) -> AngularPoint:
    return AngularPoint(**_zodiac_fields(longitude), label="Ascendant")


def _planet(body: str, longitude: float) -> PlanetPosition:
    return PlanetPosition(
        **_zodiac_fields(longitude),
        body=body,
        body_id=0,
        longitude_tropical=longitude,
        latitude_ecliptic=0,
        distance_au=1,
        speed_longitude=0,
        retrograde=False,
        classical=True,
        ephemeris_backend="moshier",
    )


def _full(sign_1_based: int, degrees: int, minutes: int, seconds: int) -> float:
    return (sign_1_based - 1) * 30 + degrees + minutes / 60 + seconds / 3600


DELHI_1979 = {
    "LA": _full(2, 15, 14, 32),
    "Sun": _full(5, 6, 27, 41),
    "Moon": _full(5, 17, 48, 46),
    "Mars": _full(3, 16, 23, 41),
    "Mercury": _full(4, 18, 55, 5),
    "Jupiter": _full(4, 28, 42, 40),
    "Venus": _full(5, 5, 59, 4),
    "Saturn": _full(5, 21, 28, 48),
    "Rahu": _full(5, 15, 13, 8),
    "Ketu": _full(11, 15, 13, 8),
}

ASTROSAGE_1979 = {
    "D1": [2, 5, 5, 3, 4, 4, 5, 5, 5, 11],
    "D2": [5, 5, 4, 4, 5, 5, 5, 4, 4, 4],
    "D3": [6, 5, 9, 7, 8, 12, 5, 1, 9, 3],
    "D4": [8, 5, 11, 9, 10, 1, 5, 11, 11, 5],
    "D7": [11, 6, 8, 6, 2, 4, 6, 9, 8, 2],
    "D9": [2, 2, 6, 11, 9, 12, 2, 7, 5, 11],
    "D10": [3, 7, 10, 8, 6, 9, 6, 12, 10, 4],
    "D12": [8, 7, 12, 9, 11, 3, 7, 1, 11, 5],
    "D16": [1, 8, 2, 5, 11, 4, 8, 4, 1, 1],
    "D20": [7, 1, 8, 3, 1, 8, 12, 11, 7, 7],
    "D24": [4, 10, 7, 6, 7, 2, 9, 10, 5, 5],
    "D27": [5, 6, 5, 9, 3, 11, 6, 8, 2, 8],
    "D30": [12, 11, 9, 9, 12, 8, 11, 3, 9, 9],
    "D40": [3, 9, 12, 10, 8, 9, 8, 5, 9, 9],
    "D45": [3, 2, 7, 9, 5, 8, 1, 1, 3, 3],
    "D60": [8, 5, 4, 11, 5, 1, 4, 11, 11, 5],
}

DELHI_1978 = {
    "LA": _full(2, 15, 30, 14),
    "Sun": _full(5, 6, 42, 30),
    "Moon": _full(1, 16, 23, 10),
    "Mars": _full(6, 18, 40, 48),
    "Mercury": _full(4, 28, 16, 43),
    "Jupiter": _full(4, 3, 54, 40),
    "Venus": _full(6, 22, 40, 42),
    "Saturn": _full(5, 9, 57, 57),
    "Rahu": _full(6, 4, 33, 40),
    "Ketu": _full(12, 4, 33, 40),
}

ASTROSAGE_1978 = {
    "D1": [2, 5, 1, 6, 4, 4, 6, 5, 6, 12],
    "D2": [5, 5, 4, 5, 5, 4, 5, 5, 4, 4],
    "D3": [6, 5, 5, 10, 12, 4, 2, 5, 6, 12],
    "D4": [8, 5, 7, 12, 1, 4, 3, 8, 6, 12],
    "D7": [11, 6, 4, 4, 4, 10, 5, 7, 12, 6],
    "D9": [2, 3, 5, 3, 12, 5, 4, 3, 11, 5],
    "D10": [3, 7, 6, 8, 9, 1, 9, 8, 3, 9],
    "D12": [8, 7, 7, 1, 3, 5, 3, 8, 7, 1],
    "D16": [1, 8, 9, 6, 4, 3, 9, 10, 11, 11],
    "D20": [7, 1, 11, 5, 7, 3, 8, 3, 8, 8],
    "D24": [4, 10, 6, 6, 2, 7, 10, 12, 7, 7],
    "D27": [5, 7, 3, 8, 11, 1, 12, 9, 8, 2],
    "D30": [12, 11, 9, 12, 8, 2, 10, 11, 2, 2],
    "D40": [3, 9, 10, 7, 8, 12, 1, 2, 1, 1],
    "D45": [4, 3, 1, 1, 7, 6, 7, 7, 3, 3],
    "D60": [9, 6, 9, 7, 12, 11, 3, 12, 3, 9],
}


def _signs_for(sample: dict[str, float], code: str, profile: str) -> list[int]:
    keys = list(sample)
    return [varga_amsa(sample[key], code, profile).sign_index + 1 for key in keys]


def test_classical_shodashavarga_set_is_exact():
    assert [spec.code for spec in SHODASHAVARGA_SPECS] == [
        "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
        "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60",
    ]


def test_parashara_traditional_matches_astrosage_1979_except_documented_d7_quirk():
    for code, expected in ASTROSAGE_1979.items():
        actual = _signs_for(DELHI_1979, code, "parashara_traditional")
        if code == "D7":
            assert actual == [11, 6, 9, 6, 2, 4, 6, 10, 8, 2]
            assert expected == [11, 6, 8, 6, 2, 4, 6, 9, 8, 2]
        else:
            assert actual == expected, (code, actual, expected)


def test_astrosage_reference_compat_profile_reproduces_all_1979_rows():
    for code, expected in ASTROSAGE_1979.items():
        assert _signs_for(DELHI_1979, code, "astrosage_reference_compat_v1") == expected


def test_astrosage_reference_compat_profile_reproduces_all_1978_rows():
    for code, expected in ASTROSAGE_1978.items():
        assert _signs_for(DELHI_1978, code, "astrosage_reference_compat_v1") == expected


def test_d7_compatibility_difference_is_explicit_not_global():
    # Public 1978 sample: Rahu at Virgo 04°33′40″ is second exact D7 amsa,
    # but the AstroSage reference table behaves as if the integer degree 4°
    # selected the first amsa.
    longitude = DELHI_1978["Rahu"]
    traditional = varga_amsa(longitude, "D7", "parashara_traditional")
    compatibility = varga_amsa(longitude, "D7", "astrosage_reference_compat_v1")
    assert traditional.amsa_index == 2
    assert compatibility.amsa_index == 1
    assert traditional.sign_index + 1 == 1
    assert compatibility.sign_index + 1 == 12

    # The compatibility profile must not alter any other varga.
    for code in ASTROSAGE_1978:
        if code == "D7":
            continue
        assert varga_amsa(longitude, code, "parashara_traditional").sign_index == varga_amsa(
            longitude, code, "astrosage_reference_compat_v1"
        ).sign_index


def test_d30_uses_unequal_classical_segments():
    assert varga_amsa(4.999, "D30").sign_index + 1 == 1
    assert varga_amsa(5.0, "D30").sign_index + 1 == 11
    assert varga_amsa(17.999, "D30").sign_index + 1 == 9
    assert varga_amsa(18.0, "D30").sign_index + 1 == 3
    # Taurus/even sign starts with Taurus then Virgo.
    assert varga_amsa(30 + 4.999, "D30").sign_index + 1 == 2
    assert varga_amsa(30 + 5.0, "D30").sign_index + 1 == 6


def test_builds_complete_16_chart_database_with_sensitivity_metadata():
    asc = _asc(DELHI_1979["LA"])
    planets = [_planet(body, longitude) for body, longitude in list(DELHI_1979.items())[1:]]
    charts = calculate_shodashavarga(asc, planets)
    assert len(charts) == 16
    assert [chart.varga for chart in charts] == [spec.code for spec in SHODASHAVARGA_SPECS]
    assert all(len(chart.placements) == len(planets) for chart in charts)
    d60 = next(chart for chart in charts if chart.varga == "D60")
    assert d60.sensitivity_note is not None
    assert d60.division == 60
    assert d60.methodology == "parashara_traditional_v1"


def test_every_amsa_records_boundary_distance_and_valid_degree():
    for code in (spec.code for spec in SHODASHAVARGA_SPECS):
        result = varga_amsa(137.8127777778, code)
        assert 1 <= result.amsa_index <= int(code[1:])
        assert 0 <= result.varga_degree < 30
        assert result.boundary_distance_arcminutes >= 0


def test_small_source_longitude_delta_can_flip_high_varga_without_formula_error():
    # AstroSage's printed 1978 Mars is 18°40′48″ Virgo. A source longitude only
    # ~98 arcseconds lower lies on the other side of a D45 boundary. This is why
    # astronomy agreement and varga-formula agreement are validated separately.
    published = 150 + 18 + 40 / 60 + 48 / 3600
    nearby = 168.6526702025
    assert abs(published - nearby) < 0.05
    assert varga_amsa(published, "D45").sign_index + 1 == 1
    assert varga_amsa(nearby, "D45").sign_index + 1 == 12


def test_chart_response_keeps_core_vargas_and_adds_full_shodashavarga():
    from datetime import date, time
    from astai.engine import calculate_chart
    from astai.models import BirthData

    chart = calculate_chart(BirthData(
        date_of_birth=date(1979, 8, 23),
        time_of_birth=time(23, 53, 18),
        latitude=28.6666666667,
        longitude=77.2166666667,
        timezone="Asia/Kolkata",
        ephemeris_policy="allow_moshier",
    ))
    assert [v.varga for v in chart.vargas] == ["D1", "D9", "D10"]
    assert [v.varga for v in chart.shodashavarga] == [spec.code for spec in SHODASHAVARGA_SPECS]


def test_third_astrosage_astronomy_fixture_and_two_varga_tables_pass():
    from pathlib import Path
    from astai.validation import validate_fixture, validate_varga_fixture

    fixtures = Path(__file__).parent / "fixtures"
    astronomy = validate_fixture(fixtures / "astrosage_brihat_1978.json")
    assert astronomy.passed, [check for check in astronomy.checks if not check.passed]
    for name in ("astrosage_brihat_1979.json", "astrosage_brihat_1978.json"):
        report = validate_varga_fixture(fixtures / name)
        assert report.passed, [check for check in report.checks if not check.passed]
