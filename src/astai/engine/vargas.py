from __future__ import annotations

from dataclasses import dataclass
from math import floor

from astai.engine.astronomy import _dms
from astai.engine.constants import SIGNS
from astai.models import AngularPoint, PlanetPosition, VargaChart, VargaPlacement, VargaProfile


@dataclass(frozen=True)
class VargaSpec:
    code: str
    division: int
    name: str


SHODASHAVARGA_SPECS = (
    VargaSpec("D1", 1, "Rasi"),
    VargaSpec("D2", 2, "Hora"),
    VargaSpec("D3", 3, "Drekkana"),
    VargaSpec("D4", 4, "Chaturthamsa"),
    VargaSpec("D7", 7, "Saptamsa"),
    VargaSpec("D9", 9, "Navamsa"),
    VargaSpec("D10", 10, "Dasamsa"),
    VargaSpec("D12", 12, "Dwadasamsa"),
    VargaSpec("D16", 16, "Shodasamsa"),
    VargaSpec("D20", 20, "Vimsamsa"),
    VargaSpec("D24", 24, "Chaturvimsamsa"),
    VargaSpec("D27", 27, "Saptavimsamsa"),
    VargaSpec("D30", 30, "Trimsamsa"),
    VargaSpec("D40", 40, "Khavedamsa"),
    VargaSpec("D45", 45, "Akshavedamsa"),
    VargaSpec("D60", 60, "Shashtiamsa"),
)
SPEC_BY_CODE = {spec.code: spec for spec in SHODASHAVARGA_SPECS}

MOVABLE_SIGNS = {0, 3, 6, 9}
FIXED_SIGNS = {1, 4, 7, 10}
DUAL_SIGNS = {2, 5, 8, 11}
FIRE_SIGNS = {0, 4, 8}
EARTH_SIGNS = {1, 5, 9}
AIR_SIGNS = {2, 6, 10}
WATER_SIGNS = {3, 7, 11}

PARASHARA_METHODOLOGY = "parashara_traditional_v1"
ASTROSAGE_D7_COMPAT_METHODOLOGY = "astrosage_reference_compat_v1_d7_degree_truncation"


@dataclass(frozen=True)
class AmsaResult:
    sign_index: int
    varga_degree: float
    amsa_index: int  # 1-based
    source_sign_degree: float
    amsa_start_degree: float
    amsa_end_degree: float
    boundary_distance_arcminutes: float


def _equal_amsa(sign_degree: float, division: int, index_degree: float | None = None) -> tuple[int, float, float, float, float]:
    """Return 0-based amsa index, start, end, normalized degree and boundary distance.

    The source interval convention is half-open [start, end). `index_degree` is
    used only for explicit compatibility modes; all audit geometry remains
    based on the actual source longitude.
    """

    width = 30.0 / division
    selection_degree = sign_degree if index_degree is None else index_degree
    segment = min(int(floor(selection_degree / width)), division - 1)
    start = segment * width
    end = (segment + 1) * width

    # Keep the within-amsa degree tied to the exact source longitude even if a
    # named compatibility profile changes only the selected amsa index. This
    # mirrors the common `longitude * division mod 30` construction and avoids
    # inventing a clipped degree when a vendor-compatibility segment differs
    # from the exact classical segment. Boundary distance is likewise measured
    # against the exact equal-division grid, not the compatibility selector.
    remainder = sign_degree % width
    normalized = (remainder / width) * 30.0
    boundary = min(remainder, width - remainder) * 60.0
    return segment, start, end, normalized, boundary


def _d30_amsa(sign_index: int, sign_degree: float) -> tuple[int, int, float, float, float, float]:
    """Traditional unequal Parashari Trimsamsa mapping."""

    if sign_index % 2 == 0:  # odd zodiac signs: Aries, Gemini, ...
        ranges = (
            (0.0, 5.0, 0),
            (5.0, 10.0, 10),
            (10.0, 18.0, 8),
            (18.0, 25.0, 2),
            (25.0, 30.0, 6),
        )
    else:
        ranges = (
            (0.0, 5.0, 1),
            (5.0, 12.0, 5),
            (12.0, 20.0, 11),
            (20.0, 25.0, 9),
            (25.0, 30.0, 7),
        )

    for segment, (start, end, target) in enumerate(ranges):
        if start <= sign_degree < end:
            width = end - start
            normalized = ((sign_degree - start) / width) * 30.0
            boundary = min(sign_degree - start, end - sign_degree) * 60.0
            return target, segment, start, end, normalized, boundary

    # sign_degree is always in [0, 30), but keep an explicit failure if that
    # upstream invariant is ever broken.
    raise ValueError(f"Invalid within-sign degree for D30: {sign_degree}")


def _target_for_equal_varga(sign_index: int, segment: int, code: str) -> int:
    odd_zodiac_sign = sign_index % 2 == 0

    if code == "D1":
        return sign_index
    if code == "D2":
        # Traditional Sun/Moon Hora: Leo/Cancer in odd signs, reversed in even.
        return (4 if segment == 0 else 3) if odd_zodiac_sign else (3 if segment == 0 else 4)
    if code == "D3":
        return (sign_index + 4 * segment) % 12
    if code == "D4":
        return (sign_index + 3 * segment) % 12
    if code == "D7":
        start = sign_index if odd_zodiac_sign else sign_index + 6
        return (start + segment) % 12
    if code == "D9":
        if sign_index in MOVABLE_SIGNS:
            start = sign_index
        elif sign_index in FIXED_SIGNS:
            start = sign_index + 8
        else:
            start = sign_index + 4
        return (start + segment) % 12
    if code == "D10":
        start = sign_index if odd_zodiac_sign else sign_index + 8
        return (start + segment) % 12
    if code == "D12":
        return (sign_index + segment) % 12
    if code == "D16":
        start = 0 if sign_index in MOVABLE_SIGNS else 4 if sign_index in FIXED_SIGNS else 8
        return (start + segment) % 12
    if code == "D20":
        start = 0 if sign_index in MOVABLE_SIGNS else 8 if sign_index in FIXED_SIGNS else 4
        return (start + segment) % 12
    if code == "D24":
        start = 4 if odd_zodiac_sign else 3
        return (start + segment) % 12
    if code == "D27":
        if sign_index in FIRE_SIGNS:
            start = 0
        elif sign_index in EARTH_SIGNS:
            start = 3
        elif sign_index in AIR_SIGNS:
            start = 6
        else:
            start = 9
        return (start + segment) % 12
    if code == "D40":
        return ((0 if odd_zodiac_sign else 6) + segment) % 12
    if code == "D45":
        start = 0 if sign_index in MOVABLE_SIGNS else 4 if sign_index in FIXED_SIGNS else 8
        return (start + segment) % 12
    if code == "D60":
        # Traditional Parashara "from sign" variant. Other D60 variants exist
        # and must not be conflated with this explicit method.
        return (sign_index + segment) % 12

    raise ValueError(f"Unsupported equal-division varga: {code}")


def varga_amsa(longitude: float, code: str, profile: VargaProfile = "parashara_traditional") -> AmsaResult:
    """Map an exact sidereal longitude into one classical Shodashavarga."""

    if code not in SPEC_BY_CODE:
        raise ValueError(f"Unsupported Shodashavarga code: {code}")

    spec = SPEC_BY_CODE[code]
    longitude %= 360.0
    sign_index = int(longitude // 30.0)
    sign_degree = longitude % 30.0

    if code == "D30":
        target, segment, start, end, varga_degree, boundary = _d30_amsa(sign_index, sign_degree)
        return AmsaResult(
            sign_index=target,
            varga_degree=varga_degree,
            amsa_index=segment + 1,
            source_sign_degree=sign_degree,
            amsa_start_degree=start,
            amsa_end_degree=end,
            boundary_distance_arcminutes=boundary,
        )

    if code == "D1":
        segment, start, end, varga_degree, boundary = _equal_amsa(sign_degree, 1)
    else:
        index_degree: float | None = None
        if code == "D7" and profile == "astrosage_reference_compat_v1":
            # Empirical compatibility rule: two public AstroSage Brihat reports
            # are reproduced when the within-sign degree is truncated to its
            # integer part before selecting the D7 amsa. This is NOT the
            # classical default and is exposed only as a named compatibility
            # profile.
            index_degree = float(int(sign_degree))
        segment, start, end, varga_degree, boundary = _equal_amsa(
            sign_degree,
            spec.division,
            index_degree=index_degree,
        )

    target = _target_for_equal_varga(sign_index, segment, code)
    return AmsaResult(
        sign_index=target,
        varga_degree=varga_degree,
        amsa_index=segment + 1,
        source_sign_degree=sign_degree,
        amsa_start_degree=start,
        amsa_end_degree=end,
        boundary_distance_arcminutes=boundary,
    )



def _varga_sign_and_degree(longitude: float, division: int, method: str) -> tuple[int, float]:
    """Compatibility shim for the v0.2/v0.3 D1/D9/D10 internal helper."""
    expected = f"D{division}"
    if method != expected or method not in {"D1", "D9", "D10"}:
        raise ValueError(f"Unsupported legacy varga request: division={division}, method={method}")
    result = varga_amsa(longitude, method, "parashara_traditional")
    return result.sign_index, result.varga_degree

def _methodology_for(code: str, profile: VargaProfile) -> str:
    if code == "D7" and profile == "astrosage_reference_compat_v1":
        return ASTROSAGE_D7_COMPAT_METHODOLOGY
    return PARASHARA_METHODOLOGY


def _build_chart(
    spec: VargaSpec,
    ascendant: AngularPoint,
    planets: list[PlanetPosition],
    profile: VargaProfile,
) -> VargaChart:
    asc = varga_amsa(ascendant.longitude_sidereal, spec.code, profile)
    placements: list[VargaPlacement] = []

    for planet in planets:
        amsa = varga_amsa(planet.longitude_sidereal, spec.code, profile)
        placements.append(
            VargaPlacement(
                body=planet.body,
                sign_index=amsa.sign_index,
                sign=SIGNS[amsa.sign_index],
                house=((amsa.sign_index - asc.sign_index) % 12) + 1,
                varga_degree=amsa.varga_degree,
                dms=_dms(amsa.varga_degree),
                amsa_index=amsa.amsa_index,
                source_sign_degree=amsa.source_sign_degree,
                amsa_start_degree=amsa.amsa_start_degree,
                amsa_end_degree=amsa.amsa_end_degree,
                boundary_distance_arcminutes=amsa.boundary_distance_arcminutes,
            )
        )

    sensitivity_note = None
    if spec.code == "D60":
        sensitivity_note = (
            "D60 uses 0.5° source segments and is highly sensitive to birth-time "
            "accuracy, especially for the Ascendant."
        )

    return VargaChart(
        varga=spec.code,
        division=spec.division,
        name=spec.name,
        methodology=_methodology_for(spec.code, profile),
        ascendant_sign_index=asc.sign_index,
        ascendant_sign=SIGNS[asc.sign_index],
        ascendant_degree=asc.varga_degree,
        ascendant_dms=_dms(asc.varga_degree),
        ascendant_amsa_index=asc.amsa_index,
        ascendant_boundary_distance_arcminutes=asc.boundary_distance_arcminutes,
        placements=placements,
        sensitivity_note=sensitivity_note,
    )


def calculate_shodashavarga(
    ascendant: AngularPoint,
    planets: list[PlanetPosition],
    profile: VargaProfile = "parashara_traditional",
) -> list[VargaChart]:
    return [
        _build_chart(spec, ascendant, planets, profile)
        for spec in SHODASHAVARGA_SPECS
    ]


def calculate_core_vargas(
    ascendant: AngularPoint,
    planets: list[PlanetPosition],
    profile: VargaProfile = "parashara_traditional",
) -> list[VargaChart]:
    """Backward-compatible convenience subset used by early v0.2/v0.3 callers."""

    wanted = {"D1", "D9", "D10"}
    return [
        _build_chart(spec, ascendant, planets, profile)
        for spec in SHODASHAVARGA_SPECS
        if spec.code in wanted
    ]
