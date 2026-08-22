from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

CLASSICAL_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
SAPTAVARGA_CODES = ("D1", "D2", "D3", "D7", "D9", "D12", "D30")

SIGN_LORDS = (
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
)

# Natural friendship used to build Panchadha Maitri. Anything not listed as
# friend/enemy (and not self) is neutral.
NATURAL_RELATIONSHIPS = {
    "Sun": {
        "friend": frozenset({"Moon", "Mars", "Jupiter"}),
        "enemy": frozenset({"Venus", "Saturn"}),
    },
    "Moon": {
        "friend": frozenset({"Sun", "Mercury"}),
        "enemy": frozenset(),
    },
    "Mars": {
        "friend": frozenset({"Sun", "Moon", "Jupiter"}),
        "enemy": frozenset({"Mercury"}),
    },
    "Mercury": {
        "friend": frozenset({"Sun", "Venus"}),
        "enemy": frozenset({"Moon"}),
    },
    "Jupiter": {
        "friend": frozenset({"Sun", "Moon", "Mars"}),
        "enemy": frozenset({"Mercury", "Venus"}),
    },
    "Venus": {
        "friend": frozenset({"Mercury", "Saturn"}),
        "enemy": frozenset({"Sun", "Moon"}),
    },
    "Saturn": {
        "friend": frozenset({"Mercury", "Venus"}),
        "enemy": frozenset({"Sun", "Moon", "Mars"}),
    },
}

# BPHS D1 Moolatrikona degree spans. Intervals are half-open [start, end).
# For higher Vargas the explicit textual profile uses Moolatrikona sign
# occupation only, not normalized Varga degrees.
MOOLATRIKONA_RANGES = {
    "Sun": (4, 0.0, 20.0),
    "Moon": (1, 3.0, 30.0),
    "Mars": (0, 0.0, 12.0),
    "Mercury": (5, 15.0, 20.0),
    "Jupiter": (8, 0.0, 10.0),
    "Venus": (6, 0.0, 15.0),
    "Saturn": (10, 0.0, 20.0),
}

TEMPORARY_FRIEND_HOUSES = frozenset({2, 3, 4, 10, 11, 12})
RELATIONSHIP_METHODOLOGY = "d1_panchadha_maitri_reused_across_saptavargas_v1"


@dataclass(frozen=True, slots=True)
class SaptavargajaProfile:
    profile: str
    scores: Mapping[str, float]
    moolatrikona_scope: str


# Two explicit profiles are retained because the textual BPHS weights and a
# widespread modern Panchadha-Maitri working convention are not identical.
# No silent compatibility conversion is allowed.
SAPTAVARGAJA_PROFILES = {
    "bphs_textual_all_vargas_v1": SaptavargajaProfile(
        profile="bphs_textual_all_vargas_v1",
        scores={
            "moolatrikona": 45.0,
            "own": 30.0,
            "great_friend": 20.0,
            "friend": 15.0,
            "neutral": 10.0,
            "enemy": 4.0,
            "great_enemy": 2.0,
        },
        moolatrikona_scope="d1_degree_higher_vargas_sign",
    ),
    "modern_panchadha_d1_mt_v1": SaptavargajaProfile(
        profile="modern_panchadha_d1_mt_v1",
        scores={
            "moolatrikona": 45.0,
            "own": 30.0,
            "great_friend": 22.5,
            "friend": 15.0,
            "neutral": 7.5,
            "enemy": 3.75,
            "great_enemy": 1.875,
        },
        moolatrikona_scope="d1_only_degree",
    ),
}


@dataclass(frozen=True, slots=True)
class SaptavargajaVargaResult:
    varga: str
    sign_index: int
    sign_degree: float
    dignity: str
    virupas: float


@dataclass(frozen=True, slots=True)
class SaptavargajaResult:
    planet: str
    profile: str
    relationship_methodology: str
    moolatrikona_scope: str
    vargas: tuple[SaptavargajaVargaResult, ...]
    total_virupas: float


def _validate_planet(planet: str) -> None:
    if planet not in CLASSICAL_PLANETS:
        raise ValueError(
            f"Saptavargaja Bala supports Sun through Saturn only; got {planet!r}."
        )


def _validate_d1_signs(d1_planet_sign_indexes: Mapping[str, int]) -> dict[str, int]:
    missing = [planet for planet in CLASSICAL_PLANETS if planet not in d1_planet_sign_indexes]
    if missing:
        raise ValueError("Missing D1 sign index for: " + ", ".join(missing))
    result = {
        planet: int(d1_planet_sign_indexes[planet])
        for planet in CLASSICAL_PLANETS
    }
    if any(index < 0 or index > 11 for index in result.values()):
        raise ValueError("All D1 planet sign indexes must be between 0 and 11.")
    return result


def get_natural_relationship(planet: str, other: str) -> str:
    _validate_planet(planet)
    _validate_planet(other)
    if planet == other:
        return "self"
    relationships = NATURAL_RELATIONSHIPS[planet]
    if other in relationships["friend"]:
        return "friend"
    if other in relationships["enemy"]:
        return "enemy"
    return "neutral"


def get_temporary_relationship(
    planet: str,
    other: str,
    d1_planet_sign_indexes: Mapping[str, int],
) -> str:
    """Return temporary friendship from the D1 planetary arrangement only."""

    _validate_planet(planet)
    _validate_planet(other)
    signs = _validate_d1_signs(d1_planet_sign_indexes)
    if planet == other:
        return "self"
    relative_house = ((signs[other] - signs[planet]) % 12) + 1
    return "friend" if relative_house in TEMPORARY_FRIEND_HOUSES else "enemy"


def get_compound_relationship(
    planet: str,
    other: str,
    d1_planet_sign_indexes: Mapping[str, int],
) -> str:
    """Combine natural and temporary friendship into the fivefold relationship."""

    natural = get_natural_relationship(planet, other)
    if natural == "self":
        return "self"
    temporary = get_temporary_relationship(planet, other, d1_planet_sign_indexes)

    if natural == "friend":
        return "great_friend" if temporary == "friend" else "neutral"
    if natural == "neutral":
        return "friend" if temporary == "friend" else "enemy"
    return "neutral" if temporary == "friend" else "great_enemy"


def _is_d1_moolatrikona(planet: str, sign_index: int, sign_degree: float) -> bool:
    mt_sign, start, end = MOOLATRIKONA_RANGES[planet]
    return sign_index == mt_sign and start <= sign_degree < end


def _is_moolatrikona_for_profile(
    planet: str,
    varga: str,
    sign_index: int,
    sign_degree: float,
    methodology: SaptavargajaProfile,
) -> bool:
    if varga == "D1":
        return _is_d1_moolatrikona(planet, sign_index, sign_degree)

    if methodology.moolatrikona_scope == "d1_only_degree":
        return False

    # BPHS textual/all-Varga profile: higher divisions are judged by sign
    # occupation. Do not interpret the normalized Varga degree as a natal
    # Moolatrikona degree range.
    mt_sign = MOOLATRIKONA_RANGES[planet][0]
    return sign_index == mt_sign


def classify_saptavargaja_dignity(
    planet: str,
    varga: str,
    sign_index: int,
    sign_degree: float,
    d1_planet_sign_indexes: Mapping[str, int],
    profile: str,
) -> str:
    _validate_planet(planet)
    if varga not in SAPTAVARGA_CODES:
        raise ValueError(f"Unsupported Saptavargaja varga: {varga}")

    sign_index = int(sign_index)
    sign_degree = float(sign_degree)
    if not 0 <= sign_index <= 11:
        raise ValueError("Varga sign index must be between 0 and 11.")
    if not 0.0 <= sign_degree < 30.0:
        raise ValueError("Varga sign degree must be in [0, 30).")

    try:
        methodology = SAPTAVARGAJA_PROFILES[profile]
    except KeyError as exc:
        raise ValueError(f"Unknown Saptavargaja profile: {profile}") from exc

    signs = _validate_d1_signs(d1_planet_sign_indexes)
    if _is_moolatrikona_for_profile(
        planet, varga, sign_index, sign_degree, methodology
    ):
        return "moolatrikona"

    sign_lord = SIGN_LORDS[sign_index]
    if sign_lord == planet:
        return "own"
    return get_compound_relationship(planet, sign_lord, signs)


def calculate_saptavargaja_bala(
    planet: str,
    varga_positions: Mapping[str, tuple[int, float]],
    d1_planet_sign_indexes: Mapping[str, int],
    profile: str,
) -> SaptavargajaResult:
    """Calculate one planet's Saptavargaja Bala under an explicit profile.

    `varga_positions` supplies already-computed (sign_index, sign_degree) pairs
    for D1/D2/D3/D7/D9/D12/D30. This module intentionally does not select a
    Hora or other varga construction method; that remains the responsibility
    of AstAi's audited divisional-chart layer when integration happens later.
    """

    _validate_planet(planet)
    try:
        methodology = SAPTAVARGAJA_PROFILES[profile]
    except KeyError as exc:
        raise ValueError(f"Unknown Saptavargaja profile: {profile}") from exc

    signs = _validate_d1_signs(d1_planet_sign_indexes)
    missing = [code for code in SAPTAVARGA_CODES if code not in varga_positions]
    if missing:
        raise ValueError(
            "Missing Saptavargaja varga position(s): " + ", ".join(missing)
        )

    d1_sign = int(varga_positions["D1"][0])
    if d1_sign != signs[planet]:
        raise ValueError(
            f"D1 Saptavargaja position for {planet} does not match the declared D1 sign index."
        )

    rows: list[SaptavargajaVargaResult] = []
    for code in SAPTAVARGA_CODES:
        sign_index, sign_degree = varga_positions[code]
        sign_index = int(sign_index)
        sign_degree = float(sign_degree)
        dignity = classify_saptavargaja_dignity(
            planet,
            code,
            sign_index,
            sign_degree,
            signs,
            profile,
        )
        rows.append(
            SaptavargajaVargaResult(
                varga=code,
                sign_index=sign_index,
                sign_degree=sign_degree,
                dignity=dignity,
                virupas=float(methodology.scores[dignity]),
            )
        )

    total = sum(row.virupas for row in rows)
    return SaptavargajaResult(
        planet=planet,
        profile=methodology.profile,
        relationship_methodology=RELATIONSHIP_METHODOLOGY,
        moolatrikona_scope=methodology.moolatrikona_scope,
        vargas=tuple(rows),
        total_virupas=total,
    )
