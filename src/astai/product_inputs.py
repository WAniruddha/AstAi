from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import date
from typing import Mapping

from astai.models import BirthData, VargaProfile

MIN_BIRTH_DATE = date(1900, 1, 1)

D7_METHOD_OPTIONS: tuple[tuple[str, VargaProfile], ...] = (
    ("Exact Parashari (default)", "parashara_traditional"),
    ("AstroSage D7 published-table compatibility", "astrosage_reference_compat_v1"),
)


@dataclass(frozen=True)
class EphemerisRuntime:
    policy: str
    mode: str
    ephemeris_path: str | None
    user_message: str


def birth_date_bounds(today: date | None = None) -> tuple[date, date]:
    """Return explicit UI DOB bounds instead of Streamlit's narrow defaults."""

    return MIN_BIRTH_DATE, today or date.today()


def resolve_ephemeris_runtime(
    environ: Mapping[str, str] | None = None,
) -> EphemerisRuntime:
    """Choose a safe calculator policy without asking end users about backends.

    A configured Swiss Ephemeris data path enables strict production mode.
    Otherwise local development allows the audited Moshier fallback so the UI
    remains usable. The actual backend is still recorded in chart metadata.
    """

    env = os.environ if environ is None else environ
    raw_path = env.get("ASTAI_EPHE_PATH")
    path = raw_path.strip() if raw_path and raw_path.strip() else None

    if path:
        return EphemerisRuntime(
            policy="strict_swiss",
            mode="production",
            ephemeris_path=path,
            user_message="Professional ephemeris mode: verified Swiss/JPL data path configured.",
        )

    return EphemerisRuntime(
        policy="allow_moshier",
        mode="development",
        ephemeris_path=None,
        user_message=(
            "Local development mode: Swiss Ephemeris data files are not configured, "
            "so AstAi may use the audited Moshier fallback. Production validation "
            "should configure ASTAI_EPHE_PATH."
        ),
    )


def calculation_request_signature(data: BirthData) -> str:
    """Hash only calculation-driving chart inputs for Streamlit state tracking."""

    payload = data.model_dump(mode="json")
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def d7_profile_from_label(label: str) -> VargaProfile:
    """Translate the explicit product label into the frozen internal profile."""

    for option_label, profile in D7_METHOD_OPTIONS:
        if option_label == label:
            return profile
    raise ValueError(f"Unknown D7 method label: {label}")


def d7_profile_label(profile: VargaProfile) -> str:
    """Return the user-facing label for one frozen D7 profile."""

    for label, option_profile in D7_METHOD_OPTIONS:
        if option_profile == profile:
            return label
    raise ValueError(f"Unknown D7 profile: {profile}")
