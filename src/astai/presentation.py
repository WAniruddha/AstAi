from __future__ import annotations

from astai.models import ChartResponse


def planetary_position_rows(chart: ChartResponse) -> list[dict[str, object]]:
    """Build the UI table with the Ascendant as the first astronomical row."""

    asc_tropical = (
        chart.ascendant.longitude_sidereal + chart.metadata.ayanamsa_degrees
    ) % 360.0
    rows: list[dict[str, object]] = [
        {
            "Body": "ASC (Ascendant)",
            "Sign": chart.ascendant.sign,
            "DMS": chart.ascendant.dms.text,
            "Sidereal °": round(chart.ascendant.longitude_sidereal, 9),
            "Tropical °": round(asc_tropical, 9),
            "Nakshatra": chart.ascendant.nakshatra,
            "Pada": chart.ascendant.pada,
            "Star Lord": chart.ascendant.nakshatra_lord,
            "Speed °/day": None,
            "Retrograde": None,
            "Backend": "geometry",
        }
    ]

    rows.extend(
        {
            "Body": planet.body,
            "Sign": planet.sign,
            "DMS": planet.dms.text,
            "Sidereal °": round(planet.longitude_sidereal, 9),
            "Tropical °": round(planet.longitude_tropical, 9),
            "Nakshatra": planet.nakshatra,
            "Pada": planet.pada,
            "Star Lord": planet.nakshatra_lord,
            "Speed °/day": round(planet.speed_longitude, 9),
            "Retrograde": planet.retrograde,
            "Backend": planet.ephemeris_backend,
        }
        for planet in chart.planets
    )
    return rows


def lagna_house_rows(chart: ChartResponse) -> list[dict[str, object]]:
    """Build the Lagna/D1 table and mark the Moon-sign house with a star."""

    moon = next(planet for planet in chart.planets if planet.body == "Moon")
    return [
        {
            "House": house.house,
            "Sign": f"{house.sign} ★" if house.sign_index == moon.sign_index else house.sign,
            "Planets": ", ".join(house.planets) if house.planets else "—",
        }
        for house in chart.whole_sign_houses
    ]
