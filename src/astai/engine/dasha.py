from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from astai.engine.constants import NAKSHATRA_SPAN, VIMSHOTTARI_LORDS, VIMSHOTTARI_YEARS
from astai.models import DashaBalance, DashaPeriod, PlanetPosition, VimshottariDasha

TOTAL_VIMSHOTTARI_YEARS = 120.0
_LEVELS = ("MD", "AD", "PD", "SD", "PRANA")


@dataclass(frozen=True)
class _FullPeriod:
    level: str
    lord: str
    start: datetime
    end: datetime
    parent_path: tuple[str, ...] = ()


def _moon(planets: list[PlanetPosition]) -> PlanetPosition:
    return next(p for p in planets if p.body == "Moon")


def _balance_components(remaining_years: float) -> tuple[int, int, int]:
    total_days = remaining_years * 360.0
    years = int(total_days // 360.0)
    total_days -= years * 360.0
    months = int(total_days // 30.0)
    days = int(round(total_days - months * 30.0))
    if days == 30:
        days = 0
        months += 1
    if months == 12:
        months = 0
        years += 1
    return years, months, days


def _sequence_from(start_lord: str) -> list[str]:
    idx = VIMSHOTTARI_LORDS.index(start_lord)
    return [VIMSHOTTARI_LORDS[(idx + i) % 9] for i in range(9)]


def _child_periods(parent: _FullPeriod, level: str) -> list[_FullPeriod]:
    total_seconds = (parent.end - parent.start).total_seconds()
    start = parent.start
    children: list[_FullPeriod] = []
    sequence = _sequence_from(parent.lord)
    parent_path = parent.parent_path + (parent.lord,)

    for index, lord in enumerate(sequence):
        if index == 8:
            end = parent.end
        else:
            seconds = total_seconds * VIMSHOTTARI_YEARS[lord] / TOTAL_VIMSHOTTARI_YEARS
            end = start + timedelta(seconds=seconds)
        children.append(
            _FullPeriod(
                level=level,
                lord=lord,
                start=start,
                end=end,
                parent_path=parent_path,
            )
        )
        start = end

    return children


def _full_mahadashas(
    birth_dt: datetime,
    lord: str,
    elapsed_fraction: float,
    lord_years: float,
    year_days: float,
) -> list[_FullPeriod]:
    theoretical_start = birth_dt - timedelta(days=elapsed_fraction * lord_years * year_days)
    coverage_end = birth_dt + timedelta(days=TOTAL_VIMSHOTTARI_YEARS * year_days)

    periods: list[_FullPeriod] = []
    current = theoretical_start
    lord_index = VIMSHOTTARI_LORDS.index(lord)

    index = 0
    while current < coverage_end:
        current_lord = VIMSHOTTARI_LORDS[(lord_index + index) % 9]
        end = current + timedelta(days=VIMSHOTTARI_YEARS[current_lord] * year_days)
        periods.append(_FullPeriod(level="MD", lord=current_lord, start=current, end=end))
        current = end
        index += 1

    return periods


def _visible_period(period: _FullPeriod, birth_dt: datetime) -> DashaPeriod:
    return DashaPeriod(
        level=period.level,
        lord=period.lord,
        start=max(period.start, birth_dt),
        end=period.end,
        parent_lord=period.parent_path[-1] if period.parent_path else None,
        parent_path=list(period.parent_path),
        theoretical_start=period.start,
        partial_at_birth=(period.start < birth_dt < period.end),
    )


def _exact_period(period: _FullPeriod, birth_dt: datetime) -> DashaPeriod:
    return DashaPeriod(
        level=period.level,
        lord=period.lord,
        start=period.start,
        end=period.end,
        parent_lord=period.parent_path[-1] if period.parent_path else None,
        parent_path=list(period.parent_path),
        theoretical_start=period.start,
        partial_at_birth=(period.start < birth_dt < period.end),
    )


def _contains(period: _FullPeriod, instant: datetime) -> bool:
    return period.start <= instant < period.end


def _timing_path_at(
    instant: datetime,
    full_mds: list[_FullPeriod],
    birth_dt: datetime,
    depth: str = "PRANA",
) -> list[DashaPeriod]:
    if depth not in _LEVELS:
        raise ValueError(f"Unsupported Vimshottari depth: {depth}")

    target_index = _LEVELS.index(depth)
    current = next((period for period in full_mds if _contains(period, instant)), None)
    if current is None:
        return []

    path = [_exact_period(current, birth_dt)]
    for level in _LEVELS[1 : target_index + 1]:
        children = _child_periods(current, level)
        current = next((period for period in children if _contains(period, instant)), None)
        if current is None:
            break
        path.append(_exact_period(current, birth_dt))
    return path


def calculate_vimshottari(
    birth_dt: datetime,
    planets: list[PlanetPosition],
    year_days: float = 365.25,
) -> VimshottariDasha:
    moon = _moon(planets)
    lord = moon.nakshatra_lord
    lord_years = VIMSHOTTARI_YEARS[lord]

    nak_start = moon.nakshatra_index * NAKSHATRA_SPAN
    elapsed_fraction = (moon.longitude_sidereal - nak_start) / NAKSHATRA_SPAN
    elapsed_fraction = max(0.0, min(elapsed_fraction, 1.0))
    remaining_fraction = 1.0 - elapsed_fraction
    remaining_years = remaining_fraction * lord_years
    years, months, days = _balance_components(remaining_years)

    full_mds = _full_mahadashas(
        birth_dt,
        lord,
        elapsed_fraction,
        lord_years,
        year_days,
    )

    full_ads = [child for md in full_mds for child in _child_periods(md, "AD")]
    full_pds = [child for ad in full_ads for child in _child_periods(ad, "PD")]

    coverage_end = birth_dt + timedelta(days=TOTAL_VIMSHOTTARI_YEARS * year_days)
    mahadashas = [
        _visible_period(p, birth_dt)
        for p in full_mds
        if p.end > birth_dt and p.start < coverage_end
    ]
    antardashas = [
        _visible_period(p, birth_dt)
        for p in full_ads
        if p.end > birth_dt and p.start < coverage_end
    ]
    pratyantardashas = [
        _visible_period(p, birth_dt)
        for p in full_pds
        if p.end > birth_dt and p.start < coverage_end
    ]
    birth_path = _timing_path_at(birth_dt, full_mds, birth_dt, depth="PRANA")

    return VimshottariDasha(
        birth_nakshatra=moon.nakshatra,
        birth_nakshatra_lord=lord,
        year_days=year_days,
        balance_at_birth=DashaBalance(
            lord=lord,
            years=years,
            months=months,
            days=days,
            remaining_fraction=remaining_fraction,
        ),
        mahadashas=mahadashas,
        antardashas=antardashas,
        pratyantardashas=pratyantardashas,
        birth_timing_path=birth_path,
        coverage_end=coverage_end,
    )
