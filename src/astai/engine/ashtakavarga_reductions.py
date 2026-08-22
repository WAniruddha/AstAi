from __future__ import annotations

from dataclasses import dataclass

from astai.engine.ashtakavarga import CLASSICAL_PLANETS, RawAshtakavarga

TRIKONA_GROUPS = (
    (0, 4, 8),
    (1, 5, 9),
    (2, 6, 10),
    (3, 7, 11),
)

DUAL_OWNERSHIP_PAIRS = {
    "Mars": (0, 7),
    "Venus": (1, 6),
    "Mercury": (2, 5),
    "Jupiter": (8, 11),
    "Saturn": (9, 10),
}

GRAHA_MULTIPLIERS = {
    "Sun": 5,
    "Moon": 5,
    "Mars": 8,
    "Mercury": 5,
    "Jupiter": 10,
    "Venus": 7,
    "Saturn": 5,
}

PINDA_RASI_PROFILES = {
    "bphs_parenthetical_v1": (7, 10, 8, 4, 10, 6, 7, 8, 9, 5, 11, 12),
    "legacy_virgo5_v1": (7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 11, 12),
}

DEFAULT_REDUCTION_PROFILE = "bphs_common_v1"
DEFAULT_PINDA_PROFILE = "bphs_parenthetical_v1"
LEGACY_PINDA_PROFILE = "legacy_virgo5_v1"


@dataclass(frozen=True, slots=True)
class ReducedBhinnaAshtakavarga:
    planet: str
    raw_points_by_sign: tuple[int, ...]
    trikona_points_by_sign: tuple[int, ...]
    ekadhipatya_points_by_sign: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class PindaResult:
    planet: str
    rasi_pinda: int
    graha_pinda: int
    shodhya_pinda: int


@dataclass(frozen=True, slots=True)
class PindaProfileResult:
    profile: str
    rasi_multipliers: tuple[int, ...]
    graha_multipliers: tuple[tuple[str, int], ...]
    results: tuple[PindaResult, ...]


@dataclass(frozen=True, slots=True)
class AshtakavargaReductions:
    methodology: str
    occupancy_semantics: str
    standard_pinda_profile: str
    bhinna: tuple[ReducedBhinnaAshtakavarga, ...]
    pinda_profiles: tuple[PindaProfileResult, ...]


def _validated_points(points: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    if len(points) != 12:
        raise ValueError("Ashtakavarga reduction rows must contain exactly 12 sign values.")
    values = tuple(int(value) for value in points)
    if any(value < 0 for value in values):
        raise ValueError("Ashtakavarga reduction values cannot be negative.")
    return values


def _validated_planet_signs(planet_sign_indexes: dict[str, int]) -> dict[str, int]:
    missing = [planet for planet in CLASSICAL_PLANETS if planet not in planet_sign_indexes]
    if missing:
        raise ValueError(
            "Missing classical planet sign(s) for Ashtakavarga reductions: "
            + ", ".join(missing)
        )
    result = {planet: int(planet_sign_indexes[planet]) for planet in CLASSICAL_PLANETS}
    if any(index < 0 or index > 11 for index in result.values()):
        raise ValueError("All Ashtakavarga planet sign indexes must be between 0 and 11.")
    return result


def apply_trikona_shodhana(points: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    """Apply the common BPHS Trikona Shodhana: subtract each trine's minimum."""

    reduced = list(_validated_points(points))
    for group in TRIKONA_GROUPS:
        minimum = min(reduced[index] for index in group)
        if minimum == 0:
            continue
        for index in group:
            reduced[index] -= minimum
    return tuple(reduced)


def apply_ekadhipatya_shodhana(
    points: tuple[int, ...] | list[int],
    occupied_sign_indexes: set[int] | frozenset[int] | tuple[int, ...] | list[int],
) -> tuple[int, ...]:
    """Apply the common BPHS Ekadhipatya rules after Trikona Shodhana.

    Occupancy is sign-level presence of any of the seven classical planets.
    Rahu/Ketu, outer planets and the Ascendant do not count as Graha occupancy
    for this declared profile.
    """

    reduced = list(_validated_points(points))
    occupied = {int(index) for index in occupied_sign_indexes}
    if any(index < 0 or index > 11 for index in occupied):
        raise ValueError("Occupied sign indexes must be between 0 and 11.")

    for first, second in DUAL_OWNERSHIP_PAIRS.values():
        first_value = reduced[first]
        second_value = reduced[second]

        if first_value == 0 or second_value == 0:
            continue

        first_occupied = first in occupied
        second_occupied = second in occupied

        if first_occupied and second_occupied:
            continue

        if not first_occupied and not second_occupied:
            if first_value == second_value:
                reduced[first] = 0
                reduced[second] = 0
            else:
                minimum = min(first_value, second_value)
                reduced[first] = minimum
                reduced[second] = minimum
            continue

        occupied_index, empty_index = (
            (first, second) if first_occupied else (second, first)
        )
        occupied_value = reduced[occupied_index]
        empty_value = reduced[empty_index]
        reduced[empty_index] = max(0, empty_value - occupied_value)

    return tuple(reduced)


def calculate_pinda(
    planet: str,
    points: tuple[int, ...] | list[int],
    planet_sign_indexes: dict[str, int],
    *,
    profile: str = DEFAULT_PINDA_PROFILE,
) -> PindaResult:
    """Calculate Rasi, Graha and Shodhya Pinda from post-Ekadhipatya values."""

    if planet not in CLASSICAL_PLANETS:
        raise ValueError(f"Unsupported Ashtakavarga target planet: {planet}")
    values = _validated_points(points)
    planet_signs = _validated_planet_signs(planet_sign_indexes)
    try:
        rasi_multipliers = PINDA_RASI_PROFILES[profile]
    except KeyError as exc:
        raise ValueError(f"Unsupported Ashtakavarga Pinda profile: {profile}") from exc

    rasi_pinda = sum(
        value * multiplier
        for value, multiplier in zip(values, rasi_multipliers, strict=True)
    )
    graha_pinda = sum(
        values[planet_signs[source_planet]] * GRAHA_MULTIPLIERS[source_planet]
        for source_planet in CLASSICAL_PLANETS
    )
    return PindaResult(
        planet=planet,
        rasi_pinda=rasi_pinda,
        graha_pinda=graha_pinda,
        shodhya_pinda=rasi_pinda + graha_pinda,
    )


def calculate_ashtakavarga_reductions(
    raw: RawAshtakavarga,
    planet_sign_indexes: dict[str, int],
) -> AshtakavargaReductions:
    """Derive audited BPHS-common reductions and explicit Pinda profiles.

    The v0.6 raw BAV/SAV object is never mutated. Both reduction stages are
    retained per target planet. Two Pinda profiles are emitted because the
    commonly circulated BPHS Rasiman table and a widespread legacy/vendor
    convention disagree on the Virgo multiplier.
    """

    planet_signs = _validated_planet_signs(planet_sign_indexes)
    occupied_signs = frozenset(planet_signs.values())

    reduced_rows: list[ReducedBhinnaAshtakavarga] = []
    for bav in raw.bhinna:
        trikona = apply_trikona_shodhana(bav.points_by_sign)
        ekadhipatya = apply_ekadhipatya_shodhana(trikona, occupied_signs)
        if any(
            after > before
            for before, after in zip(bav.points_by_sign, trikona, strict=True)
        ):
            raise AssertionError("Trikona Shodhana increased a raw Ashtakavarga value.")
        if any(
            after > before
            for before, after in zip(trikona, ekadhipatya, strict=True)
        ):
            raise AssertionError("Ekadhipatya Shodhana increased a Trikona value.")
        reduced_rows.append(
            ReducedBhinnaAshtakavarga(
                planet=bav.planet,
                raw_points_by_sign=tuple(bav.points_by_sign),
                trikona_points_by_sign=trikona,
                ekadhipatya_points_by_sign=ekadhipatya,
            )
        )

    pinda_profiles: list[PindaProfileResult] = []
    for profile in (DEFAULT_PINDA_PROFILE, LEGACY_PINDA_PROFILE):
        results = tuple(
            calculate_pinda(
                row.planet,
                row.ekadhipatya_points_by_sign,
                planet_signs,
                profile=profile,
            )
            for row in reduced_rows
        )
        pinda_profiles.append(
            PindaProfileResult(
                profile=profile,
                rasi_multipliers=PINDA_RASI_PROFILES[profile],
                graha_multipliers=tuple(
                    (planet, GRAHA_MULTIPLIERS[planet]) for planet in CLASSICAL_PLANETS
                ),
                results=results,
            )
        )

    return AshtakavargaReductions(
        methodology=DEFAULT_REDUCTION_PROFILE,
        occupancy_semantics=(
            "Sign is occupied when one or more of Sun through Saturn is present; "
            "Rahu/Ketu, outer planets and Ascendant are excluded."
        ),
        standard_pinda_profile=DEFAULT_PINDA_PROFILE,
        bhinna=tuple(reduced_rows),
        pinda_profiles=tuple(pinda_profiles),
    )
