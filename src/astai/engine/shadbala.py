from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from astai.engine.saptavargaja import (
    CLASSICAL_PLANETS,
    RELATIONSHIP_METHODOLOGY,
    calculate_saptavargaja_bala,
)

# Deep debilitation points in the sidereal zodiac, Aries = 0 degrees.
# Deep exaltation is exactly 180 degrees opposite.
DEBILITATION_LONGITUDES = {
    "Sun": 190.0,      # Libra 10
    "Moon": 213.0,     # Scorpio 3
    "Mars": 118.0,     # Cancer 28
    "Mercury": 345.0,  # Pisces 15
    "Jupiter": 275.0,  # Capricorn 5
    "Venus": 177.0,    # Virgo 27
    "Saturn": 20.0,    # Aries 20
}

# BPHS 27.14: 60/7 multiplied by 1..7 for
# Saturn, Mars, Mercury, Jupiter, Venus, Moon, Sun.
NAISARGIKA_FACTORS = {
    "Saturn": 1,
    "Mars": 2,
    "Mercury": 3,
    "Jupiter": 4,
    "Venus": 5,
    "Moon": 6,
    "Sun": 7,
}

# BPHS 27.6:
# male planets -> first drekkana;
# hermaphrodite planets -> second;
# female planets -> third.
DREKKANA_TARGET = {
    "Sun": 1,
    "Mars": 1,
    "Jupiter": 1,
    "Mercury": 2,
    "Saturn": 2,
    "Moon": 3,
    "Venus": 3,
}

FOUNDATION_METHODOLOGY = "bphs_shadbala_foundation_v1"
ASTAI_STANDARD_SAPTAVARGAJA_PROFILE = "bphs_textual_all_vargas_v1"


@dataclass(frozen=True, slots=True)
class ShadbalaFoundationRow:
    planet: str
    uccha_bala_virupas: float
    ojayugma_bala_virupas: float
    kendradi_bala_virupas: float
    drekkana_bala_virupas: float
    sthana_known_subtotal_virupas: float
    naisargika_bala_virupas: float
    saptavargaja_bala_virupas: float | None = None
    sthana_bala_total_virupas: float | None = None


@dataclass(frozen=True, slots=True)
class ShadbalaFoundation:
    methodology: str
    unit: str
    aggregation_status: str
    rows: tuple[ShadbalaFoundationRow, ...]
    saptavargaja_profile: str | None = None
    saptavargaja_relationship_methodology: str | None = None


def _validate_planet(planet: str) -> None:
    if planet not in CLASSICAL_PLANETS:
        raise ValueError(f"Shadbala foundation supports Sun through Saturn only; got {planet!r}.")


def _angular_distance_degrees(a: float, b: float) -> float:
    delta = abs((float(a) - float(b)) % 360.0)
    return min(delta, 360.0 - delta)


def calculate_uccha_bala(planet: str, longitude_sidereal: float) -> float:
    """BPHS 27.1: distance from deep debilitation, capped at 180 degrees, divided by 3."""

    _validate_planet(planet)
    distance = _angular_distance_degrees(longitude_sidereal, DEBILITATION_LONGITUDES[planet])
    return distance / 3.0


def calculate_ojayugma_bala(
    planet: str,
    rasi_sign_index: int,
    navamsa_sign_index: int,
) -> float:
    """BPHS 27.2/27.5: 15 virupas each for qualifying Rasi and Navamsa parity."""

    _validate_planet(planet)
    if not 0 <= int(rasi_sign_index) <= 11 or not 0 <= int(navamsa_sign_index) <= 11:
        raise ValueError("Rasi and Navamsa sign indexes must be between 0 and 11.")

    wants_even = planet in {"Moon", "Venus"}

    def qualifies(sign_index: int) -> bool:
        sign_number_is_even = (int(sign_index) + 1) % 2 == 0
        return sign_number_is_even if wants_even else not sign_number_is_even

    return 15.0 * (
        int(qualifies(rasi_sign_index)) + int(qualifies(navamsa_sign_index))
    )


def calculate_kendradi_bala(house: int) -> float:
    """BPHS 27.5: Kendra 60, Panaphara 30, Apoklima 15 virupas."""

    house = int(house)
    if not 1 <= house <= 12:
        raise ValueError("House must be between 1 and 12.")
    if house in {1, 4, 7, 10}:
        return 60.0
    if house in {2, 5, 8, 11}:
        return 30.0
    return 15.0


def calculate_drekkana_bala(planet: str, sign_degree: float) -> float:
    """BPHS 27.6: male/neutral/female planets gain 15 in 1st/2nd/3rd drekkana."""

    _validate_planet(planet)
    degree = float(sign_degree)
    if not 0.0 <= degree < 30.0:
        raise ValueError("Sign degree must be in [0, 30).")
    drekkana = min(int(degree // 10.0) + 1, 3)
    return 15.0 if drekkana == DREKKANA_TARGET[planet] else 0.0


def calculate_naisargika_bala(planet: str) -> float:
    """BPHS 27.14 fixed natural strength in virupas."""

    _validate_planet(planet)
    return (60.0 / 7.0) * NAISARGIKA_FACTORS[planet]


def calculate_shadbala_foundation(
    ascendant_sign_index: int,
    planet_longitudes: Mapping[str, float],
    planet_sign_indexes: Mapping[str, int],
    planet_sign_degrees: Mapping[str, float],
    navamsa_sign_indexes: Mapping[str, int],
    saptavarga_positions_by_planet: Mapping[
        str, Mapping[str, tuple[int, float]]
    ] | None = None,
    saptavargaja_profile: str = ASTAI_STANDARD_SAPTAVARGAJA_PROFILE,
) -> ShadbalaFoundation:
    """Compute the frozen v0.8 Shadbala foundation.

    Without Saptavarga positions the function preserves the earlier partial
    foundation behavior and refuses to emit complete Sthana Bala. When all
    seven planets receive D1/D2/D3/D7/D9/D12/D30 positions, Saptavargaja is
    calculated under the explicit profile and complete Sthana Bala is emitted.

    Naisargika Bala is intentionally *not* part of Sthana Bala; it remains a
    separate Shadbala component.
    """

    ascendant_sign_index = int(ascendant_sign_index)
    if not 0 <= ascendant_sign_index <= 11:
        raise ValueError("Ascendant sign index must be between 0 and 11.")

    if saptavarga_positions_by_planet is not None:
        missing_planets = [
            planet
            for planet in CLASSICAL_PLANETS
            if planet not in saptavarga_positions_by_planet
        ]
        if missing_planets:
            raise ValueError(
                "Missing Saptavargaja positions for: " + ", ".join(missing_planets)
            )

    rows: list[ShadbalaFoundationRow] = []
    for planet in CLASSICAL_PLANETS:
        try:
            longitude = planet_longitudes[planet]
            sign_index = planet_sign_indexes[planet]
            sign_degree = planet_sign_degrees[planet]
            navamsa_sign_index = navamsa_sign_indexes[planet]
        except KeyError as exc:
            raise ValueError(f"Missing {planet} input for Shadbala foundation.") from exc

        house = ((int(sign_index) - ascendant_sign_index) % 12) + 1
        uccha = calculate_uccha_bala(planet, longitude)
        ojayugma = calculate_ojayugma_bala(planet, sign_index, navamsa_sign_index)
        kendradi = calculate_kendradi_bala(house)
        drekkana = calculate_drekkana_bala(planet, sign_degree)
        known_subtotal = uccha + ojayugma + kendradi + drekkana

        saptavargaja = None
        sthana_total = None
        if saptavarga_positions_by_planet is not None:
            saptavargaja_result = calculate_saptavargaja_bala(
                planet=planet,
                varga_positions=saptavarga_positions_by_planet[planet],
                d1_planet_sign_indexes=planet_sign_indexes,
                profile=saptavargaja_profile,
            )
            saptavargaja = saptavargaja_result.total_virupas
            sthana_total = known_subtotal + saptavargaja

        rows.append(
            ShadbalaFoundationRow(
                planet=planet,
                uccha_bala_virupas=uccha,
                ojayugma_bala_virupas=ojayugma,
                kendradi_bala_virupas=kendradi,
                drekkana_bala_virupas=drekkana,
                sthana_known_subtotal_virupas=known_subtotal,
                naisargika_bala_virupas=calculate_naisargika_bala(planet),
                saptavargaja_bala_virupas=saptavargaja,
                sthana_bala_total_virupas=sthana_total,
            )
        )

    if saptavarga_positions_by_planet is None:
        return ShadbalaFoundation(
            methodology=FOUNDATION_METHODOLOGY,
            unit="virupa",
            aggregation_status=(
                "partial_saptavargaja_pending_no_sthana_or_shadbala_total"
            ),
            rows=tuple(rows),
        )

    return ShadbalaFoundation(
        methodology=FOUNDATION_METHODOLOGY,
        unit="virupa",
        aggregation_status="complete_sthana_bala_other_shadbala_components_pending",
        rows=tuple(rows),
        saptavargaja_profile=saptavargaja_profile,
        saptavargaja_relationship_methodology=RELATIONSHIP_METHODOLOGY,
    )
