from __future__ import annotations

from datetime import datetime, timedelta

from astai.engine.constants import NAKSHATRA_SPAN, VIMSHOTTARI_LORDS, VIMSHOTTARI_YEARS
from astai.models import DashaBalance, DashaPeriod, PlanetPosition, VimshottariDasha

TOTAL_VIMSHOTTARI_YEARS = 120.0


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

    theoretical_md_start = birth_dt - timedelta(days=elapsed_fraction * lord_years * year_days)
    sequence = _sequence_from(lord)

    mahadashas: list[DashaPeriod] = []
    antardashas: list[DashaPeriod] = []
    md_start = theoretical_md_start

    for md_lord in sequence:
        md_days = VIMSHOTTARI_YEARS[md_lord] * year_days
        md_end = md_start + timedelta(days=md_days)

        if md_end > birth_dt:
            mahadashas.append(
                DashaPeriod(
                    level="MD",
                    lord=md_lord,
                    start=max(md_start, birth_dt),
                    end=md_end,
                    partial_at_birth=(md_start < birth_dt < md_end),
                )
            )

            ad_start = md_start
            for ad_lord in _sequence_from(md_lord):
                ad_days = md_days * VIMSHOTTARI_YEARS[ad_lord] / TOTAL_VIMSHOTTARI_YEARS
                ad_end = ad_start + timedelta(days=ad_days)
                if ad_end > birth_dt:
                    antardashas.append(
                        DashaPeriod(
                            level="AD",
                            lord=ad_lord,
                            parent_lord=md_lord,
                            start=max(ad_start, birth_dt),
                            end=ad_end,
                            partial_at_birth=(ad_start < birth_dt < ad_end),
                        )
                    )
                ad_start = ad_end

        md_start = md_end

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
    )
