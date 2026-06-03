const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

const number = new Intl.NumberFormat("en-US");

function pct(value) {
  return `${Number(value).toFixed(1)}%`;
}

function scoreClass(value) {
  const numeric = Number(value);
  if (numeric >= 70) return "score high";
  if (numeric >= 45) return "score medium";
  return "score low";
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function renderPriority(rows) {
  const target = document.getElementById("priority-table");
  target.innerHTML = rows.map((row) => `
    <tr>
      <td>
        <b>${row.region_name}</b>
        <span>${row.division} / ${row.market_type}</span>
      </td>
      <td>${row.field_manager}</td>
      <td><span class="${scoreClass(row.priority_score)}">${row.priority_score}</span></td>
      <td>${pct(row.first_visit_fix_rate)}</td>
      <td>${row.trust_gap_score}</td>
      <td>${row.intervention_readiness}</td>
    </tr>
  `).join("");
}

function renderFindings(rows) {
  const target = document.getElementById("notebook-findings");
  target.innerHTML = rows.map((row) => `
    <article>
      <span>${row.step}</span>
      <h3>${row.notebook_cell}</h3>
      <p>${row.finding}</p>
      <small>${row.evidence}</small>
    </article>
  `).join("");
}

function renderAudit(rows) {
  const target = document.getElementById("audit-list");
  target.innerHTML = rows.slice(0, 6).map((row) => `
    <article>
      <div>
        <span>${row.week_start}</span>
        <h3>${row.metric_name.replaceAll("_", " ")}</h3>
        <p>${row.region_name}</p>
      </div>
      <div class="audit-values">
        <b>${row.absolute_delta}</b>
        <small>delta</small>
      </div>
      <p>${row.recommended_audit}</p>
      <em>${row.suspected_driver}</em>
    </article>
  `).join("");
}

function renderQuality(rows) {
  const target = document.getElementById("quality-list");
  target.innerHTML = rows.map((row) => `
    <article>
      <div>
        <b>${row.check_name}</b>
        <span>${row.primary_owner}</span>
      </div>
      <strong>${pct(row.failure_rate)}</strong>
    </article>
  `).join("");
}

function renderActions(rows) {
  const target = document.getElementById("actions-list");
  target.innerHTML = rows.slice(0, 6).map((row) => `
    <article>
      <div class="action-topline">
        <span>${row.region_id}</span>
        <b>${row.owner}</b>
      </div>
      <h3>${row.action_title}</h3>
      <p>${row.detail}</p>
      <footer>
        <span>${row.expected_weekly_hours_saved} hrs saved</span>
        <span>${money.format(Number(row.expected_cost_avoidance))}</span>
        <span>${row.status}</span>
      </footer>
    </article>
  `).join("");
}

function focusRequestedSection() {
  const params = new URLSearchParams(window.location.search);
  const requested = params.get("capture") || window.location.hash.replace("#", "");
  if (!requested) return;
  const target = document.getElementById(requested);
  if (!target) return;
  requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
}

async function init() {
  const response = await fetch("analysis/outputs/app_payload.json");
  const payload = await response.json();

  setText("metric-orders", number.format(payload.totals.work_orders));
  setText("metric-regions", payload.totals.regions);
  setText("metric-discrepancies", payload.totals.open_discrepancies);
  setText("metric-cost", money.format(payload.totals.expected_cost_avoidance));
  setText("hours-saved", `${payload.totals.expected_hours_saved.toFixed(1)} weekly hours saved`);

  renderPriority(payload.priorityQueue);
  renderFindings(payload.notebookFindings);
  renderAudit(payload.discrepancyQueue);
  renderQuality(payload.qualitySummary);
  renderActions(payload.actions);
  focusRequestedSection();
}

init();
