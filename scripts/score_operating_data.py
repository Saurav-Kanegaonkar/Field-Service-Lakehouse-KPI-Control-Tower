import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"
ANALYSIS = ROOT / "analysis"
DOCS = ROOT / "docs" / "images"

RANDOM_SEED = 4276
START_DATE = date(2026, 1, 5)
DAYS = 126


def clamp(value, low, high):
    return max(low, min(high, value))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n")


def pct(value):
    return f"{value:.1f}%"


def money(value):
    return "$" + format(round(value), ",")


def generate_regions():
    divisions = ["Mountain", "Central", "Southeast", "Atlantic"]
    market_types = ["Dense metro", "Suburban", "Rural", "Mixed footprint"]
    managers = [
        "Avery Patel",
        "Jordan Kim",
        "Maya Brooks",
        "Luis Romero",
        "Priya Nair",
        "Elena Morris",
        "Noah Grant",
        "Camila Torres",
        "Owen Shah",
        "Lena Murphy",
        "Caleb Nguyen",
        "Rina Jackson",
    ]
    regions = []
    for index in range(12):
        division = divisions[index % len(divisions)]
        market_type = market_types[(index * 2 + 1) % len(market_types)]
        rural_factor = {"Dense metro": 0.86, "Suburban": 0.98, "Rural": 1.24, "Mixed footprint": 1.08}[market_type]
        regions.append(
            {
                "region_id": f"REG{index + 1:02d}",
                "region_name": f"{division} Field Region {index + 1}",
                "division": division,
                "market_type": market_type,
                "field_manager": managers[index],
                "technician_count": random.randint(72, 168),
                "district_count": random.randint(5, 11),
                "avg_drive_miles": round(random.uniform(22, 54) * rural_factor, 1),
                "baseline_completion_rate": round(random.uniform(84.5, 94.2) - (rural_factor - 1) * 4, 1),
                "baseline_first_visit_fix": round(random.uniform(69.0, 82.0) - (rural_factor - 1) * 5, 1),
                "baseline_customer_score": round(random.uniform(78.0, 91.0) - (rural_factor - 1) * 3, 1),
            }
        )
    return regions


def generate_daily_kpis(regions):
    rows = []
    for day_index in range(DAYS):
        current = START_DATE + timedelta(days=day_index)
        weekday_factor = 0.94 if current.weekday() in (5, 6) else 1.0
        seasonality = math.sin(day_index / 13) * 1.6
        for region in regions:
            techs = int(region["technician_count"])
            drive_penalty = (float(region["avg_drive_miles"]) - 32) / 12
            capacity_hours = techs * random.uniform(7.4, 8.3) * weekday_factor
            work_orders = int(capacity_hours * random.uniform(0.62, 0.86))
            install_share = clamp(random.gauss(0.42, 0.08), 0.24, 0.62)
            repeat_visit_rate = clamp(random.gauss(12.5 + drive_penalty * 1.8, 2.2), 6.5, 22.0)
            completion_rate = clamp(
                float(region["baseline_completion_rate"])
                + seasonality
                - drive_penalty * 0.9
                + random.gauss(0, 2.0),
                74.0,
                98.5,
            )
            first_visit_fix = clamp(
                float(region["baseline_first_visit_fix"])
                + seasonality * 0.6
                - repeat_visit_rate * 0.18
                + random.gauss(0, 2.4),
                55.0,
                91.0,
            )
            on_time_arrival = clamp(
                89.0 - drive_penalty * 2.1 - repeat_visit_rate * 0.12 + random.gauss(0, 2.6),
                66.0,
                98.0,
            )
            utilization = clamp(work_orders / max(1, techs * 6.1) * 100 + random.gauss(0, 3.5), 58.0, 96.0)
            overtime_hours = round(max(0, (utilization - 78) * techs * random.uniform(0.012, 0.028)), 1)
            mean_minutes = clamp(106 + drive_penalty * 8 + repeat_visit_rate * 1.5 + random.gauss(0, 7), 72, 164)
            customer_score = clamp(
                float(region["baseline_customer_score"])
                + (first_visit_fix - 74) * 0.18
                + (on_time_arrival - 86) * 0.13
                + random.gauss(0, 1.7),
                61,
                96,
            )
            cost_per_order = clamp(118 + drive_penalty * 9 + overtime_hours / max(1, techs) * 42 + random.gauss(0, 8), 84, 178)
            lakehouse_rows = work_orders + random.randint(-4, 6)
            bi_rows = lakehouse_rows + random.choice([-3, -2, -1, 0, 0, 0, 1, 2, 4])
            crm_rows = lakehouse_rows + random.choice([-2, -1, 0, 0, 1, 2])
            data_quality_score = clamp(
                99.0
                - abs(lakehouse_rows - bi_rows) * 0.9
                - random.choice([0, 0, 0.4, 0.8, 1.1])
                - max(0, repeat_visit_rate - 15) * 0.25,
                86.0,
                100.0,
            )
            rows.append(
                {
                    "service_date": current.isoformat(),
                    "region_id": region["region_id"],
                    "work_orders": work_orders,
                    "install_share": round(install_share * 100, 1),
                    "completion_rate": round(completion_rate, 1),
                    "first_visit_fix_rate": round(first_visit_fix, 1),
                    "repeat_visit_rate": round(repeat_visit_rate, 1),
                    "on_time_arrival_rate": round(on_time_arrival, 1),
                    "technician_utilization": round(utilization, 1),
                    "overtime_hours": overtime_hours,
                    "mean_service_minutes": round(mean_minutes, 1),
                    "customer_experience_score": round(customer_score, 1),
                    "cost_per_work_order": round(cost_per_order, 2),
                    "lakehouse_order_rows": lakehouse_rows,
                    "bi_order_rows": bi_rows,
                    "crm_order_rows": crm_rows,
                    "data_quality_score": round(data_quality_score, 1),
                }
            )
    return rows


def generate_reporting_extracts(daily_rows):
    rows = []
    metrics = [
        ("completed_orders", "sum", "orders"),
        ("first_visit_fix_rate", "weighted average", "percent"),
        ("repeat_visit_rate", "weighted average", "percent"),
        ("on_time_arrival_rate", "weighted average", "percent"),
        ("technician_utilization", "average", "percent"),
        ("cost_per_work_order", "weighted average", "dollars"),
    ]
    by_region_week = defaultdict(list)
    for row in daily_rows:
        current = date.fromisoformat(row["service_date"])
        week_start = current - timedelta(days=current.weekday())
        by_region_week[(row["region_id"], week_start.isoformat())].append(row)

    for (region_id, week_start), rows_for_week in sorted(by_region_week.items()):
        orders = sum(int(row["work_orders"]) for row in rows_for_week)
        if orders < 1:
            continue
        for metric_name, calc_method, unit in metrics:
            if metric_name == "completed_orders":
                lakehouse = sum(int(row["lakehouse_order_rows"]) for row in rows_for_week)
                source_bias = random.choice([-8, -4, 0, 0, 0, 3, 6])
            elif metric_name == "cost_per_work_order":
                lakehouse = sum(float(row[metric_name]) * int(row["work_orders"]) for row in rows_for_week) / orders
                source_bias = random.choice([-2.4, -1.1, 0, 0, 0.7, 1.6, 3.2])
            elif calc_method == "weighted average":
                lakehouse = sum(float(row[metric_name]) * int(row["work_orders"]) for row in rows_for_week) / orders
                source_bias = random.choice([-1.6, -0.7, -0.2, 0, 0, 0.4, 0.9, 1.8])
            else:
                lakehouse = sum(float(row[metric_name]) for row in rows_for_week) / len(rows_for_week)
                source_bias = random.choice([-1.4, -0.8, 0, 0, 0.5, 1.1])
            bi_value = lakehouse + source_bias + random.gauss(0, abs(source_bias) * 0.15 + 0.08)
            ops_value = lakehouse + source_bias * random.uniform(0.2, 0.75) + random.gauss(0, 0.12)
            abs_delta = abs(lakehouse - bi_value)
            tolerance = 4 if unit == "orders" else (1.2 if unit == "dollars" else 0.75)
            rows.append(
                {
                    "week_start": week_start,
                    "region_id": region_id,
                    "metric_name": metric_name,
                    "calculation_method": calc_method,
                    "unit": unit,
                    "lakehouse_value": round(lakehouse, 2),
                    "bi_report_value": round(bi_value, 2),
                    "ops_platform_value": round(ops_value, 2),
                    "absolute_delta": round(abs_delta, 2),
                    "within_tolerance": "yes" if abs_delta <= tolerance else "no",
                    "suspected_driver": random.choice(
                        [
                            "late arriving work order status",
                            "missing cancellation filter",
                            "timezone boundary",
                            "technician reassignment",
                            "duplicate appointment event",
                        ]
                    ),
                }
            )
    return rows


def generate_quality_checks(daily_rows, reporting_rows):
    checks = []
    check_id = 1
    latest_date = max(date.fromisoformat(row["service_date"]) for row in daily_rows)
    grouped = defaultdict(list)
    for row in daily_rows:
        grouped[row["region_id"]].append(row)
    mismatches = defaultdict(int)
    for row in reporting_rows:
        if row["within_tolerance"] == "no":
            mismatches[row["region_id"]] += 1

    for region_id, rows in sorted(grouped.items()):
        freshness_hours = random.choice([2, 3, 4, 5, 7, 9, 13, 18])
        null_rate = clamp(random.gauss(0.65, 0.32) + mismatches[region_id] * 0.02, 0.05, 2.8)
        duplicate_rate = clamp(random.gauss(0.22, 0.18) + mismatches[region_id] * 0.01, 0.0, 1.7)
        late_status_rate = clamp(random.gauss(3.2, 1.4) + mismatches[region_id] * 0.05, 0.4, 9.5)
        checks.extend(
            [
                {
                    "check_id": f"DQ{check_id:03d}",
                    "run_date": latest_date.isoformat(),
                    "region_id": region_id,
                    "check_name": "lakehouse freshness",
                    "severity": "high" if freshness_hours > 12 else ("medium" if freshness_hours > 6 else "low"),
                    "observed_value": freshness_hours,
                    "threshold_value": 6,
                    "status": "fail" if freshness_hours > 6 else "pass",
                    "owner": "Data platform",
                    "recommended_fix": "Review upstream appointment event landing job and retry failed partition",
                },
                {
                    "check_id": f"DQ{check_id + 1:03d}",
                    "run_date": latest_date.isoformat(),
                    "region_id": region_id,
                    "check_name": "required field null rate",
                    "severity": "medium" if null_rate > 1.0 else "low",
                    "observed_value": round(null_rate, 2),
                    "threshold_value": 1.0,
                    "status": "fail" if null_rate > 1.0 else "pass",
                    "owner": "Analytics",
                    "recommended_fix": "Patch source mapping and add notebook assertion for required columns",
                },
                {
                    "check_id": f"DQ{check_id + 2:03d}",
                    "run_date": latest_date.isoformat(),
                    "region_id": region_id,
                    "check_name": "duplicate appointment event rate",
                    "severity": "medium" if duplicate_rate > 0.8 else "low",
                    "observed_value": round(duplicate_rate, 2),
                    "threshold_value": 0.8,
                    "status": "fail" if duplicate_rate > 0.8 else "pass",
                    "owner": "Data platform",
                    "recommended_fix": "Deduplicate by appointment id, status timestamp, and technician id",
                },
                {
                    "check_id": f"DQ{check_id + 3:03d}",
                    "run_date": latest_date.isoformat(),
                    "region_id": region_id,
                    "check_name": "late status update rate",
                    "severity": "high" if late_status_rate > 7.0 else ("medium" if late_status_rate > 4.5 else "low"),
                    "observed_value": round(late_status_rate, 2),
                    "threshold_value": 4.5,
                    "status": "fail" if late_status_rate > 4.5 else "pass",
                    "owner": "Field operations",
                    "recommended_fix": "Coach districts with delayed completion updates and refresh cutover rule",
                },
            ]
        )
        check_id += 4
    return checks


def aggregate_region_scores(regions, daily_rows, reporting_rows, quality_rows):
    region_lookup = {row["region_id"]: row for row in regions}
    daily_by_region = defaultdict(list)
    for row in daily_rows:
        daily_by_region[row["region_id"]].append(row)
    mismatches = defaultdict(list)
    for row in reporting_rows:
        if row["within_tolerance"] == "no":
            mismatches[row["region_id"]].append(row)
    failed_checks = defaultdict(list)
    for row in quality_rows:
        if row["status"] == "fail":
            failed_checks[row["region_id"]].append(row)

    scores = []
    for region_id, rows in sorted(daily_by_region.items()):
        orders = sum(int(row["work_orders"]) for row in rows)
        avg = lambda column: sum(float(row[column]) for row in rows) / len(rows)
        wavg = lambda column: sum(float(row[column]) * int(row["work_orders"]) for row in rows) / orders
        completion = wavg("completion_rate")
        first_fix = wavg("first_visit_fix_rate")
        repeat = wavg("repeat_visit_rate")
        on_time = wavg("on_time_arrival_rate")
        utilization = avg("technician_utilization")
        overtime = sum(float(row["overtime_hours"]) for row in rows)
        cx = wavg("customer_experience_score")
        cost = wavg("cost_per_work_order")
        data_quality = avg("data_quality_score")
        mismatch_count = len(mismatches[region_id])
        failed_count = len(failed_checks[region_id])
        efficiency_gap = clamp((92 - completion) * 1.15 + (78 - first_fix) * 0.95 + (repeat - 10) * 1.1 + (86 - on_time) * 0.75, 0, 100)
        trust_gap = clamp((99 - data_quality) * 5.5 + mismatch_count * 1.7 + failed_count * 2.4, 0, 100)
        customer_impact = clamp((86 - cx) * 3.1 + (cost - 120) * 0.8 + overtime / max(1, len(rows)) * 0.65, 0, 100)
        readiness = clamp(100 - trust_gap * 0.35 - failed_count * 1.6 + utilization * 0.18, 0, 100)
        priority = clamp(efficiency_gap * 0.42 + trust_gap * 0.28 + customer_impact * 0.22 + readiness * 0.08, 0, 100)
        score_row = {
            "region_id": region_id,
            "region_name": region_lookup[region_id]["region_name"],
            "division": region_lookup[region_id]["division"],
            "market_type": region_lookup[region_id]["market_type"],
            "field_manager": region_lookup[region_id]["field_manager"],
            "work_orders": orders,
            "completion_rate": round(completion, 1),
            "first_visit_fix_rate": round(first_fix, 1),
            "repeat_visit_rate": round(repeat, 1),
            "on_time_arrival_rate": round(on_time, 1),
            "technician_utilization": round(utilization, 1),
            "overtime_hours": round(overtime, 1),
            "customer_experience_score": round(cx, 1),
            "cost_per_work_order": round(cost, 2),
            "data_quality_score": round(data_quality, 1),
            "mismatch_count": mismatch_count,
            "failed_quality_checks": failed_count,
            "efficiency_gap_score": round(efficiency_gap, 1),
            "trust_gap_score": round(trust_gap, 1),
            "customer_impact_score": round(customer_impact, 1),
            "intervention_readiness": round(readiness, 1),
            "priority_score": round(priority, 1),
        }
        scores.append(score_row)
    return sorted(scores, key=lambda row: row["priority_score"], reverse=True)


def generate_actions(priority_rows):
    actions = []
    action_templates = [
        ("Reconcile first visit fix definition", "Analytics", "Align numerator and denominator across lakehouse, BI, and operations extracts", 9, 31),
        ("Refresh late status coaching packet", "Field operations", "Target districts with delayed completion updates and high repeat visits", 13, 45),
        ("Add appointment dedupe assertion", "Data platform", "Block duplicate appointment events before gold KPI tables refresh", 6, 26),
        ("Route rural overflow by drive-time band", "Field operations", "Move capacity from low-risk districts into longer drive-time appointment clusters", 18, 52),
        ("Publish manager KPI digest", "Analytics", "Send weekly rank, root cause, and next action summary to field leaders", 5, 22),
    ]
    for index, region in enumerate(priority_rows):
        for template_index, (title, owner, detail, effort, lift) in enumerate(action_templates[:3 if index > 3 else 5]):
            actions.append(
                {
                    "action_id": f"ACT{len(actions) + 1:03d}",
                    "region_id": region["region_id"],
                    "action_title": title,
                    "owner": owner,
                    "detail": detail,
                    "estimated_effort_hours": effort + random.randint(-2, 4),
                    "expected_weekly_hours_saved": round(lift * (region["priority_score"] / 100) * random.uniform(0.72, 1.12), 1),
                    "expected_cost_avoidance": round(region["work_orders"] * random.uniform(0.018, 0.045) * float(region["cost_per_work_order"]), 0),
                    "status": random.choice(["ready for manager review", "needs data owner", "queued for weekly review"]),
                }
            )
    return actions


def build_discrepancy_queue(reporting_rows, priority_lookup):
    severe = []
    for row in reporting_rows:
        if row["within_tolerance"] == "yes":
            continue
        metric_weight = {
            "completed_orders": 1.3,
            "first_visit_fix_rate": 1.4,
            "repeat_visit_rate": 1.1,
            "on_time_arrival_rate": 1.2,
            "technician_utilization": 1.0,
            "cost_per_work_order": 1.2,
        }[row["metric_name"]]
        priority = priority_lookup[row["region_id"]]
        severity = float(row["absolute_delta"]) * metric_weight + float(priority["priority_score"]) * 0.18
        severe.append(
            {
                "week_start": row["week_start"],
                "region_id": row["region_id"],
                "region_name": priority["region_name"],
                "metric_name": row["metric_name"],
                "lakehouse_value": row["lakehouse_value"],
                "bi_report_value": row["bi_report_value"],
                "absolute_delta": row["absolute_delta"],
                "severity_score": round(severity, 1),
                "suspected_driver": row["suspected_driver"],
                "recommended_audit": audit_recommendation(row["suspected_driver"]),
            }
        )
    return sorted(severe, key=lambda row: row["severity_score"], reverse=True)


def audit_recommendation(driver):
    mapping = {
        "late arriving work order status": "Recompute weekly gold table after late status watermark and compare closed orders",
        "missing cancellation filter": "Validate cancellation flag logic against appointment status history",
        "timezone boundary": "Check service date conversion between local appointment time and UTC event time",
        "technician reassignment": "Rebuild technician ownership bridge for reassigned work orders",
        "duplicate appointment event": "Deduplicate appointment events before metric aggregation",
    }
    return mapping[driver]


def build_quality_summary(quality_rows):
    summary = []
    by_check = defaultdict(list)
    for row in quality_rows:
        by_check[row["check_name"]].append(row)
    for check_name, rows in sorted(by_check.items()):
        failed = [row for row in rows if row["status"] == "fail"]
        summary.append(
            {
                "check_name": check_name,
                "checks_run": len(rows),
                "failures": len(failed),
                "failure_rate": round(len(failed) / len(rows) * 100, 1),
                "highest_severity": "high"
                if any(row["severity"] == "high" for row in failed)
                else ("medium" if any(row["severity"] == "medium" for row in failed) else "low"),
                "primary_owner": max(set(row["owner"] for row in rows), key=[row["owner"] for row in rows].count),
            }
        )
    return sorted(summary, key=lambda row: row["failure_rate"], reverse=True)


def build_notebook_findings(priority_rows, discrepancy_queue, quality_summary):
    top = priority_rows[0]
    second = priority_rows[1]
    return [
        {
            "step": "01",
            "notebook_cell": "Bronze to silver volume check",
            "finding": f"{top['region_name']} has the highest operating priority because completion, repeat visit, and source mismatch risk overlap.",
            "evidence": f"{top['priority_score']} priority score, {top['mismatch_count']} metric mismatches, {top['failed_quality_checks']} failed quality checks",
        },
        {
            "step": "02",
            "notebook_cell": "Gold KPI reconciliation",
            "finding": f"The largest reporting gap is {discrepancy_queue[0]['metric_name']} for {discrepancy_queue[0]['region_name']}.",
            "evidence": f"{discrepancy_queue[0]['absolute_delta']} point or unit delta, driver tagged as {discrepancy_queue[0]['suspected_driver']}",
        },
        {
            "step": "03",
            "notebook_cell": "Field manager action scoring",
            "finding": f"{second['region_name']} is the next best manager review candidate because its readiness score remains actionable.",
            "evidence": f"{second['intervention_readiness']} readiness, {second['customer_experience_score']} customer score",
        },
        {
            "step": "04",
            "notebook_cell": "Data quality monitor",
            "finding": f"The most common failing control is {quality_summary[0]['check_name']}.",
            "evidence": f"{quality_summary[0]['failure_rate']}% failure rate across regions",
        },
    ]


def build_payload(priority_rows, discrepancy_queue, quality_summary, notebook_findings, actions):
    top_actions = sorted(actions, key=lambda row: (float(row["expected_cost_avoidance"]), float(row["expected_weekly_hours_saved"])), reverse=True)[:8]
    totals = {
        "work_orders": sum(int(row["work_orders"]) for row in priority_rows),
        "regions": len(priority_rows),
        "open_discrepancies": len(discrepancy_queue),
        "failed_quality_checks": sum(int(row["failed_quality_checks"]) for row in priority_rows),
        "expected_cost_avoidance": sum(float(row["expected_cost_avoidance"]) for row in top_actions),
        "expected_hours_saved": sum(float(row["expected_weekly_hours_saved"]) for row in top_actions),
    }
    return {
        "generated_at": date.today().isoformat(),
        "hero": {
            "title": "Field Service Lakehouse KPI Control Tower",
            "subtitle": "A command-center artifact for nationwide field operations, KPI reconciliation, and manager-ready recommendations.",
        },
        "totals": totals,
        "priorityQueue": priority_rows[:8],
        "discrepancyQueue": discrepancy_queue[:10],
        "qualitySummary": quality_summary,
        "notebookFindings": notebook_findings,
        "actions": top_actions,
    }


def write_docs(regions, daily_rows, reporting_rows, quality_rows, priority_rows, discrepancy_queue, quality_summary, actions):
    top = priority_rows[0]
    top_action = max(actions, key=lambda row: float(row["expected_cost_avoidance"]))
    readme = f"""
# Field Service Lakehouse KPI Control Tower

An interactive field-service analytics artifact for a nationwide in-home installation and repair operation. The project shows how a data analyst can turn lakehouse tables, reporting discrepancies, data-quality checks, and field manager feedback into a KPI control tower with a defensible action queue.

![Executive KPI cockpit](docs/images/dashboard.png)

The executive cockpit summarizes operating health, trusted KPI coverage, open reconciliation issues, and the highest-priority regions for manager review.

![Discrepancy audit queue](docs/images/discrepancy-audit.png)

The discrepancy audit queue compares lakehouse, BI, and operations extracts, then tags the likely source of each mismatch so analysts can resolve KPI misalignment before leadership review.

![Field manager action plan](docs/images/action-plan.png)

The action plan converts analytical signals into field manager recommendations with owners, expected weekly hours saved, and estimated cost avoidance.

## What This Project Demonstrates

- Lakehouse-style KPI modeling for field service work orders, technician capacity, appointment reliability, and customer experience.
- Databricks-style notebook thinking, including bronze to silver volume checks, gold KPI reconciliation, and metric trust controls.
- Discrepancy investigation across reporting platforms before dashboards are treated as decision-ready.
- Executive storytelling that turns statistical and operational trends into manager-ready recommendations.

## Data

All data is deterministic synthetic data generated by `scripts/score_operating_data.py`. It does not represent real company performance, customer records, technician records, or private operational data.

The synthetic data is modeled on common field-service structures:

- `data/entities.csv`: {len(regions)} regional field operation records with division, market type, manager, technician count, district count, and drive-time context.
- `data/daily_metrics.csv`: {len(daily_rows):,} region-day KPI rows covering work orders, completion rate, first visit fix rate, repeat visit rate, on-time arrival, technician utilization, overtime, customer score, cost per work order, and row-count controls.
- `data/reporting_extracts.csv`: {len(reporting_rows):,} weekly KPI extracts comparing lakehouse, BI report, and operations platform values.
- `data/quality_checks.csv`: {len(quality_rows):,} data-quality checks for freshness, nulls, duplicates, and late status updates.
- `data/recommended_actions.csv`: {len(actions):,} intervention candidates with owner, effort, expected hours saved, cost avoidance, and status.

The generator uses a fixed random seed, regional market mix assumptions, drive-time penalties, weekday volume patterns, weighted KPI calculations, reporting-source bias, and quality-control thresholds. Re-running the script reproduces the same operating scenario and refreshed outputs.

## Analysis Outputs

- `analysis/outputs/priority_queue.csv` ranks regions by efficiency gap, KPI trust gap, customer impact, and intervention readiness.
- `analysis/outputs/discrepancy_queue.csv` identifies the highest-severity metric mismatches and recommended audit steps.
- `analysis/outputs/data_quality_summary.csv` summarizes check failures by control type and owner.
- `analysis/outputs/notebook_findings.csv` captures the findings an analyst would present after a notebook review.
- `analysis/outputs/app_payload.json` powers the interactive static application.

## Current Findings

- Highest-priority region: {top['region_name']} with a {top['priority_score']} priority score.
- KPI trust risk: {top['mismatch_count']} metric mismatches and {top['failed_quality_checks']} failed quality checks in the top region.
- Largest audit item: {discrepancy_queue[0]['metric_name']} for {discrepancy_queue[0]['region_name']}, with a {discrepancy_queue[0]['absolute_delta']} point or unit delta.
- Best near-term action: {top_action['action_title']}, estimated at {top_action['expected_weekly_hours_saved']} weekly hours saved and {money(float(top_action['expected_cost_avoidance']))} cost avoidance.

## Run Locally

```bash
npm run analyze
npm run start
```

Then open `http://localhost:4181`.

## Scope

This is a static public portfolio artifact. It does not connect to live lakehouse tables, Databricks workspaces, AWS storage, BI servers, field-service platforms, customer systems, workforce management tools, or production data. It shows how an analyst can structure KPI reconciliation, data integrity controls, dashboarding, and consultative field recommendations before production implementation.
"""
    write_text(ROOT / "README.md", readme)

    data_readme = f"""
# Data Sources

All datasets are deterministic synthetic data for a public field-service analytics portfolio artifact. They do not represent real company, customer, technician, appointment, or operational performance data.

The generator in `scripts/score_operating_data.py` creates a nationwide field operations scenario with regional market mix, drive-time pressure, technician capacity, work order volume, appointment completion, first visit fix performance, reporting-source mismatch, and data-quality controls.

## Files

- `entities.csv`: Regional operating metadata at region grain.
- `daily_metrics.csv`: Daily KPI facts at region and service date grain.
- `reporting_extracts.csv`: Weekly metric extracts from lakehouse, BI report, and operations platform views.
- `quality_checks.csv`: Data-quality checks for freshness, null rate, duplicate appointment events, and late status updates.
- `recommended_actions.csv`: Candidate recommendations scored by effort, hours saved, cost avoidance, and review status.
"""
    write_text(DATA / "README.md", data_readme)

    dictionary = """
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
"""
    write_text(ROOT / "data_dictionary.md", dictionary)

    analysis_plan = """
# Analysis Plan

1. Generate deterministic synthetic field-service source data across regional operations, daily KPIs, reporting extracts, and quality checks.
2. Aggregate region-level operating KPIs with weighted calculations for work-order-sensitive metrics.
3. Compare lakehouse, BI report, and operations platform extracts to surface reporting discrepancies outside tolerance.
4. Score each region by efficiency gap, KPI trust gap, customer impact, and intervention readiness.
5. Convert priority signals into field manager actions with owner, effort, expected weekly hours saved, and estimated cost avoidance.
6. Publish app-ready outputs for an executive cockpit, discrepancy audit queue, notebook findings, quality monitor, and action plan.
"""
    write_text(ANALYSIS / "analysis_plan.md", analysis_plan)

    methodology = """
# Methodology

The project uses a deterministic synthetic generator with a fixed random seed. Regional baselines vary by market type, technician count, district count, and average drive miles. Daily work order demand follows weekday volume patterns and mild seasonality. KPI calculations use weighted averages when the metric should follow work order volume, including completion rate, first visit fix rate, repeat visit rate, on-time arrival, customer score, and cost per work order.

Discrepancy records compare weekly lakehouse, BI report, and operations platform extracts. The generator introduces realistic mismatch drivers such as late arriving statuses, cancellation filters, timezone boundaries, technician reassignment, and duplicate appointment events. Data-quality checks test freshness, null rate, duplicate appointment event rate, and late status update rate.

The priority score is a weighted blend:

- Efficiency gap: 42 percent.
- KPI trust gap: 28 percent.
- Customer impact: 22 percent.
- Intervention readiness: 8 percent.

This weighting reflects the role's need to improve field efficiency while protecting metric integrity before recommendations are shared with field leaders.
"""
    write_text(ANALYSIS / "methodology.md", methodology)

    executive = f"""
# Executive Findings

## What I Analyzed

I generated and analyzed {len(daily_rows):,} daily KPI rows, {len(reporting_rows):,} weekly reporting extract rows, {len(quality_rows):,} data-quality check rows, and {len(actions):,} field manager action candidates for a synthetic nationwide in-home field operation.

## Findings

- {top['region_name']} is the highest-priority region with a {top['priority_score']} priority score.
- The top region combines {top['completion_rate']}% completion, {top['first_visit_fix_rate']}% first visit fix, {top['repeat_visit_rate']}% repeat visits, and a {top['data_quality_score']} data-quality score.
- The largest discrepancy is {discrepancy_queue[0]['metric_name']} for {discrepancy_queue[0]['region_name']}, with a {discrepancy_queue[0]['absolute_delta']} point or unit delta.
- The most common failing quality control is {quality_summary[0]['check_name']} with a {quality_summary[0]['failure_rate']}% failure rate.

## Recommendation

Use the priority queue to focus field manager review on regions where operational inefficiency and KPI trust risk overlap. Resolve the largest reporting mismatches before publishing executive dashboards, then move the top action candidates into weekly field operations follow-up.
"""
    write_text(ANALYSIS / "executive_findings.md", executive)

    sql = """
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
"""
    write_text(ANALYSIS / "sql_checks.sql", sql)

    status = """
# Status

- Status: upgraded through the Portfolio Artifact Upgrade Workflow.
- Safe to link as a field service data analyst portfolio artifact after changes are pushed.
- README uses company-domain language and does not name the target company.
- Synthetic data is disclosed in the README, data README, and project scope.
"""
    write_text(ROOT / "STATUS.md", status)


def main():
    random.seed(RANDOM_SEED)
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    regions = generate_regions()
    daily_rows = generate_daily_kpis(regions)
    reporting_rows = generate_reporting_extracts(daily_rows)
    quality_rows = generate_quality_checks(daily_rows, reporting_rows)
    priority_rows = aggregate_region_scores(regions, daily_rows, reporting_rows, quality_rows)
    priority_lookup = {row["region_id"]: row for row in priority_rows}
    actions = generate_actions(priority_rows)
    discrepancy_queue = build_discrepancy_queue(reporting_rows, priority_lookup)
    quality_summary = build_quality_summary(quality_rows)
    notebook_findings = build_notebook_findings(priority_rows, discrepancy_queue, quality_summary)
    payload = build_payload(priority_rows, discrepancy_queue, quality_summary, notebook_findings, actions)

    write_csv(DATA / "entities.csv", regions, list(regions[0].keys()))
    write_csv(DATA / "daily_metrics.csv", daily_rows, list(daily_rows[0].keys()))
    write_csv(DATA / "reporting_extracts.csv", reporting_rows, list(reporting_rows[0].keys()))
    write_csv(DATA / "quality_checks.csv", quality_rows, list(quality_rows[0].keys()))
    write_csv(DATA / "recommended_actions.csv", actions, list(actions[0].keys()))
    write_csv(OUTPUTS / "priority_queue.csv", priority_rows, list(priority_rows[0].keys()))
    write_csv(OUTPUTS / "discrepancy_queue.csv", discrepancy_queue, list(discrepancy_queue[0].keys()))
    write_csv(OUTPUTS / "data_quality_summary.csv", quality_summary, list(quality_summary[0].keys()))
    write_csv(OUTPUTS / "notebook_findings.csv", notebook_findings, list(notebook_findings[0].keys()))

    summary = {
        "regions": len(regions),
        "daily_metric_rows": len(daily_rows),
        "reporting_extract_rows": len(reporting_rows),
        "quality_check_rows": len(quality_rows),
        "recommended_actions": len(actions),
        "top_region": priority_rows[0],
        "top_discrepancy": discrepancy_queue[0],
    }
    write_text(OUTPUTS / "summary.json", json.dumps(summary, indent=2))
    write_text(OUTPUTS / "app_payload.json", json.dumps(payload, indent=2))
    write_docs(regions, daily_rows, reporting_rows, quality_rows, priority_rows, discrepancy_queue, quality_summary, actions)

    print(f"Generated {len(daily_rows):,} daily KPI rows")
    print(f"Top region: {priority_rows[0]['region_name']} priority_score={priority_rows[0]['priority_score']}")
    print(f"Open discrepancies: {len(discrepancy_queue)}")


if __name__ == "__main__":
    main()
