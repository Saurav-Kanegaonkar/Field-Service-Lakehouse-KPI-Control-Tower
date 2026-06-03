# Data Sources

All datasets are deterministic synthetic data for a public field-service analytics portfolio artifact. They do not represent real company, customer, technician, appointment, or operational performance data.

The generator in `scripts/score_operating_data.py` creates a nationwide field operations scenario with regional market mix, drive-time pressure, technician capacity, work order volume, appointment completion, first visit fix performance, reporting-source mismatch, and data-quality controls.

## Files

- `entities.csv`: Regional operating metadata at region grain.
- `daily_metrics.csv`: Daily KPI facts at region and service date grain.
- `reporting_extracts.csv`: Weekly metric extracts from lakehouse, BI report, and operations platform views.
- `quality_checks.csv`: Data-quality checks for freshness, null rate, duplicate appointment events, and late status updates.
- `recommended_actions.csv`: Candidate recommendations scored by effort, hours saved, cost avoidance, and review status.
