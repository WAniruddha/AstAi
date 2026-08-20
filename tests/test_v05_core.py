from __future__ import annotations

from datetime import datetime, timezone

import swisseph as swe

from astai.engine.constants import NAKSHATRA_SPAN, SIGNS
from astai.engine.dasha import calculate_vimshottari
from astai.engine.houses import calculate_sripati_bhava
from astai.models import AngularPoint, DMS, HouseCusp, PlanetPosition


def _dms(value: float) -> DMS:
    value %= 30
    deg = int(value)
    rem = (value - deg) * 60
    minute = int(rem)
    sec = (rem - minute) * 60
    return DMS(degrees=deg, minutes=minute, seconds=sec, text="")


def _zodiac_fields(longitude: float, nak_index: int | None = None, lord: str = "Ketu") -> dict:
    longitude %= 360
    sign_index = int(longitude // 30)
    if nak_index is None:
        nak_index = min(int(longitude // NAKSHATRA_SPAN), 26)
    return {
        "longitude_sidereal": longitude,
        "sign_index": sign_index,
        "sign": SIGNS[sign_index],
        "sign_degree": longitude % 30,
        "dms": _dms(longitude),
        "nakshatra_index": nak_index,
        "nakshatra": "Test",
        "pada": 1,
        "nakshatra_lord": lord,
    }


def _planet(body: str, longitude: float, nak_index: int | None = None, lord: str = "Ketu") -> PlanetPosition:
    return PlanetPosition(
        **_zodiac_fields(longitude, nak_index, lord),
        body=body,
        body_id=0,
        longitude_tropical=longitude,
        latitude_ecliptic=0,
        distance_au=1,
        speed_longitude=0,
        retrograde=False,
        classical=True,
        ephemeris_backend="moshier",
    )


def _asc(longitude: float) -> AngularPoint:
    return AngularPoint(**_zodiac_fields(longitude), label="Ascendant")


def _cusps(values) -> list[HouseCusp]:
    out = []
    for i, longitude in enumerate(values, start=1):
        sign_index = int((longitude % 360) // 30)
        out.append(HouseCusp(
            house=i,
            longitude_sidereal=longitude % 360,
            sign_index=sign_index,
            sign=SIGNS[sign_index],
            sign_degree=longitude % 30,
            dms=_dms(longitude),
        ))
    return out


def test_sripati_derivation_matches_native_swiss_to_machine_precision():
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd = swe.julday(1979, 8, 23, 18 + 23 / 60 + 18 / 3600, swe.GREG_CAL)
    por, _ = swe.houses_ex(jd, 28.6666666667, 77.2166666667, b"O", swe.FLG_SIDEREAL)
    sri, _ = swe.houses_ex(jd, 28.6666666667, 77.2166666667, b"S", swe.FLG_SIDEREAL)
    result = calculate_sripati_bhava(_asc(por[0]), [], _cusps(por), _cusps(sri))
    assert result.swiss_sripati_crosscheck_max_arcseconds < 1e-6
    assert abs(result.houses[0].madhya_longitude_sidereal - por[0]) < 1e-12
    assert abs(result.houses[9].madhya_longitude_sidereal - por[9]) < 1e-12
    assert abs(sum(h.span_degrees for h in result.houses) - 360) < 1e-9


def test_sripati_chalit_changes_house_not_rasi_sign():
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd = swe.julday(1979, 8, 23, 18 + 23 / 60 + 18 / 3600, swe.GREG_CAL)
    por, _ = swe.houses_ex(jd, 28.6666666667, 77.2166666667, b"O", swe.FLG_SIDEREAL)
    sri, _ = swe.houses_ex(jd, 28.6666666667, 77.2166666667, b"S", swe.FLG_SIDEREAL)
    planets = [
        _planet("Moon", 137.8173145406078),
        _planet("Mercury", 108.90848945045316),
        _planet("Jupiter", 118.73725670899658),
        _planet("Saturn", 141.46365870731447),
    ]
    result = calculate_sripati_bhava(_asc(por[0]), planets, _cusps(por), _cusps(sri))
    shifts = {
        p.body: (p.rasi_house, p.bhava_house, p.rasi_sign, p.shifted)
        for p in result.placements
    }
    assert shifts["Moon"][:2] == (4, 5)
    assert shifts["Mercury"][:2] == (3, 4)
    assert shifts["Jupiter"][:2] == (3, 4)
    assert shifts["Saturn"][:2] == (4, 5)
    assert all(x[3] for x in shifts.values())
    assert shifts["Moon"][2] == "Leo"


def test_sripati_boundary_is_half_open_and_belongs_to_incoming_house():
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd = swe.julday(1979, 8, 23, 18 + 23 / 60 + 18 / 3600, swe.GREG_CAL)
    por, _ = swe.houses_ex(jd, 28.6666666667, 77.2166666667, b"O", swe.FLG_SIDEREAL)
    sri, _ = swe.houses_ex(jd, 28.6666666667, 77.2166666667, b"S", swe.FLG_SIDEREAL)
    p = _planet("Boundary", sri[1])
    result = calculate_sripati_bhava(_asc(por[0]), [p], _cusps(por), _cusps(sri))
    placement = result.placements[0]
    assert placement.bhava_house == 2
    assert result.boundary_policy.startswith("half_open_[start,end)")


def test_vimshottari_exact_nakshatra_start_has_full_ketu_balance_and_five_level_path():
    birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
    moon = _planet("Moon", 0.0, nak_index=0, lord="Ketu")
    result = calculate_vimshottari(birth, [moon])
    assert (
        result.balance_at_birth.years,
        result.balance_at_birth.months,
        result.balance_at_birth.days,
    ) == (7, 0, 0)
    assert [p.level for p in result.birth_timing_path] == ["MD", "AD", "PD", "SD", "PRANA"]
    assert [p.lord for p in result.birth_timing_path] == ["Ketu"] * 5
    assert result.mahadashas[0].start == birth
    assert result.mahadashas[0].theoretical_start == birth


def test_vimshottari_partial_birth_covers_full_120_year_horizon_and_repeats_start_lord():
    birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
    moon = _planet("Moon", NAKSHATRA_SPAN / 2, nak_index=0, lord="Ketu")
    result = calculate_vimshottari(birth, [moon])
    assert result.mahadashas[0].lord == "Ketu"
    assert result.mahadashas[0].partial_at_birth
    assert result.mahadashas[-1].lord == "Ketu"
    assert len(result.mahadashas) == 10
    assert result.mahadashas[-1].end >= result.coverage_end


def test_vimshottari_ad_and_pd_close_exactly_to_parent_boundaries():
    birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
    moon = _planet("Moon", 0.0, nak_index=0, lord="Ketu")
    result = calculate_vimshottari(birth, [moon])
    md = result.mahadashas[0]
    ads = [p for p in result.antardashas if p.parent_path == ["Ketu"]]
    assert len(ads) == 9
    assert ads[0].start == md.start
    assert ads[-1].end == md.end
    assert all(a.end == b.start for a, b in zip(ads, ads[1:]))

    first_ad = ads[0]
    pds = [p for p in result.pratyantardashas if p.parent_path == ["Ketu", "Ketu"]]
    assert len(pds) == 9
    assert pds[0].start == first_ad.start
    assert pds[-1].end == first_ad.end
    assert all(a.end == b.start for a, b in zip(pds, pds[1:]))
