from __future__ import annotations

import os
from datetime import datetime, time, timedelta, timezone
from threading import RLock
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

from astai.engine.constants import (
    NAKSHATRAS,
    NAKSHATRA_SPAN,
    PADA_SPAN,
    SIGNS,
    VIMSHOTTARI_LORDS,
)
from astai.models import (
    AngularPoint,
    BirthData,
    DMS,
    HouseCusp,
    PlanetPosition,
    WholeSignHouse,
    ZodiacPoint,
)

_SWE_LOCK = RLock()

CLASSICAL_PLANETS = (
    ("Sun", swe.SUN),
    ("Moon", swe.MOON),
    ("Mars", swe.MARS),
    ("Mercury", swe.MERCURY),
    ("Jupiter", swe.JUPITER),
    ("Venus", swe.VENUS),
    ("Saturn", swe.SATURN),
)

OUTER_PLANETS = (
    ("Uranus", swe.URANUS),
    ("Neptune", swe.NEPTUNE),
    ("Pluto", swe.PLUTO),
)


class EphemerisUnavailableError(RuntimeError):
    """Raised when strict mode cannot use a Swiss/JPL ephemeris backend."""


def _dms(degrees_within_sign: float) -> DMS:
    """Convert a within-sign angle to display-safe DMS.

    Values are quantized to centiseconds for display only. Raw longitudes remain
    unrounded elsewhere. Clamping prevents an impossible 30°00′00″ display
    inside the current sign when a value lies just below the next sign boundary.
    """

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


def zodiac_point(longitude: float) -> ZodiacPoint:
    """Map a sidereal longitude to sign, Nakshatra, Pada and star lord."""

    longitude %= 360.0
    sign_index = min(int(longitude // 30.0), 11)
    nakshatra_index = min(int(longitude // NAKSHATRA_SPAN), 26)
    offset = longitude - nakshatra_index * NAKSHATRA_SPAN
    pada = min(int(offset // PADA_SPAN) + 1, 4)

    return ZodiacPoint(
        longitude_sidereal=longitude,
        sign_index=sign_index,
        sign=SIGNS[sign_index],
        sign_degree=longitude % 30.0,
        dms=_dms(longitude % 30.0),
        nakshatra_index=nakshatra_index,
        nakshatra=NAKSHATRAS[nakshatra_index],
        pada=pada,
        nakshatra_lord=VIMSHOTTARI_LORDS[nakshatra_index % 9],
    )


def _resolve_local_datetime(data: BirthData) -> datetime:
    """Resolve historical local civil time without guessing DST ambiguity."""

    try:
        tz = ZoneInfo(data.timezone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown IANA timezone: {data.timezone}") from exc

    naive = datetime.combine(data.date_of_birth, data.time_of_birth)
    candidates: list[datetime] = []

    for fold in (0, 1):
        local = naive.replace(tzinfo=tz, fold=fold)
        round_trip = local.astimezone(timezone.utc).astimezone(tz)
        if round_trip.replace(tzinfo=None) == naive and round_trip.fold == fold:
            candidates.append(local)

    unique_utc = {candidate.astimezone(timezone.utc) for candidate in candidates}

    if not unique_utc:
        raise ValueError(
            "The supplied local civil time does not exist in the IANA timezone "
            "(DST gap). Provide a valid historical civil time."
        )

    if len(unique_utc) > 1:
        if data.timezone_fold is None:
            raise ValueError(
                "The supplied local civil time is DST-ambiguous. "
                "Set timezone_fold to 0 or 1 explicitly."
            )
        return naive.replace(tzinfo=tz, fold=data.timezone_fold)

    return candidates[0]


def _julian_day_ut(utc_dt: datetime) -> float:
    hour = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + utc_dt.microsecond / 3_600_000_000.0
    )
    return swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        hour,
        swe.GREG_CAL,
    )


def _backend_from_flags(retflags: int) -> str:
    if retflags & swe.FLG_JPLEPH:
        return "jpl"
    if retflags & swe.FLG_SWIEPH:
        return "swiss"
    if retflags & swe.FLG_MOSEPH:
        return "moshier"
    raise RuntimeError(f"Unknown Swiss Ephemeris backend flags: {retflags}")


def _configure_ephemeris() -> None:
    ephemeris_path = os.getenv("ASTAI_EPHE_PATH")
    if ephemeris_path:
        swe.set_ephe_path(ephemeris_path)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0.0, 0.0)


def _calc_body(
    jd_ut: float,
    name: str,
    body_id: int,
    policy: str,
    classical: bool,
    analytic: bool = False,
) -> PlanetPosition:
    """Calculate tropical and Lahiri-sidereal apparent geocentric positions."""

    base_flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    tropical, tropical_retflags = swe.calc_ut(jd_ut, body_id, base_flags)
    sidereal, sidereal_retflags = swe.calc_ut(
        jd_ut,
        body_id,
        base_flags | swe.FLG_SIDEREAL,
    )

    backend_tropical = _backend_from_flags(tropical_retflags)
    backend_sidereal = _backend_from_flags(sidereal_retflags)
    if backend_tropical != backend_sidereal:
        raise RuntimeError(
            "Tropical and sidereal calculations used different ephemeris backends"
        )

    backend = "analytic" if analytic else backend_sidereal
    if (
        policy == "strict_swiss"
        and not analytic
        and backend not in {"swiss", "jpl"}
    ):
        raise EphemerisUnavailableError(
            "Strict ephemeris policy requires Swiss/JPL ephemeris files, but "
            "the runtime fell back to Moshier. Set ASTAI_EPHE_PATH to a "
            "verified Swiss Ephemeris data directory."
        )

    point = zodiac_point(sidereal[0])
    return PlanetPosition(
        **point.model_dump(),
        body=name,
        body_id=body_id,
        longitude_tropical=tropical[0] % 360.0,
        latitude_ecliptic=sidereal[1],
        distance_au=sidereal[2],
        speed_longitude=sidereal[3],
        retrograde=sidereal[3] < 0.0,
        classical=classical,
        ephemeris_backend=backend,
    )


def _jd_to_utc_datetime(jd_ut: float) -> datetime:
    year, month, day, hour_float = swe.revjul(jd_ut, swe.GREG_CAL)
    total_microseconds = int(round(hour_float * 3_600_000_000.0))
    day_microseconds = 24 * 3_600_000_000

    if total_microseconds >= day_microseconds:
        base = datetime(year, month, day, tzinfo=timezone.utc) + timedelta(days=1)
        total_microseconds -= day_microseconds
    else:
        base = datetime(year, month, day, tzinfo=timezone.utc)

    return base + timedelta(microseconds=total_microseconds)


def _solar_event_for_local_date(
    local_dt: datetime,
    data: BirthData,
    event_flag: int,
) -> datetime | None:
    """Calculate apparent sunrise/sunset for the local civil date."""

    tz = local_dt.tzinfo
    if tz is None:
        raise ValueError("Local datetime must be timezone-aware")

    local_midnight = datetime.combine(local_dt.date(), time.min, tzinfo=tz)
    jd_start = _julian_day_ut(local_midnight.astimezone(timezone.utc))

    result, event_times = swe.rise_trans(
        jd_start,
        swe.SUN,
        event_flag,
        (data.longitude, data.latitude, data.elevation_m),
        0.0,
        15.0,
        swe.FLG_SWIEPH,
    )

    # Swiss Ephemeris returns -2 when the requested rise/set does not occur.
    if result == -2:
        return None

    return _jd_to_utc_datetime(event_times[0]).astimezone(tz)


def _build_placidus_cusps(
    jd_ut: float,
    latitude: float,
    longitude: float,
) -> list[HouseCusp]:
    raw_cusps, _ = swe.houses_ex(
        jd_ut,
        latitude,
        longitude,
        b"P",
        swe.FLG_SIDEREAL,
    )

    cusps: list[HouseCusp] = []
    for house_number, cusp_longitude in enumerate(raw_cusps, start=1):
        point = zodiac_point(cusp_longitude)
        cusps.append(
            HouseCusp(
                house=house_number,
                longitude_sidereal=point.longitude_sidereal,
                sign_index=point.sign_index,
                sign=point.sign,
                sign_degree=point.sign_degree,
                dms=point.dms,
            )
        )
    return cusps


def _build_whole_sign_houses(
    ascendant: AngularPoint,
    planets: list[PlanetPosition],
) -> list[WholeSignHouse]:
    houses: list[WholeSignHouse] = []
    for house_number in range(1, 13):
        sign_index = (ascendant.sign_index + house_number - 1) % 12
        occupants = [
            planet.body for planet in planets if planet.sign_index == sign_index
        ]
        houses.append(
            WholeSignHouse(
                house=house_number,
                sign_index=sign_index,
                sign=SIGNS[sign_index],
                planets=occupants,
            )
        )
    return houses


def calculate_astronomy(data: BirthData) -> dict:
    """Calculate the canonical astronomical basis under one Swiss Ephemeris lock."""

    with _SWE_LOCK:
        _configure_ephemeris()

        local_dt = _resolve_local_datetime(data)
        utc_dt = local_dt.astimezone(timezone.utc)
        jd_ut = _julian_day_ut(utc_dt)

        planets = [
            _calc_body(
                jd_ut,
                name,
                body_id,
                data.ephemeris_policy,
                classical=True,
            )
            for name, body_id in CLASSICAL_PLANETS
        ]

        if data.include_outer_planets:
            planets.extend(
                _calc_body(
                    jd_ut,
                    name,
                    body_id,
                    data.ephemeris_policy,
                    classical=False,
                )
                for name, body_id in OUTER_PLANETS
            )

        node_id = swe.MEAN_NODE if data.node_model == "mean" else swe.TRUE_NODE
        rahu = _calc_body(
            jd_ut,
            "Rahu",
            node_id,
            data.ephemeris_policy,
            classical=True,
            analytic=data.node_model == "mean",
        )
        planets.append(rahu)

        ketu_point = zodiac_point((rahu.longitude_sidereal + 180.0) % 360.0)
        planets.append(
            PlanetPosition(
                **ketu_point.model_dump(),
                body="Ketu",
                body_id=node_id,
                longitude_tropical=(rahu.longitude_tropical + 180.0) % 360.0,
                latitude_ecliptic=-rahu.latitude_ecliptic,
                distance_au=rahu.distance_au,
                speed_longitude=rahu.speed_longitude,
                retrograde=rahu.retrograde,
                classical=True,
                ephemeris_backend=(
                    "analytic" if data.node_model == "mean" else rahu.ephemeris_backend
                ),
            )
        )

        _, ascmc = swe.houses_ex(
            jd_ut,
            data.latitude,
            data.longitude,
            b"W",
            swe.FLG_SIDEREAL,
        )
        ascendant = AngularPoint(
            **zodiac_point(ascmc[0]).model_dump(),
            label="Ascendant",
        )
        midheaven = AngularPoint(
            **zodiac_point(ascmc[1]).model_dump(),
            label="Midheaven",
        )

        placidus_cusps = _build_placidus_cusps(
            jd_ut,
            data.latitude,
            data.longitude,
        )
        whole_sign_houses = _build_whole_sign_houses(ascendant, planets)

        sunrise_local = _solar_event_for_local_date(local_dt, data, swe.CALC_RISE)
        sunset_local = _solar_event_for_local_date(local_dt, data, swe.CALC_SET)

        _, ayanamsa_value = swe.get_ayanamsa_ex_ut(jd_ut, swe.FLG_SWIEPH)

        physical_backends = {
            planet.ephemeris_backend
            for planet in planets
            if planet.ephemeris_backend != "analytic"
        }
        if len(physical_backends) != 1:
            raise RuntimeError(
                "Mixed physical ephemeris backends detected: "
                f"{sorted(physical_backends)}"
            )

        return {
            "local_dt": local_dt,
            "utc_dt": utc_dt,
            "jd_ut": jd_ut,
            "ayanamsa_degrees": ayanamsa_value,
            "actual_backend": next(iter(physical_backends)),
            "ascendant": ascendant,
            "midheaven": midheaven,
            "planets": planets,
            "whole_sign_houses": whole_sign_houses,
            "placidus_cusps": placidus_cusps,
            "sunrise_local": sunrise_local,
            "sunset_local": sunset_local,
        }
