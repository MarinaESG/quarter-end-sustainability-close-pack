from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "raw" / "sample_kpi_data.csv"
OUTPUT_FILE = ROOT / "outputs" / "validation_results.csv"
SUMMARY_FILE = ROOT / "outputs" / "validation_summary.txt"

REQUIRED_FIELDS = [
    "reporting_period",
    "kpi_id",
    "kpi_name",
    "category",
    "unit",
    "current_value",
    "prior_value",
    "data_owner",
    "evidence_reference",
    "approval_status",
    "source_system",
    "last_updated",
]

VALID_APPROVAL_STATUSES = {
    "Approved",
    "Pending",
    "Under Review",
}

MOVEMENT_THRESHOLD = 0.20


def add_issue(
    issues: list[dict[str, str]],
    row_number: int,
    kpi_id: str,
    severity: str,
    control: str,
    message: str,
) -> None:
    """Add one validation exception to the exception log."""

    issues.append(
        {
            "row_number": str(row_number),
            "kpi_id": kpi_id,
            "severity": severity,
            "control": control,
            "message": message,
        }
    )


def validate() -> tuple[list[dict[str, str]], int]:
    """Run reporting-control checks against the KPI dataset."""

    issues: list[dict[str, str]] = []
    seen_kpi_ids: set[str] = set()

    with INPUT_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("The CSV file has no header row.")

        missing_columns = [
            field for field in REQUIRED_FIELDS
            if field not in reader.fieldnames
        ]

        if missing_columns:
            raise ValueError(
                "Missing required columns: " + ", ".join(missing_columns)
            )

        rows = list(reader)

    for row_number, row in enumerate(rows, start=2):
        kpi_id = row.get("kpi_id", "").strip() or "UNKNOWN"

        # Control 1: completeness
        for field in REQUIRED_FIELDS:
            if not row.get(field, "").strip():
                add_issue(
                    issues,
                    row_number,
                    kpi_id,
                    "High",
                    "Completeness",
                    f"Required field '{field}' is blank.",
                )

        # Control 2: unique KPI identifiers
        if kpi_id in seen_kpi_ids:
            add_issue(
                issues,
                row_number,
                kpi_id,
                "High",
                "Uniqueness",
                "Duplicate KPI ID detected.",
            )

        seen_kpi_ids.add(kpi_id)

        # Control 3: evidence-reference format
        evidence_reference = row.get(
            "evidence_reference", ""
        ).strip()

        if (
            evidence_reference
            and not evidence_reference.startswith("EVID-")
        ):
            add_issue(
                issues,
                row_number,
                kpi_id,
                "Medium",
                "Evidence traceability",
                "Evidence reference should start with 'EVID-'.",
            )

        # Control 4: approval workflow
        approval_status = row.get(
            "approval_status", ""
        ).strip()

        if approval_status not in VALID_APPROVAL_STATUSES:
            add_issue(
                issues,
                row_number,
                kpi_id,
                "High",
                "Approval workflow",
                f"Unexpected approval status: '{approval_status}'.",
            )

        elif approval_status != "Approved":
            add_issue(
                issues,
                row_number,
                kpi_id,
                "Medium",
                "Approval workflow",
                (
                    "KPI is not fully approved; current status is "
                    f"'{approval_status}'."
                ),
            )

        # Controls 5–7: numeric validity, range and movement
        try:
            current_value = float(row["current_value"])
            prior_value = float(row["prior_value"])

            if current_value < 0 or prior_value < 0:
                add_issue(
                    issues,
                    row_number,
                    kpi_id,
                    "High",
                    "Value validity",
                    "Current and prior values must not be negative.",
                )

            if prior_value != 0:
                movement = (
                    current_value - prior_value
                ) / abs(prior_value)

                if abs(movement) > MOVEMENT_THRESHOLD:
                    add_issue(
                        issues,
                        row_number,
                        kpi_id,
                        "Medium",
                        "Period-on-period movement",
                        (
                            f"Movement of {movement:.1%} exceeds the "
                            f"{MOVEMENT_THRESHOLD:.0%} review threshold."
                        ),
                    )

            elif current_value != 0:
                add_issue(
                    issues,
                    row_number,
                    kpi_id,
                    "Medium",
                    "Period-on-period movement",
                    (
                        "Prior value is zero while the current value "
                        "is non-zero."
                    ),
                )

            if row.get("unit", "").strip().lower() == "percent":
                if not 0 <= current_value <= 100:
                    add_issue(
                        issues,
                        row_number,
                        kpi_id,
                        "High",
                        "Percentage range",
                        "Percentage KPI must be between 0 and 100.",
                    )

        except ValueError:
            add_issue(
                issues,
                row_number,
                kpi_id,
                "High",
                "Numeric validity",
                "Current value and prior value must be numeric.",
            )

        # Control 8: date format
        try:
            datetime.strptime(
                row.get("last_updated", "").strip(),
                "%Y-%m-%d",
            )

        except ValueError:
            add_issue(
                issues,
                row_number,
                kpi_id,
                "Medium",
                "Date validity",
                "last_updated must use YYYY-MM-DD format.",
            )

    return issues, len(rows)


def write_outputs(
    issues: list[dict[str, str]],
    row_count: int,
) -> None:
    """Write the detailed exception log and management summary."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "row_number",
        "kpi_id",
        "severity",
        "control",
        "message",
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(issues)

    severity_counts = {
        severity: sum(
            issue["severity"] == severity
            for issue in issues
        )
        for severity in ("High", "Medium", "Low")
    }

    summary = (
        "SUSTAINABILITY KPI VALIDATION SUMMARY\n"
        "=====================================\n"
        f"Input records reviewed: {row_count}\n"
        f"Total exceptions: {len(issues)}\n"
        f"High-severity exceptions: "
        f"{severity_counts['High']}\n"
        f"Medium-severity exceptions: "
        f"{severity_counts['Medium']}\n"
        f"Low-severity exceptions: "
        f"{severity_counts['Low']}\n"
        f"Detailed exception log: "
        f"{OUTPUT_FILE.relative_to(ROOT)}\n"
    )

    SUMMARY_FILE.write_text(
        summary,
        encoding="utf-8",
    )

    print(summary)


def main() -> None:
    """Run the complete validation process."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    issues, row_count = validate()
    write_outputs(issues, row_count)


if __name__ == "__main__":
    main()