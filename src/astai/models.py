from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field

EphemerisPolicy = Literal["strict_swiss", "allow_moshier"]
NodeModel = Literal["mean", "true"]
VargaProfile = Literal["parashara_traditional", "astrosage_reference_compat_v1"]
BhavaMethod = Literal["sripati"]
DashaLevel = Literal["MD", "AD", "PD", "SD", "PRANA"]
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
    bhava_method: BhavaMethod = "sripati"
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


class BhavaHouse(BaseModel):
    house: int
    start_longitude_sidereal: float
    start_sign: str
    start_dms: DMS
    madhya_longitude_sidereal: float
    madhya_sign: str
    madhya_dms: DMS
    end_longitude_sidereal: float
    end_sign: str
    end_dms: DMS
    span_degrees: float
    planets: list[str]


class BhavaChalitPlacement(BaseModel):
    body: str
    longitude_sidereal: float
    rasi_sign: str
    rasi_house: int
    bhava_house: int
    shifted: bool


class BhavaChalit(BaseModel):
    methodology: str
    boundary_policy: str
    houses: list[BhavaHouse]
    placements: list[BhavaChalitPlacement]
    swiss_sripati_crosscheck_max_arcseconds: float


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
    level: DashaLevel
    lord: str
    start: datetime
    end: datetime
    parent_lord: str | None = None
    parent_path: list[str] = Field(default_factory=list)
    theoretical_start: datetime | None = None
    partial_at_birth: bool = False


class VimshottariDasha(BaseModel):
    birth_nakshatra: str
    birth_nakshatra_lord: str
    year_days: float
    methodology: str = "vimshottari_120_v1"
    balance_at_birth: DashaBalance
    mahadashas: list[DashaPeriod]
    antardashas: list[DashaPeriod]
    pratyantardashas: list[DashaPeriod] = Field(default_factory=list)
    birth_timing_path: list[DashaPeriod] = Field(default_factory=list)
    coverage_end: datetime | None = None


class AshtakavargaContribution(BaseModel):
    contributor: str
    points_by_sign: list[int]
    total: int


class Bhinnashtakavarga(BaseModel):
    planet: str
    points_by_sign: list[int]
    total: int
    prastara: list[AshtakavargaContribution]


class Ashtakavarga(BaseModel):
    methodology: str = "classical_raw_ashtakavarga_v1"
    sign_order: list[str]
    point_semantics: str = "1 = benefic support; 0 = no benefic support"
    reduction_status: Literal["unreduced"] = "unreduced"
    bhinna: list[Bhinnashtakavarga]
    sarva_points_by_sign: list[int]
    sarva_total: int


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
    parashari_bhava_system: BhavaMethod = "sripati"
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
    bhava_chalit: BhavaChalit
    placidus_cusps: list[HouseCusp]
    panchanga: Panchanga
    vargas: list[VargaChart]
    shodashavarga: list[VargaChart]
    vimshottari: VimshottariDasha
    ashtakavarga: Ashtakavarga
    audit: list[AuditItem]
