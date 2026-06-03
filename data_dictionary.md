# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| entities.csv | region | Field operating metadata, manager ownership, technician capacity, districts, market type, and baseline KPI assumptions. |
| daily_metrics.csv | region x service date | Daily work order volume, installation mix, completion rate, first visit fix rate, repeat visits, arrival reliability, utilization, overtime, customer score, cost, and row-count controls. |
| reporting_extracts.csv | region x week x metric | Lakehouse, BI report, and operations platform metric values used for discrepancy investigation. |
| quality_checks.csv | region x check run | Freshness, null-rate, duplicate-event, and late-status controls with thresholds, owners, and recommended fixes. |
| recommended_actions.csv | region x action | Manager-ready intervention candidates with effort, expected hours saved, estimated cost avoidance, owner, and status. |
| analysis/outputs/priority_queue.csv | region | Ranked region queue scored by efficiency risk, KPI trust risk, customer impact, and intervention readiness. |
| analysis/outputs/discrepancy_queue.csv | discrepancy | Highest-severity reporting mismatches with suspected driver and audit recommendation. |
| analysis/outputs/data_quality_summary.csv | check type | Failure rates and owners for the data-quality monitor. |
| analysis/outputs/notebook_findings.csv | finding | Databricks-style notebook findings for stakeholder narration. |
