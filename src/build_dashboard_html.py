from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from string import Template


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "dashboard_kpi_dataset.csv"
)

OUTPUT_FILE = (
    ROOT
    / "outputs"
    / "sustainability_dashboard.html"
)


def read_dataset() -> list[dict[str, str]]:
    """Read the controlled dashboard dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def build_dashboard(rows: list[dict[str, str]]) -> str:
    """Generate a self-contained HTML dashboard."""

    if not rows:
        raise ValueError("The dashboard dataset is empty.")

    total_kpis = len(rows)

    ready_kpis = sum(
        row["reporting_readiness"] == "Ready to report"
        for row in rows
    )

    hold_kpis = total_kpis - ready_kpis

    total_exceptions = sum(
        int(row.get("exception_count", "0") or 0)
        for row in rows
    )

    approved_kpis = sum(
        row["approval_status"] == "Approved"
        for row in rows
    )

    ready_percentage = round(
        (ready_kpis / total_kpis) * 100,
        1,
    )

    data_json = json.dumps(
        rows,
        ensure_ascii=False,
    ).replace("</", "<\\/")

    generated_at = datetime.now().strftime(
        "%d %B %Y, %H:%M"
    )

    template = Template(
        r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>
<title>Quarter-End Sustainability Reporting Dashboard</title>

<style>
:root {
    --background: #f3f5f7;
    --surface: #ffffff;
    --text: #18202a;
    --muted: #667085;
    --border: #d9dee7;
    --ready: #157347;
    --hold: #b54708;
    --exception: #b42318;
    --accent: #175cd3;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: var(--background);
    color: var(--text);
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;
}

.dashboard {
    width: min(1500px, 96%);
    margin: 28px auto 48px;
}

.header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px 30px;
}

.header h1 {
    margin: 0 0 10px;
    font-size: 30px;
}

.header p {
    max-width: 1000px;
    margin: 0;
    color: var(--muted);
    line-height: 1.6;
}

.meta {
    margin-top: 14px;
    color: var(--muted);
    font-size: 13px;
}

.cards {
    display: grid;
    grid-template-columns:
        repeat(5, minmax(160px, 1fr));
    gap: 16px;
    margin: 18px 0;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
}

.card-label {
    color: var(--muted);
    font-size: 13px;
    font-weight: 600;
}

.card-value {
    margin-top: 8px;
    font-size: 31px;
    font-weight: 700;
}

.grid {
    display: grid;
    grid-template-columns: 340px 1fr;
    gap: 18px;
}

.panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 22px;
}

.panel h2 {
    margin: 0 0 18px;
    font-size: 19px;
}

.donut {
    width: 190px;
    height: 190px;
    margin: 12px auto 20px;
    border-radius: 50%;
    background:
        conic-gradient(
            var(--ready) 0 $ready_percentage%,
            #e9a23b $ready_percentage% 100%
        );
    position: relative;
}

.donut::after {
    content: "";
    position: absolute;
    inset: 32px;
    border-radius: 50%;
    background: var(--surface);
}

.donut-label {
    position: absolute;
    inset: 0;
    z-index: 1;
    display: grid;
    place-content: center;
    text-align: center;
    font-size: 28px;
    font-weight: 700;
}

.donut-label span {
    display: block;
    margin-top: 4px;
    color: var(--muted);
    font-size: 12px;
    font-weight: 500;
}

.legend {
    display: grid;
    gap: 10px;
}

.legend-item {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
}

.filters {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 18px;
}

select,
input {
    min-width: 210px;
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: white;
    font: inherit;
}

.chart-row {
    display: grid;
    grid-template-columns: 260px 1fr 76px;
    align-items: center;
    gap: 12px;
    margin: 12px 0;
}

.chart-label {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 13px;
}

.bar-track {
    height: 14px;
    border-radius: 8px;
    background: #edf0f4;
    overflow: hidden;
}

.bar {
    height: 100%;
    border-radius: 8px;
}

.bar.positive {
    background: var(--accent);
}

.bar.negative {
    background: var(--exception);
}

.chart-value {
    text-align: right;
    font-size: 13px;
    font-weight: 600;
}

.table-panel {
    margin-top: 18px;
    overflow: hidden;
}

.table-scroll {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 1200px;
}

th {
    background: #f8f9fb;
    color: #344054;
    font-size: 12px;
    text-align: left;
    padding: 12px;
    border-bottom: 1px solid var(--border);
}

td {
    padding: 12px;
    border-bottom: 1px solid #eaecf0;
    font-size: 13px;
    vertical-align: top;
}

.badge {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
}

.badge-ready {
    color: var(--ready);
    background: #e8f5ee;
}

.badge-hold {
    color: var(--hold);
    background: #fff1dc;
}

.badge-exception {
    color: var(--exception);
    background: #feeceb;
}

.empty {
    padding: 26px;
    color: var(--muted);
    text-align: center;
}

.footer {
    margin-top: 18px;
    color: var(--muted);
    font-size: 12px;
    text-align: center;
}

@media (max-width: 1000px) {
    .cards {
        grid-template-columns: repeat(2, 1fr);
    }

    .grid {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>
<main class="dashboard">

<section class="header">
    <h1>Quarter-End Sustainability Reporting Dashboard</h1>

    <p>
        Assurance-ready reporting view linking KPI ownership,
        source evidence, automated validation, exception
        management, variance review and formal sign-off.
    </p>

    <div class="meta">
        Reporting period: 2026 Q2 |
        Generated: $generated_at |
        Controlled source:
        data/processed/dashboard_kpi_dataset.csv
    </div>
</section>

<section class="cards">
    <article class="card">
        <div class="card-label">KPI records</div>
        <div class="card-value">$total_kpis</div>
    </article>

    <article class="card">
        <div class="card-label">Ready to report</div>
        <div class="card-value">$ready_kpis</div>
    </article>

    <article class="card">
        <div class="card-label">On hold</div>
        <div class="card-value">$hold_kpis</div>
    </article>

    <article class="card">
        <div class="card-label">Approved KPIs</div>
        <div class="card-value">$approved_kpis</div>
    </article>

    <article class="card">
        <div class="card-label">Validation exceptions</div>
        <div class="card-value">$total_exceptions</div>
    </article>
</section>

<section class="grid">

<article class="panel">
    <h2>Reporting readiness</h2>

    <div class="donut">
        <div class="donut-label">
            $ready_percentage%
            <span>ready to report</span>
        </div>
    </div>

    <div class="legend">
        <div class="legend-item">
            <span>Ready to report</span>
            <strong>$ready_kpis</strong>
        </div>

        <div class="legend-item">
            <span>On hold or under review</span>
            <strong>$hold_kpis</strong>
        </div>
    </div>
</article>

<article class="panel">
    <h2>Period-on-period KPI movements</h2>

    <div class="filters">
        <select id="categoryFilter">
            <option value="">All categories</option>
        </select>

        <select id="readinessFilter">
            <option value="">All readiness statuses</option>
        </select>

        <input
            id="searchFilter"
            type="search"
            placeholder="Search KPI or owner"
        >
    </div>

    <div id="movementChart"></div>
</article>

</section>

<section class="panel table-panel">
    <h2>KPI control and sign-off register</h2>

    <div class="table-scroll">
        <table>
            <thead>
                <tr>
                    <th>KPI</th>
                    <th>Category</th>
                    <th>Current</th>
                    <th>Prior</th>
                    <th>Movement</th>
                    <th>Owner</th>
                    <th>Evidence</th>
                    <th>Approval</th>
                    <th>Exceptions</th>
                    <th>Readiness</th>
                </tr>
            </thead>

            <tbody id="dashboardTable"></tbody>
        </table>
    </div>
</section>

<div class="footer">
    Illustrative portfolio data. This dashboard is not an
    external assurance opinion.
</div>

</main>

<script>
const rows = $data_json;

const categoryFilter =
    document.getElementById("categoryFilter");

const readinessFilter =
    document.getElementById("readinessFilter");

const searchFilter =
    document.getElementById("searchFilter");

function uniqueValues(field) {
    return [...new Set(
        rows.map(row => row[field]).filter(Boolean)
    )].sort();
}

function addOptions(selectElement, values) {
    values.forEach(value => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        selectElement.appendChild(option);
    });
}

addOptions(
    categoryFilter,
    uniqueValues("category")
);

addOptions(
    readinessFilter,
    uniqueValues("reporting_readiness")
);

function filteredRows() {
    const category =
        categoryFilter.value;

    const readiness =
        readinessFilter.value;

    const search =
        searchFilter.value.trim().toLowerCase();

    return rows.filter(row => {
        const categoryMatch =
            !category || row.category === category;

        const readinessMatch =
            !readiness ||
            row.reporting_readiness === readiness;

        const searchText = (
            row.kpi_id + " " +
            row.kpi_name + " " +
            row.data_owner
        ).toLowerCase();

        return (
            categoryMatch &&
            readinessMatch &&
            (!search || searchText.includes(search))
        );
    });
}

function readinessBadge(status) {
    const badgeClass =
        status === "Ready to report"
            ? "badge-ready"
            : "badge-hold";

    return (
        '<span class="badge ' +
        badgeClass +
        '">' +
        status +
        '</span>'
    );
}

function approvalBadge(status) {
    const badgeClass =
        status === "Approved"
            ? "badge-ready"
            : "badge-exception";

    return (
        '<span class="badge ' +
        badgeClass +
        '">' +
        status +
        '</span>'
    );
}

function renderChart(data) {
    const chart =
        document.getElementById("movementChart");

    if (!data.length) {
        chart.innerHTML =
            '<div class="empty">No matching KPI records.</div>';
        return;
    }

    const maxMovement = Math.max(
        ...data.map(
            row => Math.abs(
                Number(row.movement_percent || 0)
            )
        ),
        1
    );

    chart.innerHTML = data.map(row => {
        const movement =
            Number(row.movement_percent || 0);

        const width =
            Math.max(
                Math.abs(movement) / maxMovement * 100,
                2
            );

        const directionClass =
            movement >= 0
                ? "positive"
                : "negative";

        return (
            '<div class="chart-row">' +
                '<div class="chart-label" title="' +
                    row.kpi_name +
                '">' +
                    row.kpi_name +
                '</div>' +
                '<div class="bar-track">' +
                    '<div class="bar ' +
                        directionClass +
                        '" style="width:' +
                        width +
                        '%"></div>' +
                '</div>' +
                '<div class="chart-value">' +
                    movement.toFixed(2) +
                    '%' +
                '</div>' +
            '</div>'
        );
    }).join("");
}

function renderTable(data) {
    const table =
        document.getElementById("dashboardTable");

    if (!data.length) {
        table.innerHTML =
            '<tr><td colspan="10" class="empty">' +
            'No matching KPI records.' +
            '</td></tr>';
        return;
    }

    table.innerHTML = data.map(row => {
        const exceptions =
            Number(row.exception_count || 0);

        return (
            "<tr>" +
                "<td><strong>" +
                    row.kpi_id +
                    "</strong><br>" +
                    row.kpi_name +
                "</td>" +
                "<td>" +
                    row.category +
                "</td>" +
                "<td>" +
                    row.current_value +
                    " " +
                    row.unit +
                "</td>" +
                "<td>" +
                    row.prior_value +
                    " " +
                    row.unit +
                "</td>" +
                "<td>" +
                    Number(
                        row.movement_percent || 0
                    ).toFixed(2) +
                    "%" +
                "</td>" +
                "<td>" +
                    row.data_owner +
                "</td>" +
                "<td>" +
                    row.evidence_reference +
                    "<br>" +
                    row.evidence_review_status +
                "</td>" +
                "<td>" +
                    approvalBadge(
                        row.approval_status
                    ) +
                "</td>" +
                "<td>" +
                    exceptions +
                    (
                        row.controls_failed
                            ? "<br>" +
                              row.controls_failed
                            : ""
                    ) +
                "</td>" +
                "<td>" +
                    readinessBadge(
                        row.reporting_readiness
                    ) +
                "</td>" +
            "</tr>"
        );
    }).join("");
}

function render() {
    const data = filteredRows();
    renderChart(data);
    renderTable(data);
}

categoryFilter.addEventListener(
    "change",
    render
);

readinessFilter.addEventListener(
    "change",
    render
);

searchFilter.addEventListener(
    "input",
    render
);

render();
</script>

</body>
</html>
"""
    )

    return template.substitute(
        generated_at=generated_at,
        total_kpis=total_kpis,
        ready_kpis=ready_kpis,
        hold_kpis=hold_kpis,
        approved_kpis=approved_kpis,
        total_exceptions=total_exceptions,
        ready_percentage=ready_percentage,
        data_json=data_json,
    )


def main() -> None:
    rows = read_dataset()
    dashboard = build_dashboard(rows)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        dashboard,
        encoding="utf-8",
    )

    print("HTML DASHBOARD CREATED")
    print("======================")
    print(f"Records displayed: {len(rows)}")
    print(
        "Output file: "
        "outputs/sustainability_dashboard.html"
    )


if __name__ == "__main__":
    main()