from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field

EphemerisPolicy = Literal["strict_swiss", "allow_moshier"]
NodeModel = Literal["mean", "true"]
VargaProfile = Literal["parashara_traditional", "astrosage_reference_compat_v1"]
AuditStatus = Literal[
    "COMPUTED", "UNIT_TESTED", "REFERENCE_MATCHED", "CROSS_VERIFIED",
    "DERIVED", "WARNING", "NOT_COMPUTED",
]


class BirthData(BaseModel):
    name: str | None = None
    place_name: str | None = None
    date_of_birth: date
    time_of_birth: time
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    elevation_m: float = Field(default=0.0, ge=-500.0, le=9000.0)
    timezone: str
    timezone_fold: Literal[0, 1] | None = None
    ayanamsa: Literal["lahiri"] = "lahiri"
    node_model: NodeModel = "mean"
    ephemeris_policy: EphemerisPolicy = "strict_swiss"
    include_outer_planets: bool = False
    dasha_year_days: float = Field(default=365.25, gt=365.0, lt=366.0)
    varga_profile: VargaProfile = "parashara_traditional"
    birth_time_uncertainty_seconds: float | None = Field(default=None, ge=0.0)


class DMS(BaseModel):
    degrees: int
    minutes: int
    seconds: float
    text: str


class ZodiacPoint(BaseModel):
    longitude_sidereal: float
    sign_index: int
    sign: str
    sign_degree: float
    dms: DMS
    nakshatra_index: int
    nakshatra: str
    pada: int
    nakshatra_lord: str


class PlanetPosition(ZodiacPoint):
    body: str
    body_id: int
    longitude_tropical: float
    latitude_ecliptic: float
    distance_au: float
    speed_longitude: float
    retrograde: bool
    classical: bool = True
    ephemeris_backend: Literal["swiss", "jpl", "moshier", "analytic"]


class AngularPoint(ZodiacPoint):
    label: str


class WholeSignHouse(BaseModel):
    house: int
    sign_index: int
    sign: str
    planets: list[str]


class HouseCusp(BaseModel):
    house: int
    longitude_sidereal: float
    sign_index: int
    sign: str
    sign_degree: float
    dms: DMS


class VargaPlacement(BaseModel):
    body: str
    sign_index: int
    sign: str
    house: int
    varga_degree: float
    dms: DMS
    amsa_index: int
    source_sign_degree: float
    amsa_start_degree: float
    amsa_end_degree: float
    boundary_distance_arcminutes: float


class VargaChart(BaseModel):
    varga: str
    division: int
    name: str
    methodology: str
    ascendant_sign_index: int
    ascendant_sign: str
    ascendant_degree: float
    ascendant_dms: DMS
    ascendant_amsa_index: int
    ascendant_boundary_distance_arcminutes: float
    placements: list[VargaPlacement]
    sensitivity_note: str | None = None


class Panchanga(BaseModel):
    weekday: str
    civil_weekday: str
    sunrise_local: datetime | None = None
    sunset_local: datetime | None = None
    day_duration_seconds: float | None = None
    birth_before_sunrise: bool | None = None
    tithi_number: int
    tithi_name: str
    paksha: Literal["Shukla", "Krishna"]
    karana: str
    yoga_number: int
    yoga_name: str
    moon_rashi: str
    moon_nakshatra: str
    moon_pada: int


class DashaBalance(BaseModel):
    lord: str
    years: int
    months: int
    days: int
    remaining_fraction: float


class DashaPeriod(BaseModel):
    level: Literal["MD", "AD"]
    lord: str
    start: datetime
    end: datetime
    parent_lord: str | None = None
    partial_at_birth: bool = False


class VimshottariDasha(BaseModel):
    birth_nakshatra: str
    birth_nakshatra_lord: str
    year_days: float
    balance_at_birth: DashaBalance
    mahadashas: list[DashaPeriod]
    antardashas: list[DashaPeriod]


class CalculationMetadata(BaseModel):
    calculation_fingerprint: str
    julian_day_ut: float
    utc_datetime: str
    local_datetime: str
    utc_offset_seconds: int
    ayanamsa: str
    ayanamsa_degrees: float
    node_model: str
    ephemeris_library: str = "Swiss Ephemeris"
    ephemeris_library_version: str
    actual_ephemeris_backend: str
    ephemeris_policy: EphemerisPolicy
    zodiac: str = "sidereal"
    parashari_house_system: str = "whole_sign"
    secondary_cusp_system: str = "placidus"
    coordinate_frame: str = "apparent geocentric ecliptic of date"
    civil_time_source: str = "IANA tzdata"
    calendar: str = "proleptic_gregorian"
    varga_profile: VargaProfile = "parashara_traditional"


class AuditItem(BaseModel):
    code: str
    status: AuditStatus
    message: str


class ChartResponse(BaseModel):
    input: BirthData
    metadata: CalculationMetadata
    ascendant: AngularPoint
    midheaven: AngularPoint
    planets: list[PlanetPosition]
    whole_sign_houses: list[WholeSignHouse]
    placidus_cusps: list[HouseCusp]
    panchanga: Panchanga
    vargas: list[VargaChart]
    shodashavarga: list[VargaChart]
    vimshottari: VimshottariDasha
    audit: list[AuditItem]
