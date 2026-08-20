from __future__ import annotations

from datetime import datetime

from astai.engine.constants import MOVABLE_KARANAS, TITHI_NAMES, YOGA_NAMES
from astai.models import Panchanga, PlanetPosition


def _planet(planets: list[PlanetPosition], name: str) -> PlanetPosition:
    return next(p for p in planets if p.body == name)


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


def calculate_panchanga(local_dt: datetime, planets: list[PlanetPosition]) -> Panchanga:
    sun = _planet(planets, "Sun")
    moon = _planet(planets, "Moon")
    elongation = (moon.longitude_sidereal - sun.longitude_sidereal) % 360.0
    tithi_index = min(int(elongation // 12.0), 29)
    paksha = "Shukla" if tithi_index < 15 else "Krishna"
    tithi_name = "Amavasya" if tithi_index == 29 else TITHI_NAMES[tithi_index % 15]

    half_tithi_index = min(int(elongation // 6.0), 59)
    yoga_index = min(
        int(((sun.longitude_sidereal + moon.longitude_sidereal) % 360.0) // (360.0 / 27.0)),
        26,
    )

    return Panchanga(
        weekday=local_dt.strftime("%A"),
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
