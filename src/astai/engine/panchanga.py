from __future__ import annotations

from datetime import datetime, timedelta

from astai.engine.constants import MOVABLE_KARANAS, TITHI_NAMES, YOGA_NAMES
from astai.models import Panchanga, PlanetPosition


def _planet(planets: list[PlanetPosition], name: str) -> PlanetPosition:
    return next(planet for planet in planets if planet.body == name)


def _karana_name(half_tithi_index: int) -> str:
    if half_tithi_index == 0:
        return "Kimstughna"
    if 1 <= half_tithi_index <= 56:
        return MOVABLE_KARANAS[(half_tithi_index - 1) % 7]
    if half_tithi_index == 57:
        return "Shakuni"
    if half_tithi_index == 58:
        return "Chatushpada"
    return "Naga"


def calculate_panchanga(
    local_dt: datetime,
    planets: list[PlanetPosition],
    sunrise_local: datetime | None,
    sunset_local: datetime | None,
) -> Panchanga:
    sun = _planet(planets, "Sun")
    moon = _planet(planets, "Moon")

    elongation = (moon.longitude_sidereal - sun.longitude_sidereal) % 360.0
    tithi_index = min(int(elongation // 12.0), 29)
    paksha = "Shukla" if tithi_index < 15 else "Krishna"
    tithi_name = (
        "Amavasya"
        if tithi_index == 29
        else TITHI_NAMES[tithi_index % 15]
    )

    half_tithi_index = min(int(elongation // 6.0), 59)
    yoga_index = min(
        int(
            ((sun.longitude_sidereal + moon.longitude_sidereal) % 360.0)
            // (360.0 / 27.0)
        ),
        26,
    )

    civil_weekday = local_dt.strftime("%A")
    birth_before_sunrise: bool | None = None
    hindu_weekday = civil_weekday

    if sunrise_local is not None:
        birth_before_sunrise = local_dt < sunrise_local
        if birth_before_sunrise:
            hindu_weekday = (local_dt - timedelta(days=1)).strftime("%A")

    day_duration_seconds: float | None = None
    if (
        sunrise_local is not None
        and sunset_local is not None
        and sunset_local > sunrise_local
    ):
        day_duration_seconds = (sunset_local - sunrise_local).total_seconds()

    return Panchanga(
        weekday=hindu_weekday,
        civil_weekday=civil_weekday,
        sunrise_local=sunrise_local,
        sunset_local=sunset_local,
        day_duration_seconds=day_duration_seconds,
        birth_before_sunrise=birth_before_sunrise,
        tithi_number=tithi_index + 1,
        tithi_name=tithi_name,
        paksha=paksha,
        karana=_karana_name(half_tithi_index),
        yoga_number=yoga_index + 1,
        yoga_name=YOGA_NAMES[yoga_index],
        moon_rashi=moon.sign,
        moon_nakshatra=moon.nakshatra,
        moon_pada=moon.pada,
    )
