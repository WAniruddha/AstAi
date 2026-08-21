from datetime import date, time

from astai.engine import calculate_chart
from astai.engine.vargas import varga_amsa
from astai.india_places import INDIA_PLACES, find_india_place, india_states, places_for_state
from astai.models import BirthData
from astai.presentation import lagna_house_rows, planetary_position_rows
from astai.product_inputs import (
    D7_METHOD_OPTIONS,
    MIN_BIRTH_DATE,
    birth_date_bounds,
    calculation_request_signature,
    d7_profile_from_label,
    d7_profile_label,
    resolve_ephemeris_runtime,
)


def test_birth_date_bounds_are_explicit_and_not_limited_to_1999():
    lower, upper = birth_date_bounds(date(2026, 8, 21))
    assert lower == MIN_BIRTH_DATE == date(1900, 1, 1)
    assert upper == date(2026, 8, 21)
    assert upper > date(1999, 12, 31)


def test_ephemeris_mode_is_automatic_for_local_development():
    runtime = resolve_ephemeris_runtime({})
    assert runtime.mode == "development"
    assert runtime.policy == "allow_moshier"
    assert runtime.ephemeris_path is None


def test_ephemeris_mode_becomes_strict_when_data_path_is_configured():
    runtime = resolve_ephemeris_runtime({"ASTAI_EPHE_PATH": r"D:\\swisseph\\ephe"})
    assert runtime.mode == "production"
    assert runtime.policy == "strict_swiss"
    assert runtime.ephemeris_path


def test_pune_resolves_without_manual_coordinates():
    pune = find_india_place("Maharashtra", "Pune")
    assert pune.label == "Pune, Maharashtra, India"
    assert abs(pune.latitude - 18.5204) < 1e-12
    assert abs(pune.longitude - 73.8567) < 1e-12
    assert pune.timezone == "Asia/Kolkata"


def test_catalog_covers_all_indian_states_and_union_territories_at_product_level():
    states = india_states()
    assert len(states) == 36
    assert "Maharashtra" in states
    assert "Delhi" in states
    assert "Andaman and Nicobar Islands" in states
    assert "Ladakh" in states


def test_state_place_lists_are_sorted_and_nonempty():
    for state in india_states():
        places = places_for_state(state)
        assert places
        assert [p.name for p in places] == sorted(p.name for p in places)


def test_catalog_coordinates_and_timezone_are_sane_for_india():
    assert len(INDIA_PLACES) >= 100
    for place in INDIA_PLACES:
        assert 6.0 <= place.latitude <= 38.0
        assert 68.0 <= place.longitude <= 98.0
        assert place.timezone == "Asia/Kolkata"


def _pune_birth_data(**updates) -> BirthData:
    values = {
        "date_of_birth": date(1999, 1, 14),
        "time_of_birth": time(12, 0, 0),
        "latitude": 18.5204,
        "longitude": 73.8567,
        "timezone": "Asia/Kolkata",
        "ephemeris_policy": "allow_moshier",
    }
    values.update(updates)
    return BirthData(**values)


def test_outer_planets_are_mandatory_in_product_chart_output():
    chart = calculate_chart(_pune_birth_data(include_outer_planets=True))
    by_name = {planet.body: planet for planet in chart.planets}
    for body in ("Uranus", "Neptune", "Pluto"):
        assert body in by_name
        assert by_name[body].classical is False

    d1_occupants = {body for house in chart.whole_sign_houses for body in house.planets}
    assert {"Uranus", "Neptune", "Pluto"} <= d1_occupants
    for varga in chart.shodashavarga:
        placements = {placement.body for placement in varga.placements}
        assert {"Uranus", "Neptune", "Pluto"} <= placements


def test_planetary_position_presentation_starts_with_ascendant():
    chart = calculate_chart(_pune_birth_data())
    rows = planetary_position_rows(chart)
    assert rows[0]["Body"] == "ASC (Ascendant)"
    assert rows[0]["Sign"] == chart.ascendant.sign
    assert rows[0]["Nakshatra"] == chart.ascendant.nakshatra


def test_lagna_d1_presentation_marks_moon_sign_with_star():
    chart = calculate_chart(_pune_birth_data())
    rows = lagna_house_rows(chart)
    moon = next(planet for planet in chart.planets if planet.body == "Moon")
    marked = [row for row in rows if "★" in str(row["Sign"])]
    assert len(marked) == 1
    assert str(marked[0]["Sign"]).startswith(moon.sign)


def test_calculation_request_signature_changes_for_node_or_d7_method():
    base = _pune_birth_data(
        include_outer_planets=True,
        node_model="mean",
        varga_profile="parashara_traditional",
    )
    same = base.model_copy()
    true_node = base.model_copy(update={"node_model": "true"})
    astro_d7 = base.model_copy(update={"varga_profile": "astrosage_reference_compat_v1"})

    assert calculation_request_signature(base) == calculation_request_signature(same)
    assert calculation_request_signature(base) != calculation_request_signature(true_node)
    assert calculation_request_signature(base) != calculation_request_signature(astro_d7)


def test_d7_product_labels_are_explicit_and_round_trip():
    assert [label for label, _ in D7_METHOD_OPTIONS] == [
        "Exact Parashari (default)",
        "AstroSage D7 published-table compatibility",
    ]
    for label, profile in D7_METHOD_OPTIONS:
        assert d7_profile_from_label(label) == profile
        assert d7_profile_label(profile) == label


def test_astrosage_compatibility_profile_changes_d7_only():
    longitude = 4.3
    exact_d7 = varga_amsa(longitude, "D7", "parashara_traditional")
    astro_d7 = varga_amsa(longitude, "D7", "astrosage_reference_compat_v1")
    assert exact_d7.sign_index != astro_d7.sign_index

    exact_d9 = varga_amsa(longitude, "D9", "parashara_traditional")
    astro_d9 = varga_amsa(longitude, "D9", "astrosage_reference_compat_v1")
    assert exact_d9 == astro_d9
