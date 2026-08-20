# Vimshottari Methodology

## Frozen v0.5 method

AstAi uses `vimshottari_120_v1`.

The lord sequence is:

`Ketu → Venus → Sun → Moon → Mars → Rahu → Jupiter → Saturn → Mercury`

with year weights:

`7, 20, 6, 10, 7, 18, 16, 19, 17`

for a total 120-year cycle.

## Birth balance

The Moon's exact position inside its Nakshatra determines the elapsed and remaining fraction of the birth Mahadasha.

For the traditional displayed balance:

- 1 dasha year = 360 days
- 1 dasha month = 30 days

This is used only for the displayed Y/M/D balance.

## Calendar timeline convention

Actual datetime boundaries use the explicit input:

`dasha_year_days`

Default: `365.25`.

This convention is stored in the response and audit metadata so calendar-date differences between software packages are not hidden.

## Nested periods

Each child period duration is:

`parent duration × child lord years / 120`

and each child sequence starts from the parent lord.

v0.5 outputs:

- full Mahadasha timeline
- full Antardasha timeline
- full Pratyantardasha timeline
- the exact birth-time path through:
  - Mahadasha
  - Antardasha
  - Pratyantardasha
  - Sookshma
  - Prana

Parent intervals are forced to close exactly at the final child boundary to prevent accumulated floating-point drift.

## Coverage

The generated timeline covers at least 120 dasha years after birth. If birth occurs partway through the first Mahadasha, the sequence repeats the starting lord as needed to preserve that post-birth coverage.

## Validation

Tests assert:

- child periods are contiguous and non-overlapping
- first child starts at the parent start
- last child ends exactly at the parent end
- partial-at-birth periods preserve their theoretical start
- the five-level birth path is internally consistent
- the post-birth coverage is at least the configured 120-year cycle

External vendor date compatibility for PD/SD/Prana is not yet claimed; it will require fixtures that state the vendor's calendar-year convention.
