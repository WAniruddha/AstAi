from datetime import date, time
import json
from pathlib import Path
import swisseph as swe

from astai.engine import calculate_chart
from astai.engine.astronomy import _dms, zodiac_point
from astai.models import BirthData
from astai.validation import validate_fixture

FIXTURES = Path(__file__).parent / 'fixtures'

def _chart(**overrides):
    base = dict(date_of_birth=date(1979,4,11), time_of_birth=time(18,23,24), latitude=27.15, longitude=78.0, timezone='Asia/Kolkata', ephemeris_policy='allow_moshier')
    base.update(overrides)
    return calculate_chart(BirthData(**base))

def test_two_independent_astrosage_golden_reports_pass():
    for name in ('astrosage_public_1979.json','astrosage_brihat_1979.json'):
        report = validate_fixture(FIXTURES / name)
        failed = [check for check in report.checks if not check.passed]
        assert report.passed, failed

def test_lahiri_ayanamsa_matches_official_swiss_ephemeris_j2000_anchor():
    # Swiss Ephemeris documentation gives 23°51′25.5324″ at JD 2451545.0 TT.
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    expected = 23 + 51/60 + 25.5324/3600
    assert abs(swe.get_ayanamsa(2451545.0) - expected) < 1e-6

def test_tropical_minus_sidereal_equals_recorded_ayanamsa():
    chart = _chart()
    for planet in chart.planets:
        if planet.ephemeris_backend == 'analytic':
            continue
        expected_sidereal = (planet.longitude_tropical - chart.metadata.ayanamsa_degrees) % 360.0
        delta = abs((planet.longitude_sidereal - expected_sidereal + 180) % 360 - 180)
        assert delta < 1e-9

def test_dms_never_rolls_to_30_degrees_inside_sign():
    dms = _dms(29.99999999999)
    assert (dms.degrees, dms.minutes) == (29, 59)
    assert dms.seconds <= 59.99

def test_hindu_weekday_uses_sunrise_boundary():
    chart = _chart(time_of_birth=time(2,0,0))
    assert chart.panchanga.civil_weekday == 'Wednesday'
    assert chart.panchanga.weekday == 'Tuesday'
    assert chart.panchanga.birth_before_sunrise is True

def test_calculation_fingerprint_is_reproducible_and_input_sensitive():
    a = _chart()
    b = _chart()
    c = _chart(time_of_birth=time(18,23,25))
    assert a.metadata.calculation_fingerprint == b.metadata.calculation_fingerprint
    assert a.metadata.calculation_fingerprint != c.metadata.calculation_fingerprint

def test_all_sign_nakshatra_pada_boundaries_are_valid():
    eps = 1e-10
    for k in range(108):
        boundary = k * (360.0 / 108.0)
        for longitude in ((boundary - eps) % 360.0, boundary % 360.0, (boundary + eps) % 360.0):
            point = zodiac_point(longitude)
            assert 0 <= point.sign_index < 12
            assert 0 <= point.nakshatra_index < 27
            assert 1 <= point.pada <= 4
