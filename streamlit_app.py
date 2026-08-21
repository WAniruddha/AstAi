from __future__ import annotations

from datetime import date, time

import streamlit as st

from astai.engine import calculate_chart
from astai.india_places import find_india_place, india_states, places_for_state
from astai.models import BirthData, ChartResponse
from astai.presentation import lagna_house_rows, planetary_position_rows
from astai.product_inputs import (
    D7_METHOD_OPTIONS,
    birth_date_bounds,
    calculation_request_signature,
    d7_profile_from_label,
    d7_profile_label,
    resolve_ephemeris_runtime,
)

st.set_page_config(page_title="AstAi Calculator", page_icon="🪐", layout="wide")
st.title("AstAi · Professional Kundali Calculator Lab")
st.caption(
    "India-first birth input. Deterministic calculation remains separate from interpretation and LLM reasoning."
)

runtime = resolve_ephemeris_runtime()
min_dob, max_dob = birth_date_bounds()
states = india_states()
default_state = "Maharashtra"
state_index = states.index(default_state) if default_state in states else 0


@st.cache_data(show_spinner=False, max_entries=64)
def _calculate_chart_cached(request_json: str, runtime_key: str) -> dict:
    """Cache deterministic chart results for repeated identical requests.

    runtime_key deliberately participates in the cache key so a production Swiss
    runtime can never reuse a development-mode Moshier result.
    """

    del runtime_key
    request = BirthData.model_validate_json(request_json)
    return calculate_chart(request).model_dump(mode="json")


def _runtime_cache_key() -> str:
    return f"{runtime.mode}|{runtime.policy}|{runtime.ephemeris_path or ''}"


@st.fragment
def _birth_controls() -> None:
    """Render calculation-driving inputs without rerunning the full result page."""

    st.header("Birth details")
    name = st.text_input("Name", value="")
    dob = st.date_input(
        "Date of birth",
        value=date(1990, 1, 1),
        min_value=min_dob,
        max_value=max_dob,
        format="DD/MM/YYYY",
        help=f"Supported range: {min_dob:%d/%m/%Y} to {max_dob:%d/%m/%Y}.",
    )
    tob = st.time_input(
        "Time of birth",
        value=time(12, 0, 0),
        step=1,
        help="Enter the recorded birth time as accurately as available, including seconds when known.",
    )

    st.subheader("Birth place")
    st.selectbox("Country", ["India"], index=0, disabled=True)
    state = st.selectbox("State / Union Territory", states, index=state_index)
    state_places = places_for_state(state)
    place_names = [place.name for place in state_places]
    default_place_index = (
        place_names.index("Pune")
        if state == "Maharashtra" and "Pune" in place_names
        else 0
    )
    place_name = st.selectbox(
        "City / town",
        place_names,
        index=default_place_index,
        key=f"birth_place_{state}",
        help="Type while this list is open to filter the built-in India place catalog.",
    )
    selected_place = find_india_place(state, place_name)

    st.caption(
        f"Selected: {selected_place.label}\n\n"
        f"City reference point: {selected_place.latitude:.6f}°, "
        f"{selected_place.longitude:.6f}° · {selected_place.timezone}"
    )

    exact_coordinates = st.checkbox(
        "Use exact birth coordinates (optional)",
        value=False,
        key=f"exact_coordinates_{state}_{place_name}",
        help=(
            "Leave this off to use the selected city's reference point. "
            "Turn it on only when you know a more precise birth location."
        ),
    )

    lat_col, lon_col = st.columns(2)
    latitude = lat_col.number_input(
        "Latitude",
        min_value=6.0,
        max_value=38.0,
        value=float(selected_place.latitude),
        step=0.000001,
        format="%.6f",
        disabled=not exact_coordinates,
        key=f"latitude_{state}_{place_name}",
        help="Decimal degrees, India-only product range.",
    )
    longitude = lon_col.number_input(
        "Longitude",
        min_value=68.0,
        max_value=98.0,
        value=float(selected_place.longitude),
        step=0.000001,
        format="%.6f",
        disabled=not exact_coordinates,
        key=f"longitude_{state}_{place_name}",
        help="Decimal degrees, India-only product range.",
    )
    elevation = st.number_input(
        "Elevation (m, optional)",
        min_value=-50.0,
        max_value=8600.0,
        value=0.0,
        step=1.0,
        format="%.1f",
        disabled=not exact_coordinates,
        key=f"elevation_{state}_{place_name}",
        help="Optional exact elevation. The default city calculation uses 0 m.",
    )
    timezone_name = selected_place.timezone
    st.caption(
        "The city reference coordinates are used automatically. "
        "Exact-coordinate override is optional."
    )

    with st.expander("Advanced calculation settings"):
        st.caption("Most users can leave these settings unchanged.")
        node_model = st.selectbox(
            "Rahu / Ketu model",
            ["mean", "true"],
            index=0,
            help=(
                "Mean and True Rahu/Ketu are different node models. "
                "Changing this setting requires recalculation."
            ),
        )
        d7_labels = [label for label, _ in D7_METHOD_OPTIONS]
        d7_method_label = st.selectbox(
            "D7 (Saptamsa) method",
            d7_labels,
            index=0,
            help=(
                "This affects D7 only. D1, D2, D9, D10 and the other Vargas "
                "remain on the frozen AstAi/Parashari formulas."
            ),
        )
        varga_profile = d7_profile_from_label(d7_method_label)
        birth_time_uncertainty = st.number_input(
            "Birth-time uncertainty ± seconds (optional)",
            min_value=0.0,
            value=None,
            step=1.0,
        )
        st.text_input("Parashari Bhava / Chalit", value="Sripati", disabled=True)
        st.text_input("Timezone", value=timezone_name, disabled=True)
        st.caption(
            "Uranus, Neptune and Pluto are always included as non-classical chart bodies. "
            "Traditional algorithms remain restricted to declared classical contributors."
        )
        st.caption(f"Runtime: {runtime.mode}. Ephemeris policy is selected automatically.")

    current_request = BirthData(
        name=name or None,
        place_name=selected_place.label,
        date_of_birth=dob,
        time_of_birth=tob,
        latitude=latitude,
        longitude=longitude,
        elevation_m=elevation,
        timezone=timezone_name,
        node_model=node_model,
        bhava_method="sripati",
        varga_profile=varga_profile,
        birth_time_uncertainty_seconds=birth_time_uncertainty,
        include_outer_planets=True,
        ephemeris_policy=runtime.policy,
    )
    current_signature = calculation_request_signature(current_request)
    st.session_state["astai_draft_signature"] = current_signature

    stored_chart = st.session_state.get("astai_chart")
    stored_signature = st.session_state.get("astai_chart_request_signature")
    if stored_chart is not None and stored_signature != current_signature:
        st.warning(
            "Changes are staged; the chart on the right is still the last calculated result. "
            "Click **Recalculate Kundali** to apply them."
        )

    button_label = "Recalculate Kundali" if stored_chart is not None else "Calculate Kundali"
    if st.button(button_label, type="primary", use_container_width=True):
        try:
            with st.spinner("Calculating Kundali…"):
                payload = _calculate_chart_cached(
                    current_request.model_dump_json(),
                    _runtime_cache_key(),
                )
                calculated_chart = ChartResponse.model_validate(payload)
        except Exception as exc:
            st.error(f"Calculation failed: {exc}")
        else:
            st.session_state["astai_chart"] = calculated_chart
            st.session_state["astai_chart_request_signature"] = current_signature
            # Only an actual calculation refreshes the full result area.
            st.rerun()


with st.sidebar:
    _birth_controls()

if runtime.mode == "development":
    st.info(runtime.user_message)
else:
    st.success(runtime.user_message)

chart = st.session_state.get("astai_chart")
if chart is None:
    st.info("Enter the birth details in the sidebar, choose the Indian birth place, then calculate.")
    st.stop()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Ascendant", f"{chart.ascendant.sign} {chart.ascendant.dms.text}")
m2.metric(
    "Moon",
    f"{chart.panchanga.moon_rashi} · {chart.panchanga.moon_nakshatra}-{chart.panchanga.moon_pada}",
)
m3.metric("Ayanamsa", f"{chart.metadata.ayanamsa_degrees:.8f}°")
m4.metric("Backend", chart.metadata.actual_ephemeris_backend.upper())
st.caption(
    f"Calculated place: {chart.input.place_name} · "
    f"lat {chart.input.latitude:.6f}°, lon {chart.input.longitude:.6f}° · "
    f"{chart.input.timezone}"
)
st.caption(
    f"Calculated settings: {chart.input.node_model.title()} Rahu/Ketu · "
    f"D7 method: {d7_profile_label(chart.input.varga_profile)}."
)

(
    positions_tab,
    d1_tab,
    bhava_tab,
    varga_tab,
    ashtakavarga_tab,
    panchanga_tab,
    dasha_tab,
    cusps_tab,
    audit_tab,
) = st.tabs(
    [
        "Planetary positions",
        "Lagna (D1)",
        "Bhava / Chalit",
        "Shodashavarga",
        "Ashtakavarga",
        "Panchanga",
        "Vimshottari",
        "Placidus cusps",
        "Audit",
    ]
)

with positions_tab:
    st.dataframe(
        planetary_position_rows(chart),
        use_container_width=True,
        hide_index=True,
    )

with d1_tab:
    st.subheader("Lagna (D1) · Whole Sign")
    st.caption("Primary Parashari Rashi framework. This is intentionally separate from Bhava/Chalit.")
    st.dataframe(
        lagna_house_rows(chart),
        use_container_width=True,
        hide_index=True,
    )
    moon = next(planet for planet in chart.planets if planet.body == "Moon")
    st.caption(
        f"Ascendant (Lagna): {chart.ascendant.sign} {chart.ascendant.dms.text}. "
        f"★ marks the Moon sign (Chandra Rashi): {moon.sign}."
    )

with bhava_tab:
    b = chart.bhava_chalit
    st.caption(
        f"Methodology: {b.methodology}. Planet signs do not change; only Bhava house membership can shift. "
        f"Swiss Sripati cross-check max delta: {b.swiss_sripati_crosscheck_max_arcseconds:.6g} arcsec."
    )
    st.subheader("Bhava Madhya and Sandhi")
    st.dataframe(
        [
            {
                "Bhava": h.house,
                "Start Sandhi": f"{h.start_sign} {h.start_dms.text}",
                "Bhava Madhya": f"{h.madhya_sign} {h.madhya_dms.text}",
                "End Sandhi": f"{h.end_sign} {h.end_dms.text}",
                "Span °": round(h.span_degrees, 8),
                "Planets": ", ".join(h.planets) if h.planets else "—",
            }
            for h in b.houses
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.subheader("Chalit house shifts")
    st.dataframe(
        [
            {
                "Body": p.body,
                "Rashi sign": p.rasi_sign,
                "Whole-sign house": p.rasi_house,
                "Bhava house": p.bhava_house,
                "Shifted": p.shifted,
            }
            for p in b.placements
        ],
        use_container_width=True,
        hide_index=True,
    )


@st.fragment
def _render_varga_panel() -> None:
    current_chart = st.session_state.get("astai_chart")
    if current_chart is None:
        return
    codes = [v.varga for v in current_chart.shodashavarga]
    if st.session_state.get("selected_varga_code") not in codes:
        st.session_state["selected_varga_code"] = "D9" if "D9" in codes else codes[0]
    selected_code = st.selectbox(
        "Select divisional chart",
        codes,
        key="selected_varga_code",
    )
    varga = next(v for v in current_chart.shodashavarga if v.varga == selected_code)
    st.subheader(f"{varga.varga} · {varga.name} · Ascendant {varga.ascendant_sign}")
    st.caption(f"Methodology: {varga.methodology}")
    if selected_code == "D7":
        st.caption(
            f"Calculated D7 profile: {d7_profile_label(current_chart.input.varga_profile)}. "
            "The AstroSage compatibility option affects D7 only."
        )
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


with varga_tab:
    _render_varga_panel()


@st.fragment
def _render_ashtakavarga_panel() -> None:
    current_chart = st.session_state.get("astai_chart")
    if current_chart is None:
        return

    av = current_chart.ashtakavarga
    st.caption(
        f"Methodology: {av.methodology} · status: {av.reduction_status}. "
        "These are raw classical scores; Trikona Shodhana, Ekadhipatya Shodhana and Shodhya Pinda are not applied."
    )

    st.subheader("Sarvashtakavarga (SAV)")
    st.dataframe(
        [
            {"Sign": sign, "SAV points": points}
            for sign, points in zip(av.sign_order, av.sarva_points_by_sign)
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.metric("SAV total", av.sarva_total)

    planets = [bav.planet for bav in av.bhinna]
    if st.session_state.get("selected_bav_planet") not in planets:
        st.session_state["selected_bav_planet"] = planets[0]
    selected_planet = st.selectbox(
        "Select Bhinnashtakavarga",
        planets,
        key="selected_bav_planet",
    )
    bav = next(item for item in av.bhinna if item.planet == selected_planet)

    st.subheader(f"{selected_planet} Bhinnashtakavarga (BAV)")
    st.dataframe(
        [
            {"Sign": sign, "BAV points": points}
            for sign, points in zip(av.sign_order, bav.points_by_sign)
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.metric(f"{selected_planet} BAV total", bav.total)

    st.subheader("Prastara contribution matrix")
    st.caption(av.point_semantics)
    st.dataframe(
        [
            {
                "Contributor": row.contributor,
                **{
                    sign: point
                    for sign, point in zip(av.sign_order, row.points_by_sign)
                },
                "Total": row.total,
            }
            for row in bav.prastara
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "Classical contributors are Sun through Saturn plus Ascendant/Lagna. "
        "Rahu, Ketu, Uranus, Neptune and Pluto are intentionally excluded from raw classical Ashtakavarga."
    )


with ashtakavarga_tab:
    _render_ashtakavarga_panel()

with panchanga_tab:
    p = chart.panchanga
    c1, c2, c3 = st.columns(3)
    c1.metric("Vara (weekday)", p.weekday)
    c2.metric("Sunrise", p.sunrise_local.strftime("%H:%M:%S") if p.sunrise_local else "Unavailable")
    c3.metric("Sunset", p.sunset_local.strftime("%H:%M:%S") if p.sunset_local else "Unavailable")
    st.subheader("Panchanga details")
    st.dataframe(
        [
            {"Element": "Tithi", "Value": f"{p.paksha} {p.tithi_name}"},
            {"Element": "Karana", "Value": p.karana},
            {"Element": "Yoga", "Value": p.yoga_name},
            {"Element": "Moon Rashi", "Value": p.moon_rashi},
            {"Element": "Moon Nakshatra", "Value": f"{p.moon_nakshatra}-{p.moon_pada}"},
            {"Element": "Civil weekday", "Value": p.civil_weekday},
            {
                "Element": "Birth before sunrise",
                "Value": (
                    "Yes"
                    if p.birth_before_sunrise is True
                    else "No"
                    if p.birth_before_sunrise is False
                    else "Unknown"
                ),
            },
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "This tab currently reports Vara, Tithi, Karana, Yoga, Moon Rashi and Moon Nakshatra. "
        "Additional classifications will be added only when their methodology is explicitly frozen."
    )

with dasha_tab:
    dasha = chart.vimshottari
    balance = dasha.balance_at_birth
    st.info(
        f"Balance at birth: {balance.lord} {balance.years}Y {balance.months}M {balance.days}D · "
        f"calendar year basis {dasha.year_days} days"
    )
    st.subheader("Birth timing path")
    st.dataframe(
        [
            {
                "Level": d.level,
                "Lord": d.lord,
                "Parent path": " / ".join(d.parent_path) if d.parent_path else "—",
                "Start": d.start,
                "End": d.end,
            }
            for d in dasha.birth_timing_path
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.subheader("Mahadashas")
    st.dataframe(
        [
            {
                "Lord": d.lord,
                "Start": d.start,
                "Theoretical start": d.theoretical_start,
                "End": d.end,
                "Partial at birth": d.partial_at_birth,
            }
            for d in dasha.mahadashas
        ],
        use_container_width=True,
        hide_index=True,
    )
    with st.expander("Antardashas"):
        st.dataframe(
            [
                {
                    "MD": d.parent_path[0] if d.parent_path else None,
                    "AD": d.lord,
                    "Start": d.start,
                    "End": d.end,
                    "Partial at birth": d.partial_at_birth,
                }
                for d in dasha.antardashas
            ],
            use_container_width=True,
            hide_index=True,
        )
    with st.expander("Pratyantardashas"):
        st.dataframe(
            [
                {
                    "MD": d.parent_path[0] if len(d.parent_path) > 0 else None,
                    "AD": d.parent_path[1] if len(d.parent_path) > 1 else None,
                    "PD": d.lord,
                    "Start": d.start,
                    "End": d.end,
                    "Partial at birth": d.partial_at_birth,
                }
                for d in dasha.pratyantardashas
            ],
            use_container_width=True,
            hide_index=True,
        )

with cusps_tab:
    st.caption(
        "These are Lahiri sidereal Placidus cusps. They are separate from Whole Sign and Sripati Bhava/Chalit, "
        "and are retained as the future KP cusp basis."
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
    st.write(f"**Birth place used:** {chart.input.place_name}")
    st.write(
        f"**Coordinates used:** {chart.input.latitude:.6f}°, "
        f"{chart.input.longitude:.6f}° · elevation {chart.input.elevation_m:.1f} m"
    )
    for item in chart.audit:
        st.write(f"**{item.status} · {item.code}**: {item.message}")
    st.caption(
        f"UTC: {chart.metadata.utc_datetime} · Julian day UT: {chart.metadata.julian_day_ut:.9f}"
    )
    st.code(chart.metadata.calculation_fingerprint, language=None)
    with st.expander("Raw reusable chart JSON"):
        st.json(chart.model_dump(mode="json"))