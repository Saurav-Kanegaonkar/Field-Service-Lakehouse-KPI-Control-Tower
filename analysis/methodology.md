# Methodology

The project uses a deterministic synthetic generator with a fixed random seed. Regional baselines vary by market type, technician count, district count, and average drive miles. Daily work order demand follows weekday volume patterns and mild seasonality. KPI calculations use weighted averages when the metric should follow work order volume, including completion rate, first visit fix rate, repeat visit rate, on-time arrival, customer score, and cost per work order.

Discrepancy records compare weekly lakehouse, BI report, and operations platform extracts. The generator introduces realistic mismatch drivers such as late arriving statuses, cancellation filters, timezone boundaries, technician reassignment, and duplicate appointment events. Data-quality checks test freshness, null rate, duplicate appointment event rate, and late status update rate.

The priority score is a weighted blend:

- Efficiency gap: 42 percent.
- KPI trust gap: 28 percent.
- Customer impact: 22 percent.
- Intervention readiness: 8 percent.

This weighting reflects the role's need to improve field efficiency while protecting metric integrity before recommendations are shared with field leaders.
