from __future__ import annotations

from dataclasses import dataclass

from astai.engine.constants import SIGNS

CLASSICAL_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
CONTRIBUTORS = (*CLASSICAL_PLANETS, "Ascendant")

# Benefic houses counted inclusively from each contributor's natal sign.
# These are the raw/unreduced classical BAV rules. Lagna contributes to every
# planetary BAV but does not form an eighth BAV in Sarvashtakavarga.
BENEFIC_HOUSES: dict[str, dict[str, tuple[int, ...]]] = {
    "Sun": {
        "Sun": (1, 2, 4, 7, 8, 9, 10, 11),
        "Moon": (3, 6, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (5, 6, 9, 11),
        "Venus": (6, 7, 12),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Ascendant": (3, 4, 6, 10, 11, 12),
    },
    "Moon": {
        "Sun": (3, 6, 7, 8, 10, 11),
        "Moon": (1, 3, 6, 7, 10, 11),
        "Mars": (2, 3, 5, 6, 9, 10, 11),
        "Mercury": (1, 3, 4, 5, 7, 8, 10, 11),
        "Jupiter": (1, 4, 7, 8, 10, 11, 12),
        "Venus": (3, 4, 5, 7, 9, 10, 11),
        "Saturn": (3, 5, 6, 11),
        "Ascendant": (3, 6, 10, 11),
    },
    "Mars": {
        "Sun": (3, 5, 6, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (3, 5, 6, 11),
        "Jupiter": (6, 10, 11, 12),
        "Venus": (6, 8, 11, 12),
        "Saturn": (1, 4, 7, 8, 9, 10, 11),
        "Ascendant": (1, 3, 6, 10, 11),
    },
    "Mercury": {
        "Sun": (5, 6, 9, 11, 12),
        "Moon": (2, 4, 6, 8, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (1, 3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (6, 8, 11, 12),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 11),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Ascendant": (1, 2, 4, 6, 8, 10, 11),
    },
    "Jupiter": {
        "Sun": (1, 2, 3, 4, 7, 8, 9, 10, 11),
        "Moon": (2, 5, 7, 9, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (1, 2, 4, 5, 6, 9, 10, 11),
        "Jupiter": (1, 2, 3, 4, 7, 8, 10, 11),
        "Venus": (2, 5, 6, 9, 10, 11),
        "Saturn": (3, 5, 6, 12),
        "Ascendant": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "Venus": {
        "Sun": (8, 11, 12),
        "Moon": (1, 2, 3, 4, 5, 8, 9, 11, 12),
        "Mars": (3, 5, 6, 9, 11, 12),
        "Mercury": (3, 5, 6, 9, 11),
        "Jupiter": (5, 8, 9, 10, 11),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 10, 11),
        "Saturn": (3, 4, 5, 8, 9, 10, 11),
        "Ascendant": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    "Saturn": {
        "Sun": (1, 2, 4, 7, 8, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (3, 5, 6, 10, 11, 12),
        "Mercury": (6, 8, 9, 10, 11, 12),
        "Jupiter": (5, 6, 11, 12),
        "Venus": (6, 11, 12),
        "Saturn": (3, 5, 6, 11),
        "Ascendant": (1, 3, 4, 6, 10, 11),
    },
}

EXPECTED_BAV_TOTALS = {
    "Sun": 48,
    "Moon": 49,
    "Mars": 39,
    "Mercury": 54,
    "Jupiter": 56,
    "Venus": 52,
    "Saturn": 39,
}


@dataclass(frozen=True, slots=True)
class ContributorRow:
    contributor: str
    points_by_sign: tuple[int, ...]
    total: int


@dataclass(frozen=True, slots=True)
class BhinnaAshtakavarga:
    planet: str
    points_by_sign: tuple[int, ...]
    total: int
    prastara: tuple[ContributorRow, ...]


@dataclass(frozen=True, slots=True)
class RawAshtakavarga:
    methodology: str
    sign_order: tuple[str, ...]
    point_semantics: str
    reduction_status: str
    bhinna: tuple[BhinnaAshtakavarga, ...]
    sarva_points_by_sign: tuple[int, ...]
    sarva_total: int


def _sign_index_map(ascendant_sign_index: int, planet_sign_indexes: dict[str, int]) -> dict[str, int]:
    missing = [planet for planet in CLASSICAL_PLANETS if planet not in planet_sign_indexes]
    if missing:
        raise ValueError(f"Missing classical planet sign(s) for Ashtakavarga: {', '.join(missing)}")
    if not 0 <= ascendant_sign_index <= 11:
        raise ValueError("Ascendant sign index must be between 0 and 11.")
    result = {planet: int(planet_sign_indexes[planet]) for planet in CLASSICAL_PLANETS}
    result["Ascendant"] = int(ascendant_sign_index)
    if any(not 0 <= idx <= 11 for idx in result.values()):
        raise ValueError("All Ashtakavarga source sign indexes must be between 0 and 11.")
    return result


def _contributor_row(source_sign_index: int, benefic_houses: tuple[int, ...]) -> tuple[int, ...]:
    row = [0] * 12
    for house in benefic_houses:
        row[(source_sign_index + house - 1) % 12] = 1
    return tuple(row)


def calculate_raw_ashtakavarga(
    ascendant_sign_index: int,
    planet_sign_indexes: dict[str, int],
) -> RawAshtakavarga:
    """Calculate unreduced classical BAV, Prastara and SAV.

    The seven classical planets each receive one BAV. Each BAV is the sum of
    eight binary contributor rows: Sun through Saturn plus Ascendant. The
    Sarvashtakavarga is the sign-wise sum of the seven unreduced BAV rows.
    """

    source_signs = _sign_index_map(ascendant_sign_index, planet_sign_indexes)
    bhinna: list[BhinnaAshtakavarga] = []

    for target in CLASSICAL_PLANETS:
        contribution_rows: list[ContributorRow] = []
        for contributor in CONTRIBUTORS:
            points = _contributor_row(
                source_signs[contributor],
                BENEFIC_HOUSES[target][contributor],
            )
            contribution_rows.append(
                ContributorRow(
                    contributor=contributor,
                    points_by_sign=points,
                    total=sum(points),
                )
            )

        points_by_sign = tuple(
            sum(row.points_by_sign[sign_index] for row in contribution_rows)
            for sign_index in range(12)
        )
        total = sum(points_by_sign)
        expected = EXPECTED_BAV_TOTALS[target]
        if total != expected:
            raise AssertionError(
                f"{target} BAV invariant failed: expected {expected}, got {total}."
            )
        bhinna.append(
            BhinnaAshtakavarga(
                planet=target,
                points_by_sign=points_by_sign,
                total=total,
                prastara=tuple(contribution_rows),
            )
        )

    sarva_points = tuple(
        sum(bav.points_by_sign[sign_index] for bav in bhinna)
        for sign_index in range(12)
    )
    sarva_total = sum(sarva_points)
    if sarva_total != 337:
        raise AssertionError(
            f"Sarvashtakavarga invariant failed: expected 337, got {sarva_total}."
        )

    return RawAshtakavarga(
        methodology="classical_raw_ashtakavarga_v1",
        sign_order=SIGNS,
        point_semantics="1 = benefic support; 0 = no benefic support",
        reduction_status="unreduced",
        bhinna=tuple(bhinna),
        sarva_points_by_sign=sarva_points,
        sarva_total=sarva_total,
    )
