from __future__ import annotations

import os
from datetime import date, time

import streamlit as st

from astai.engine import calculate_chart
from astai.models import BirthData

st.set_page_config(page_title="AstAi Calculator", page_icon="🪐", layout="wide")
st.title("AstAi · Professional Kundali Calculator Lab")
st.caption(
    "Deterministic calculation first. Interpretation, RAG and LLM reasoning stay outside this layer."
)

has_ephe_path = bool(os.getenv("ASTAI_EPHE_PATH"))

with st.sidebar:
    st.header("Birth data")
    name = st.text_input("Name", value="")
    place_name = st.text_input("Place name", value="")
    dob = st.date_input("Date of birth", value=date(1990, 1, 1))
    tob = st.time_input("Time of birth", value=time(12, 0))
    latitude = st.number_input(
        "Latitude", min_value=-90.0, max_value=90.0, value=19.0760, format="%.6f"
    )
    longitude = st.number_input(
        "Longitude", min_value=-180.0, max_value=180.0, value=72.8777, format="%.6f"
    )
    elevation = st.number_input(
        "Elevation (m)", min_value=-500.0, max_value=9000.0, value=0.0, step=1.0
    )
    timezone_name = st.text_input("IANA timezone", value="Asia/Kolkata")
    node_model = st.selectbox("Rahu/Ketu model", ["mean", "true"], index=0)
    varga_profile = st.selectbox(
        "Varga profile",
        ["parashara_traditional", "astrosage_reference_compat_v1"],
        index=0,
        help=(
            "Use exact Parashari rules by default. AstroSage compatibility changes only D7 "
            "to reproduce two public reference tables and is explicitly audited."
        ),
    )
    birth_time_uncertainty = st.number_input(
        "Birth-time uncertainty ± seconds (optional)",
        min_value=0.0,
        value=None,
        step=1.0,
        help="Stored for sensitivity/audit. AstAi does not invent a confidence score.",
    )
    include_outer = st.checkbox("Include Uranus / Neptune / Pluto", value=False)
    strict = st.checkbox(
        "Strict Swiss/JPL ephemeris",
        value=has_ephe_path,
        help=(
            "Requires ASTAI_EPHE_PATH containing verified Swiss Ephemeris data files. "
            "If disabled, Moshier fallback is allowed but explicitly reported."
        ),
    )
    calculate = st.button("Calculate chart", type="primary", use_container_width=True)

if not has_ephe_path:
    st.warning(
        "ASTAI_EPHE_PATH is not configured in this runtime. Strict production calculations "
        "will refuse a silent Moshier fallback."
    )

if not calculate:
    st.info("Enter authoritative birth data in the sidebar, then calculate.")
    st.stop()

try:
    chart = calculate_chart(
        BirthData(
            name=name or None,
            place_name=place_name or None,
            date_of_birth=dob,
            time_of_birth=tob,
            latitude=latitude,
            longitude=longitude,
            elevation_m=elevation,
            timezone=timezone_name,
            node_model=node_model,
            varga_profile=varga_profile,
            birth_time_uncertainty_seconds=birth_time_uncertainty,
            include_outer_planets=include_outer,
            ephemeris_policy="strict_swiss" if strict else "allow_moshier",
        )
    )
except Exception as exc:
    st.error(f"Calculation failed: {exc}")
    st.stop()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Ascendant", f"{chart.ascendant.sign} {chart.ascendant.dms.text}")
m2.metric(
    "Moon",
    f"{chart.panchanga.moon_rashi} · {chart.panchanga.moon_nakshatra}-{chart.panchanga.moon_pada}",
)
m3.metric("Ayanamsa", f"{chart.metadata.ayanamsa_degrees:.8f}°")
m4.metric("Backend", chart.metadata.actual_ephemeris_backend.upper())

positions_tab, d1_tab, varga_tab, panchanga_tab, dasha_tab, cusps_tab, audit_tab = st.tabs(
    [
        "Planetary positions",
        "D1",
        "Shodashavarga",
        "Panchanga",
        "Vimshottari",
        "Placidus cusps",
        "Audit",
    ]
)

with positions_tab:
    st.dataframe(
        [
            {
                "Body": p.body,
                "Sign": p.sign,
                "DMS": p.dms.text,
                "Sidereal °": round(p.longitude_sidereal, 9),
                "Tropical °": round(p.longitude_tropical, 9),
                "Nakshatra": p.nakshatra,
                "Pada": p.pada,
                "Star Lord": p.nakshatra_lord,
                "Speed °/day": round(p.speed_longitude, 9),
                "Retrograde": p.retrograde,
                "Backend": p.ephemeris_backend,
            }
            for p in chart.planets
        ],
        use_container_width=True,
        hide_index=True,
    )

with d1_tab:
    st.dataframe(
        [
            {
                "House": h.house,
                "Sign": h.sign,
                "Planets": ", ".join(h.planets) if h.planets else "—",
            }
            for h in chart.whole_sign_houses
        ],
        use_container_width=True,
        hide_index=True,
    )

with varga_tab:
    codes = [v.varga for v in chart.shodashavarga]
    selected_code = st.selectbox("Select divisional chart", codes, index=codes.index("D9"))
    varga = next(v for v in chart.shodashavarga if v.varga == selected_code)
    st.subheader(f"{varga.varga} · {varga.name} · Ascendant {varga.ascendant_sign}")
    st.caption(f"Methodology: {varga.methodology}")
    if varga.sensitivity_note:
        st.warning(varga.sensitivity_note)
    st.dataframe(
        [
            {
                "Body": p.body,
                "Sign": p.sign,
                "House": p.house,
                "Amsa": p.amsa_index,
                "Varga degree": p.dms.text,
                "Nearest source boundary (arcmin)": round(p.boundary_distance_arcminutes, 4),
            }
            for p in varga.placements
        ],
        use_container_width=True,
        hide_index=True,
    )

with panchanga_tab:
    p = chart.panchanga
    c1, c2, c3 = st.columns(3)
    c1.metric("Hindu weekday", p.weekday)
    c2.metric("Sunrise", p.sunrise_local.strftime("%H:%M:%S") if p.sunrise_local else "Unavailable")
    c3.metric("Sunset", p.sunset_local.strftime("%H:%M:%S") if p.sunset_local else "Unavailable")
    st.write(
        {
            "Civil weekday": p.civil_weekday,
            "Birth before sunrise": p.birth_before_sunrise,
            "Tithi": f"{p.paksha} {p.tithi_name}",
            "Karana": p.karana,
            "Yoga": p.yoga_name,
            "Moon Rashi": p.moon_rashi,
            "Moon Nakshatra": f"{p.moon_nakshatra}-{p.moon_pada}",
        }
    )

with dasha_tab:
    balance = chart.vimshottari.balance_at_birth
    st.info(
        f"Balance at birth: {balance.lord} {balance.years}Y {balance.months}M {balance.days}D"
    )
    st.dataframe(
        [
            {
                "Lord": d.lord,
                "Start": d.start,
                "End": d.end,
                "Partial at birth": d.partial_at_birth,
            }
            for d in chart.vimshottari.mahadashas
        ],
        use_container_width=True,
        hide_index=True,
    )
    with st.expander("Antardashas"):
        st.dataframe(
            [
                {
                    "MD": d.parent_lord,
                    "AD": d.lord,
                    "Start": d.start,
                    "End": d.end,
                    "Partial at birth": d.partial_at_birth,
                }
                for d in chart.vimshottari.antardashas
            ],
            use_container_width=True,
            hide_index=True,
        )

with cusps_tab:
    st.caption(
        "These are Lahiri sidereal Placidus cusps. They are not Parashari whole-sign "
        "houses and are not yet the KP module."
    )
    st.dataframe(
        [
            {
                "House": c.house,
                "Sign": c.sign,
                "DMS": c.dms.text,
                "Longitude": round(c.longitude_sidereal, 9),
            }
            for c in chart.placidus_cusps
        ],
        use_container_width=True,
        hide_index=True,
    )

with audit_tab:
    for item in chart.audit:
        st.write(f"**{item.status} · {item.code}**: {item.message}")
    st.caption(
        f"UTC: {chart.metadata.utc_datetime} · Julian day UT: {chart.metadata.julian_day_ut:.9f}"
    )
    st.code(chart.metadata.calculation_fingerprint, language=None)
    with st.expander("Raw reusable chart JSON"):
        st.json(chart.model_dump(mode="json"))
