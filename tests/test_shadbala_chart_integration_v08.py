from datetime import date, time

import pytest

from astai.engine import calculate_chart
from astai.models import BirthData, ChartResponse


CLASSICAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _birth_data(varga_profile: str = "parashara_traditional") -> BirthData:
    return BirthData(
        name="Shadbala v0.8 integration fixture",
        place_name="Delhi, India",
        date_of_birth=date(1979, 8, 28),
        time_of_birth=time(17, 0, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
        ephemeris_policy="allow_moshier",
        include_outer_planets=True,
        varga_profile=varga_profile,
    )


def test_chart_response_exposes_complete_sthana_bala_with_provenance() -> None:
    chart = calculate_chart(_birth_data())
    shadbala = chart.shadbala

    assert shadbala.aggregation_status == "complete_sthana_bala_other_shadbala_components_pending"
    assert shadbala.saptavargaja_profile == "bphs_textual_all_vargas_v1"
    assert shadbala.saptavargaja_relationship_methodology == (
        "d1_panchadha_maitri_reused_across_saptavargas_v1"
    )
    assert shadbala.source_varga_profile == "parashara_traditional"
    assert [row.planet for row in shadbala.rows] == CLASSICAL_PLANETS

    for row in shadbala.rows:
        expected_sthana = (
            row.uccha_bala_virupas
            + row.saptavargaja_bala_virupas
            + row.ojayugma_bala_virupas
            + row.kendradi_bala_virupas
            + row.drekkana_bala_virupas
        )
        assert row.sthana_bala_total_virupas == pytest.approx(expected_sthana)
        assert row.naisargika_bala_virupas > 0.0
        assert row.sthana_bala_total_virupas != pytest.approx(
            expected_sthana + row.naisargika_bala_virupas
        )

    assert any(
        item.code == "SHADBALA_STHANA" and item.status == "METHODOLOGY_DEPENDENT"
        for item in chart.audit
    )

    payload = chart.model_dump(mode="json")
    roundtrip = ChartResponse.model_validate(payload)
    assert roundtrip.shadbala == chart.shadbala


def test_selected_d7_varga_profile_is_declared_in_shadbala_provenance() -> None:
    chart = calculate_chart(_birth_data("astrosage_reference_compat_v1"))
    assert chart.shadbala.source_varga_profile == "astrosage_reference_compat_v1"
    assert chart.metadata.varga_profile == "astrosage_reference_compat_v1"
    assert any(item.code == "VARGA_COMPATIBILITY_PROFILE" for item in chart.audit)
