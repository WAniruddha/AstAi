from __future__ import annotations

from astai.engine.constants import SIGNS
from astai.models import (
    AngularPoint,
    BhavaChalit,
    BhavaChalitPlacement,
    BhavaHouse,
    DMS,
    HouseCusp,
    PlanetPosition,
)

SRIPATI_METHODOLOGY = "sripati_bhava_chalit_v1"
_BOUNDARY_EPSILON_DEGREES = 1e-10
_BOUNDARY_POLICY = "half_open_[start,end); incoming_boundary_epsilon=1e-10_deg"


def _dms(degrees_within_sign: float) -> DMS:
    value = degrees_within_sign % 30.0
    centiseconds = int(round(value * 3600.0 * 100.0))
    centiseconds = min(centiseconds, 30 * 3600 * 100 - 1)
    degrees, remainder = divmod(centiseconds, 3600 * 100)
    minutes, remainder = divmod(remainder, 60 * 100)
    seconds = remainder / 100.0
    return DMS(
        degrees=degrees,
        minutes=minutes,
        seconds=seconds,
        text=f"{degrees:02d}°{minutes:02d}′{seconds:05.2f}″",
    )


def _forward_distance(start: float, end: float) -> float:
    return (end - start) % 360.0


def _forward_midpoint(start: float, end: float) -> float:
    return (start + _forward_distance(start, end) / 2.0) % 360.0


def _angular_diff(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _contains(longitude: float, start: float, end: float) -> bool:
    width = _forward_distance(start, end)
    offset = _forward_distance(start, longitude)
    return offset < width


def _house_for_longitude(longitude: float, boundaries: list[float]) -> int:
    value = longitude % 360.0
    for index, boundary in enumerate(boundaries):
        if _angular_diff(value, boundary) <= _BOUNDARY_EPSILON_DEGREES:
            return index + 1
    for index, start in enumerate(boundaries):
        end = boundaries[(index + 1) % 12]
        if _contains(value, start, end):
            return index + 1
    raise RuntimeError(f"Longitude {longitude} did not map to a Sripati house")


def _point_fields(longitude: float) -> tuple[str, DMS]:
    value = longitude % 360.0
    sign_index = int(value // 30.0)
    return SIGNS[sign_index], _dms(value % 30.0)


def calculate_sripati_bhava(
    ascendant: AngularPoint,
    planets: list[PlanetPosition],
    porphyry_madhyas: list[HouseCusp],
    swiss_sripati_boundaries: list[HouseCusp],
    crosscheck_tolerance_arcseconds: float = 1e-6,
) -> BhavaChalit:
    """Build Parashari Bhava/Chalit using the frozen Sripati convention.

    Porphyry house cusps are treated as Bhava Madhya. Each Sripati house starts
    at the forward midpoint between the previous and current Madhya. Planetary
    zodiac signs never change; only Bhava house membership is derived.
    """

    if len(porphyry_madhyas) != 12 or len(swiss_sripati_boundaries) != 12:
        raise ValueError("Sripati calculation requires exactly 12 Madhyas and 12 reference boundaries")

    madhyas = [c.longitude_sidereal % 360.0 for c in porphyry_madhyas]
    boundaries = [
        _forward_midpoint(madhyas[(index - 1) % 12], madhyas[index])
        for index in range(12)
    ]

    deltas_arcseconds = [
        _angular_diff(boundaries[index], swiss_sripati_boundaries[index].longitude_sidereal) * 3600.0
        for index in range(12)
    ]
    max_delta = max(deltas_arcseconds)
    if max_delta > crosscheck_tolerance_arcseconds:
        raise RuntimeError(
            "Derived Sripati boundaries disagree with Swiss Ephemeris native Sripati: "
            f"max delta {max_delta:.9f} arcsec"
        )

    houses: list[BhavaHouse] = []
    for index in range(12):
        start = boundaries[index]
        madhya = madhyas[index]
        end = boundaries[(index + 1) % 12]
        start_sign, start_dms = _point_fields(start)
        madhya_sign, madhya_dms = _point_fields(madhya)
        end_sign, end_dms = _point_fields(end)
        occupants = [
            planet.body
            for planet in planets
            if _house_for_longitude(planet.longitude_sidereal, boundaries) == index + 1
        ]
        houses.append(
            BhavaHouse(
                house=index + 1,
                start_longitude_sidereal=start,
                start_sign=start_sign,
                start_dms=start_dms,
                madhya_longitude_sidereal=madhya,
                madhya_sign=madhya_sign,
                madhya_dms=madhya_dms,
                end_longitude_sidereal=end,
                end_sign=end_sign,
                end_dms=end_dms,
                span_degrees=_forward_distance(start, end),
                planets=occupants,
            )
        )

    placements: list[BhavaChalitPlacement] = []
    for planet in planets:
        rasi_house = ((planet.sign_index - ascendant.sign_index) % 12) + 1
        bhava_house = _house_for_longitude(planet.longitude_sidereal, boundaries)
        placements.append(
            BhavaChalitPlacement(
                body=planet.body,
                longitude_sidereal=planet.longitude_sidereal,
                rasi_sign=planet.sign,
                rasi_house=rasi_house,
                bhava_house=bhava_house,
                shifted=(rasi_house != bhava_house),
            )
        )

    total_span = sum(house.span_degrees for house in houses)
    if abs(total_span - 360.0) > 1e-9:
        raise RuntimeError(f"Sripati house spans do not close to 360°: {total_span}")

    return BhavaChalit(
        methodology=SRIPATI_METHODOLOGY,
        boundary_policy=_BOUNDARY_POLICY,
        houses=houses,
        placements=placements,
        swiss_sripati_crosscheck_max_arcseconds=max_delta,
    )
