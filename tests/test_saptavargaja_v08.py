from __future__ import annotations

import pytest

from astai.engine.saptavargaja import (
    SAPTAVARGA_CODES,
    SAPTAVARGAJA_PROFILES,
    calculate_saptavargaja_bala,
    classify_saptavargaja_dignity,
    get_compound_relationship,
)

BASE_SIGNS = {
    "Sun": 4,
    "Moon": 3,
    "Mars": 5,
    "Mercury": 10,
    "Jupiter": 7,
    "Venus": 10,
    "Saturn": 9,
}


def test_score_profiles_are_explicit():
    assert SAPTAVARGAJA_PROFILES["bphs_textual_all_vargas_v1"].scores == {
        "moolatrikona": 45.0,
        "own": 30.0,
        "great_friend": 20.0,
        "friend": 15.0,
        "neutral": 10.0,
        "enemy": 4.0,
        "great_enemy": 2.0,
    }
    assert SAPTAVARGAJA_PROFILES["modern_panchadha_d1_mt_v1"].scores == {
        "moolatrikona": 45.0,
        "own": 30.0,
        "great_friend": 22.5,
        "friend": 15.0,
        "neutral": 7.5,
        "enemy": 3.75,
        "great_enemy": 1.875,
    }


def test_bphs_literal_profile_allows_mt_in_all_seven_vargas():
    positions = {code: (4, 10.0) for code in SAPTAVARGA_CODES}
    result = calculate_saptavargaja_bala(
        "Sun", positions, BASE_SIGNS, "bphs_textual_all_vargas_v1"
    )
    assert result.total_virupas == pytest.approx(315.0)
    assert {row.dignity for row in result.vargas} == {"moolatrikona"}


def test_modern_profile_limits_mt_to_d1():
    positions = {code: (4, 10.0) for code in SAPTAVARGA_CODES}
    result = calculate_saptavargaja_bala(
        "Sun", positions, BASE_SIGNS, "modern_panchadha_d1_mt_v1"
    )
    assert result.total_virupas == pytest.approx(225.0)
    assert result.vargas[0].dignity == "moolatrikona"
    assert all(row.dignity == "own" for row in result.vargas[1:])


def test_compound_relationship_matrix_uses_d1_positions():
    assert get_compound_relationship("Sun", "Mars", BASE_SIGNS) == "great_friend"
    assert get_compound_relationship("Sun", "Mercury", BASE_SIGNS) == "enemy"
    assert get_compound_relationship("Sun", "Venus", BASE_SIGNS) == "great_enemy"


def test_d1_compound_relationship_is_reused_in_non_d1_vargas():
    positions = {"D1": (4, 10.0)}
    positions.update({code: (0, 5.0) for code in SAPTAVARGA_CODES if code != "D1"})
    result = calculate_saptavargaja_bala(
        "Sun", positions, BASE_SIGNS, "modern_panchadha_d1_mt_v1"
    )
    assert result.vargas[0].dignity == "moolatrikona"
    assert all(row.dignity == "great_friend" for row in result.vargas[1:])
    assert result.total_virupas == pytest.approx(45.0 + 6 * 22.5)
    assert result.relationship_methodology == (
        "d1_panchadha_maitri_reused_across_saptavargas_v1"
    )


@pytest.mark.parametrize(
    ("planet", "sign_index", "inside_degree", "outside_degree"),
    [
        ("Sun", 4, 10.0, 25.0),
        ("Moon", 1, 10.0, 2.0),
        ("Mars", 0, 5.0, 20.0),
        ("Mercury", 5, 17.0, 25.0),
        ("Jupiter", 8, 5.0, 20.0),
        ("Venus", 6, 10.0, 20.0),
        ("Saturn", 10, 10.0, 25.0),
    ],
)
def test_bphs_moolatrikona_ranges(planet, sign_index, inside_degree, outside_degree):
    d1 = dict(BASE_SIGNS)
    d1[planet] = sign_index
    assert classify_saptavargaja_dignity(
        planet,
        "D1",
        sign_index,
        inside_degree,
        d1,
        "bphs_textual_all_vargas_v1",
    ) == "moolatrikona"
    outside = classify_saptavargaja_dignity(
        planet,
        "D1",
        sign_index,
        outside_degree,
        d1,
        "bphs_textual_all_vargas_v1",
    )
    assert outside != "moolatrikona"


def test_missing_varga_is_rejected():
    positions = {code: (4, 10.0) for code in SAPTAVARGA_CODES if code != "D30"}
    with pytest.raises(ValueError, match="D30"):
        calculate_saptavargaja_bala(
            "Sun", positions, BASE_SIGNS, "bphs_textual_all_vargas_v1"
        )


def test_d1_position_must_match_relationship_chart():
    positions = {code: (4, 10.0) for code in SAPTAVARGA_CODES}
    wrong = dict(BASE_SIGNS)
    wrong["Sun"] = 3
    with pytest.raises(ValueError, match="does not match"):
        calculate_saptavargaja_bala(
            "Sun", positions, wrong, "bphs_textual_all_vargas_v1"
        )


@pytest.mark.parametrize("planet", ["Rahu", "Ketu", "Uranus", "Neptune", "Pluto"])
def test_non_classical_bodies_rejected(planet):
    positions = {code: (0, 1.0) for code in SAPTAVARGA_CODES}
    with pytest.raises(ValueError):
        calculate_saptavargaja_bala(
            planet, positions, BASE_SIGNS, "bphs_textual_all_vargas_v1"
        )
