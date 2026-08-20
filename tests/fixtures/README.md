# Golden reference fixtures

This directory is reserved for independently verified chart fixtures.

Preferred sources:

1. Raw exports from trusted astrology software using explicitly documented settings.
2. Trusted generated chart PDFs whose displayed values can be transcribed with provenance.
3. Independently calculated astronomical reference values.

Each fixture should record:

- source/software and version if known
- birth input exactly as entered
- timezone/DST convention
- ayanamsa
- node model
- house methodology
- expected planetary longitudes
- expected Ascendant/cusps
- expected Nakshatra/Pada
- tolerance used for numerical comparison
- notes about any methodology-dependent values

Do not add guessed expected values merely to make a test pass.

Future fixture groups should separately cover astronomy, D1/house frameworks, Vargas, Vimshottari, KP cusps/subdivisions, Jaimini and other deterministic modules.
