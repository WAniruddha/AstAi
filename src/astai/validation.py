from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, time
import json
from pathlib import Path
from typing import Any

from astai.engine import calculate_chart
from astai.models import BirthData, ChartResponse


def angular_diff_degrees(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


@dataclass(frozen=True)
class ValidationCheck:
    field: str
    passed: bool
    expected: Any
    actual: Any
    delta: float | None = None
    tolerance: float | None = None
    unit: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    vendor: str
    document: str
    passed: bool
    checks: tuple[ValidationCheck, ...]

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


def _clock_seconds(value: datetime, hhmmss: str) -> float:
    hh, mm, ss = (int(part) for part in hhmmss.split(':'))
    expected = value.replace(hour=hh, minute=mm, second=ss, microsecond=0)
    return abs((value - expected).total_seconds())


def compare_chart_to_fixture(chart: ChartResponse, fixture: dict[str, Any]) -> ValidationReport:
    tolerance = float(fixture.get('cross_vendor_tolerance_degrees', 0.05))
    checks: list[ValidationCheck] = []
    reference = fixture['reference']

    def exact(field: str, actual: Any, expected: Any) -> None:
        checks.append(ValidationCheck(field, actual == expected, expected, actual))

    def angular(field: str, actual: float, expected: float, tol: float = tolerance) -> None:
        delta = angular_diff_degrees(actual, expected)
        checks.append(ValidationCheck(field, delta <= tol, expected, actual, delta, tol, 'degrees'))

    expected_asc = reference['ascendant']
    angular('ascendant.longitude', chart.ascendant.longitude_sidereal, expected_asc['longitude'])
    exact('ascendant.sign', chart.ascendant.sign, expected_asc['sign'])
    exact('ascendant.nakshatra', chart.ascendant.nakshatra, expected_asc['nakshatra'])
    exact('ascendant.pada', chart.ascendant.pada, expected_asc['pada'])

    by_body = {planet.body: planet for planet in chart.planets}
    for body, expected in reference['planets'].items():
        actual = by_body[body]
        angular(f'{body}.longitude', actual.longitude_sidereal, expected['longitude'])
        exact(f'{body}.sign', actual.sign, expected['sign'])
        exact(f'{body}.nakshatra', actual.nakshatra, expected['nakshatra'])
        exact(f'{body}.pada', actual.pada, expected['pada'])

    panchanga = reference.get('panchanga', {})
    if panchanga:
        exact('panchanga.weekday', chart.panchanga.weekday, panchanga['weekday'])
        exact('panchanga.tithi', chart.panchanga.tithi_name, panchanga['tithi'])
        exact('panchanga.paksha', chart.panchanga.paksha, panchanga['paksha'])
        exact('panchanga.karana', chart.panchanga.karana, panchanga['karana'])
        exact('panchanga.yoga', chart.panchanga.yoga_name, panchanga['yoga'])

        solar_tolerance = float(panchanga.get('solar_event_tolerance_seconds', 60.0))
        if 'sunrise' in panchanga and chart.panchanga.sunrise_local is not None:
            delta = _clock_seconds(chart.panchanga.sunrise_local, panchanga['sunrise'])
            checks.append(ValidationCheck('panchanga.sunrise', delta <= solar_tolerance, panchanga['sunrise'], chart.panchanga.sunrise_local.strftime('%H:%M:%S'), delta, solar_tolerance, 'seconds'))
        if 'sunset' in panchanga and chart.panchanga.sunset_local is not None:
            delta = _clock_seconds(chart.panchanga.sunset_local, panchanga['sunset'])
            checks.append(ValidationCheck('panchanga.sunset', delta <= solar_tolerance, panchanga['sunset'], chart.panchanga.sunset_local.strftime('%H:%M:%S'), delta, solar_tolerance, 'seconds'))

    expected_balance = reference.get('dasha_balance')
    if expected_balance:
        balance = chart.vimshottari.balance_at_birth
        exact('dasha.lord', balance.lord, expected_balance['lord'])
        exact('dasha.years', balance.years, expected_balance['years'])
        exact('dasha.months', balance.months, expected_balance['months'])
        day_tolerance = int(expected_balance.get('day_tolerance', 0))
        delta_days = abs(balance.days - expected_balance['days'])
        checks.append(ValidationCheck('dasha.days', delta_days <= day_tolerance, expected_balance['days'], balance.days, float(delta_days), float(day_tolerance), 'days'))

    ayanamsa = reference.get('ayanamsa')
    if ayanamsa:
        tol_arcsec = float(ayanamsa.get('tolerance_arcseconds', 5.0))
        delta_arcsec = abs(chart.metadata.ayanamsa_degrees - ayanamsa['degrees']) * 3600.0
        checks.append(ValidationCheck('ayanamsa', delta_arcsec <= tol_arcsec, ayanamsa['degrees'], chart.metadata.ayanamsa_degrees, delta_arcsec, tol_arcsec, 'arcseconds'))

    provenance = fixture.get('provenance', {})
    return ValidationReport(
        vendor=provenance.get('vendor', 'unknown'),
        document=provenance.get('document', 'unknown'),
        passed=all(check.passed for check in checks),
        checks=tuple(checks),
    )


def birth_data_from_fixture(fixture: dict[str, Any]) -> BirthData:
    raw = fixture['birth_data']
    yyyy, mm, dd = (int(part) for part in raw['date'].split('-'))
    hh, mi, ss = (int(part) for part in raw['time'].split(':'))
    return BirthData(
        name=f"{fixture.get('provenance', {}).get('vendor', 'reference')} fixture",
        place_name=raw.get('place'),
        date_of_birth=date(yyyy, mm, dd),
        time_of_birth=time(hh, mi, ss),
        latitude=raw['latitude'],
        longitude=raw['longitude'],
        timezone=raw['timezone'],
        node_model=raw.get('node_model', 'Mean').lower(),
        ephemeris_policy='allow_moshier',
    )


def validate_fixture(path: str | Path) -> ValidationReport:
    fixture = json.loads(Path(path).read_text())
    chart = calculate_chart(birth_data_from_fixture(fixture))
    return compare_chart_to_fixture(chart, fixture)
