from __future__ import annotations

from astai.engine.astronomy import _dms
from astai.engine.constants import SIGNS
from astai.models import AngularPoint, PlanetPosition, VargaChart, VargaPlacement


def _varga_sign_and_degree(longitude: float, division: int, method: str) -> tuple[int, float]:
    longitude %= 360.0
    sign_index = int(longitude // 30.0)
    sign_degree = longitude % 30.0
    segment_size = 30.0 / division
    segment = min(int(sign_degree // segment_size), division - 1)
    degree_in_segment = sign_degree - segment * segment_size
    varga_degree = degree_in_segment * division

    if method == "D1":
        return sign_index, sign_degree
    if method == "D9":
        modality = sign_index % 3
        if modality == 0:
            start = sign_index
        elif modality == 1:
            start = (sign_index + 8) % 12
        else:
            start = (sign_index + 4) % 12
        return (start + segment) % 12, varga_degree
    if method == "D10":
        start = sign_index if sign_index % 2 == 0 else (sign_index + 8) % 12
        return (start + segment) % 12, varga_degree
    raise ValueError(f"Unsupported varga method: {method}")


def _build_chart(label: str, division: int, ascendant: AngularPoint, planets: list[PlanetPosition]) -> VargaChart:
    asc_sign, asc_degree = _varga_sign_and_degree(ascendant.longitude_sidereal, division, label)
    placements = []
    for planet in planets:
        sign_index, varga_degree = _varga_sign_and_degree(planet.longitude_sidereal, division, label)
        placements.append(
            VargaPlacement(
                body=planet.body,
                sign_index=sign_index,
                sign=SIGNS[sign_index],
                house=((sign_index - asc_sign) % 12) + 1,
                varga_degree=varga_degree,
                dms=_dms(varga_degree),
            )
        )
    return VargaChart(
        varga=label,
        ascendant_sign_index=asc_sign,
        ascendant_sign=SIGNS[asc_sign],
        ascendant_degree=asc_degree,
        placements=placements,
    )


def calculate_core_vargas(ascendant: AngularPoint, planets: list[PlanetPosition]) -> list[VargaChart]:
    return [
        _build_chart("D1", 1, ascendant, planets),
        _build_chart("D9", 9, ascendant, planets),
        _build_chart("D10", 10, ascendant, planets),
    ]
