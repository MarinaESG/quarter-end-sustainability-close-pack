from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

KPI_FILE = ROOT / "data" / "raw" / "sample_kpi_data.csv"
EVIDENCE_FILE = ROOT / "evidence" / "evidence_register.csv"
SIGN_OFF_FILE = ROOT / "evidence" / "sign_off_register.csv"
EXCEPTIONS_FILE = ROOT / "outputs" / "validation_results.csv"

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "dashboard_kpi_dataset.csv"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV file and return its records."""

    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def calculate_movement(
    current_value: str,
    prior_value: str,
) -> float | None:
    """Calculate percentage movement from prior to current value."""

    current = float(current_value)
    prior = float(prior_value)

    if prior == 0:
        return None

    return ((current - prior) / abs(prior)) * 100


def determine_readiness(
    approval_status: str,
    exception_count: int,
) -> str:
    """Assign a reporting-readiness status."""

    if approval_status == "Pending":
        return "Hold - Pending approval"

    if approval_status == "Under Review":
        return "Hold - Under review"

    if approval_status != "Approved":
        return "Hold - Invalid approval status"

    if exception_count > 0:
        return "Approved - Review exceptions"

    return "Ready to report"


def build_dashboard_dataset() -> list[dict[str, str]]:
    """Join reporting, evidence, sign-off and exception data."""

    kpi_rows = read_csv(KPI_FILE)
    evidence_rows = read_csv(EVIDENCE_FILE)
    sign_off_rows = read_csv(SIGN_OFF_FILE)
    exception_rows = read_csv(EXCEPTIONS_FILE)

    evidence_by_kpi = {
        row["kpi_id"]: row
        for row in evidence_rows
    }

    sign_off_by_kpi = {
        row["kpi_id"]: row
        for row in sign_off_rows
    }

    exceptions_by_kpi: dict[
        str,
        list[dict[str, str]],
    ] = defaultdict(list)

    for exception in exception_rows:
        exceptions_by_kpi[exception["kpi_id"]].append(
            exception
        )

    dashboard_rows: list[dict[str, str]] = []

    for kpi in kpi_rows:
        kpi_id = kpi["kpi_id"]
        evidence = evidence_by_kpi.get(kpi_id, {})
        sign_off = sign_off_by_kpi.get(kpi_id, {})
        exceptions = exceptions_by_kpi.get(kpi_id, [])

        high_count = sum(
            issue["severity"] == "High"
            for issue in exceptions
        )

        medium_count = sum(
            issue["severity"] == "Medium"
            for issue in exceptions
        )

        movement = calculate_movement(
            kpi["current_value"],
            kpi["prior_value"],
        )

        approval_status = sign_off.get(
            "approval_status",
            kpi["approval_status"],
        )

        controls_failed = sorted(
            {
                issue["control"]
                for issue in exceptions
            }
        )

        dashboard_rows.append(
            {
                "reporting_period": kpi["reporting_period"],
                "kpi_id": kpi_id,
                "kpi_name": kpi["kpi_name"],
                "category": kpi["category"],
                "unit": kpi["unit"],
                "current_value": kpi["current_value"],
                "prior_value": kpi["prior_value"],
                "movement_percent": (
                    ""
                    if movement is None
                    else f"{movement:.2f}"
                ),
                "data_owner": kpi["data_owner"],
                "source_system": kpi["source_system"],
                "evidence_reference": (
                    kpi["evidence_reference"]
                ),
                "evidence_type": evidence.get(
                    "evidence_type",
                    "",
                ),
                "source_document": evidence.get(
                    "source_document",
                    "",
                ),
                "evidence_review_status": evidence.get(
                    "review_status",
                    "",
                ),
                "reviewer": sign_off.get(
                    "reviewer",
                    "",
                ),
                "approval_status": approval_status,
                "review_date": sign_off.get(
                    "review_date",
                    "",
                ),
                "approval_date": sign_off.get(
                    "approval_date",
                    "",
                ),
                "exception_count": str(len(exceptions)),
                "high_exception_count": str(high_count),
                "medium_exception_count": str(medium_count),
                "controls_failed": "; ".join(
                    controls_failed
                ),
                "has_exception": (
                    "Yes" if exceptions else "No"
                ),
                "reporting_readiness": determine_readiness(
                    approval_status,
                    len(exceptions),
                ),
            }
        )

    return dashboard_rows


def write_dataset(rows: list[dict[str, str]]) -> None:
    """Write the processed dashboard dataset."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not rows:
        raise ValueError("No dashboard records were created.")

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = build_dashboard_dataset()
    write_dataset(rows)

    ready_count = sum(
        row["reporting_readiness"] == "Ready to report"
        for row in rows
    )

    hold_count = len(rows) - ready_count

    print("DASHBOARD DATASET CREATED")
    print("=========================")
    print(f"Output records: {len(rows)}")
    print(f"Ready to report: {ready_count}")
    print(f"On hold or requiring review: {hold_count}")
    print(
        "Output file: "
        "data/processed/dashboard_kpi_dataset.csv"
    )


if __name__ == "__main__":
    main()