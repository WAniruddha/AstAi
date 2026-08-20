from datetime import date, time

from astai.engine import calculate_chart
from astai.models import BirthData


def _sample() -> BirthData:
    return BirthData(
        date_of_birth=date(1979, 8, 23),
        time_of_birth=time(23, 53, 18),
        latitude=28.6666666667,
        longitude=77.2166666667,
        timezone="Asia/Kolkata",
        ephemeris_policy="allow_moshier",
    )


def test_chart_exposes_separate_whole_sign_sripati_and_placidus_frameworks():
    chart = calculate_chart(_sample())
    assert chart.metadata.parashari_house_system == "whole_sign"
    assert chart.metadata.parashari_bhava_system == "sripati"
    assert chart.metadata.secondary_cusp_system == "placidus"
    assert chart.bhava_chalit.methodology == "sripati_bhava_chalit_v1"
    assert len(chart.whole_sign_houses) == 12
    assert len(chart.bhava_chalit.houses) == 12
    assert len(chart.placidus_cusps) == 12
    assert chart.bhava_chalit.swiss_sripati_crosscheck_max_arcseconds < 1e-6


def test_reference_sample_has_expected_chalit_shifts_and_deeper_dasha():
    chart = calculate_chart(_sample())
    shifts = {
        p.body: (p.rasi_house, p.bhava_house)
        for p in chart.bhava_chalit.placements
        if p.shifted
    }
    assert shifts == {
        "Moon": (4, 5),
        "Mercury": (3, 4),
        "Jupiter": (3, 4),
        "Saturn": (4, 5),
    }
    assert len(chart.vimshottari.pratyantardashas) > 0
    assert [p.level for p in chart.vimshottari.birth_timing_path] == [
        "MD", "AD", "PD", "SD", "PRANA"
    ]
    assert chart.vimshottari.coverage_end is not None
