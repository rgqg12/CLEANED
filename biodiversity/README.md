# Biodiversity for i-CLEANED (SALCA-BD review)

- `scripts/01_extract_salcabd_table.py <control_table.ct> <outdir>`: reads the SALCA-BD rating table (a Python pickle in agroscope-ch/salca, SALCA-BD/salcabd/pkg_resources) with a restricted unpickler that only allows pandas/numpy classes, and writes the indicator groups, ratings and min/max tables.
- `salcabd_indicator_groups.csv`: the 11 indicator species groups with their weights.
- Worked example (extensive vs intensive permanent pasture: 17.0 vs 8.6 points) is in the methodology document.
