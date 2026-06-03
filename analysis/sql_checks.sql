-- SQL checks mirror the synthetic CSV outputs in this public portfolio artifact.
-- They are written in Databricks SQL style for interview discussion.

-- 1. Region-day uniqueness.
select
  service_date,
  region_id,
  count(*) as row_count
from daily_metrics
group by service_date, region_id
having count(*) > 1;

-- 2. KPI bounds.
select *
from daily_metrics
where completion_rate not between 0 and 100
   or first_visit_fix_rate not between 0 and 100
   or repeat_visit_rate not between 0 and 100
   or on_time_arrival_rate not between 0 and 100
   or technician_utilization not between 0 and 100
   or data_quality_score not between 0 and 100;

-- 3. Reporting discrepancies outside tolerance.
select
  week_start,
  region_id,
  metric_name,
  lakehouse_value,
  bi_report_value,
  absolute_delta,
  suspected_driver
from reporting_extracts
where within_tolerance = 'no'
order by absolute_delta desc;

-- 4. Failed data-quality checks by owner.
select
  owner,
  check_name,
  count(*) as failed_checks
from quality_checks
where status = 'fail'
group by owner, check_name
order by failed_checks desc;

-- 5. Manager-ready priority queue.
select
  region_id,
  region_name,
  priority_score,
  efficiency_gap_score,
  trust_gap_score,
  customer_impact_score,
  intervention_readiness
from priority_queue
order by priority_score desc;
