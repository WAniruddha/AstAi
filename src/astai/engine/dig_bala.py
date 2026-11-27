from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

CLASSICAL_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

# BPHS 27.7: Dig Bala is measured from each planet's directionally weakest
# angular point. The opposite angle is therefore the point of full strength.
WEAK_DIRECTION_HOUSES = {
    "Sun": 4,
    "Mars": 4,
    "Jupiter": 7,
    "Mercury": 7,
    "Moon": 10,
    "Venus": 10,
    "Saturn": 1,
}

STRONG_DIRECTION_HOUSES = {
    "Sun": 10,
    "Mars": 10,
    "Jupiter": 1,
    "Mercury": 1,
    "Moon": 4,
    "Venus": 4,
    "Saturn": 7,
}

DIG_BALA_METHODOLOGY = "bphs_dig_bala_bhava_madhya_v1"
DIG_BALA_ZERO_POINT_SOURCE = "sidereal_sripati_bhava_madhya_quadrants"


@dataclass(frozen=True, slots=True)
class DigBalaRow:
    planet: str
    weakest_house: int
    strongest_house: int
    weakest_point_longitude_sidereal: float
    angular_distance_degrees: float
    dig_bala_virupas: float


@dataclass(frozen=True, slots=True)
class DigBalaResult:
    methodology: str
    unit: str
    zero_point_source: str
    rows: tuple[DigBalaRow, ...]


def _validate_planet(planet: str) -> None:
    if planet not in CLASSICAL_PLANETS:
        raise ValueError(f"Dig Bala supports Sun through Saturn only; got {planet!r}.")


def _normalize_longitude(longitude: float) -> float:
    return float(longitude) % 360.0


def _shortest_angular_distance(a: float, b: float) -> float:
    delta = (_normalize_longitude(a) - _normalize_longitude(b)) % 360.0
    if delta > 180.0:
        delta = 360.0 - delta
    return delta


def calculate_dig_bala(
    planet: str,
    planet_longitude_sidereal: float,
    weakest_point_longitude_sidereal: float,
) -> float:
    """Return BPHS Dig Bala in virupas for one classical planet.

    BPHS 27.7 instructs subtracting the planet-specific weakest angular house
    point, folding separations above 180 degrees, and dividing the resulting
    degrees by three. The range is therefore exactly 0..60 virupas.
    """

    _validate_planet(planet)
    distance = _shortest_angular_distance(
        planet_longitude_sidereal,
        weakest_point_longitude_sidereal,
    )
    return distance / 3.0


def calculate_dig_bala_all(
    planet_longitudes_sidereal: Mapping[str, float],
    bhava_madhya_longitudes_sidereal: Mapping[int, float],
) -> DigBalaResult:
    """Calculate Dig Bala for Sun through Saturn from angular Bhava Madhyas.

    `bhava_madhya_longitudes_sidereal` must provide houses 1, 4, 7 and 10.
    In AstAi integration these are the audited sidereal Sripati Bhava Madhya
    angles (Ascendant, IC, Descendant and MC respectively), not whole-sign
    centers.
    """

    missing_planets = [planet for planet in CLASSICAL_PLANETS if planet not in planet_longitudes_sidereal]
    if missing_planets:
        raise ValueError("Missing Dig Bala longitude for: " + ", ".join(missing_planets))

    required_houses = (1, 4, 7, 10)
    missing_houses = [house for house in required_houses if house not in bhava_madhya_longitudes_sidereal]
    if missing_houses:
        raise ValueError(
            "Missing Dig Bala Bhava Madhya longitude for house(s): "
            + ", ".join(str(house) for house in missing_houses)
        )

    rows: list[DigBalaRow] = []
    for planet in CLASSICAL_PLANETS:
        weakest_house = WEAK_DIRECTION_HOUSES[planet]
        weakest_point = _normalize_longitude(
            bhava_madhya_longitudes_sidereal[weakest_house]
        )
        distance = _shortest_angular_distance(
            planet_longitudes_sidereal[planet], weakest_point
        )
        rows.append(
            DigBalaRow(
                planet=planet,
                weakest_house=weakest_house,
                strongest_house=STRONG_DIRECTION_HOUSES[planet],
                weakest_point_longitude_sidereal=weakest_point,
                angular_distance_degrees=distance,
                dig_bala_virupas=distance / 3.0,
            )
        )

    return DigBalaResult(
        methodology=DIG_BALA_METHODOLOGY,
        unit="virupa",
        zero_point_source=DIG_BALA_ZERO_POINT_SOURCE,
        rows=tuple(rows),
    )
