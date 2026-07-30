# Sustainability KPI Control Framework

## Purpose

This project demonstrates how sustainability data can be converted into a controlled, traceable and assurance-ready reporting process.

The framework is designed to support quarterly sustainability reporting by defining KPI ownership, validation controls, evidence requirements, exception management and approval status.

## Reporting workflow

1. KPI data is submitted by the named data owner.
2. Source-system and evidence references are recorded.
3. Automated validation checks are performed.
4. Exceptions are recorded in the validation log.
5. Data owners investigate and resolve exceptions.
6. Reviewers confirm that supporting evidence is complete.
7. KPIs receive formal approval before reporting.
8. Final outputs are retained as part of the reporting evidence pack.

## Key controls

| Control | Objective | Validation performed | Evidence |
|---|---|---|---|
| Completeness | Ensure all required reporting fields are populated | Checks mandatory fields for blanks | KPI dataset and exception log |
| Uniqueness | Prevent duplicate KPI records | Checks for duplicate KPI IDs | Validation results |
| Evidence traceability | Link each KPI to supporting documentation | Checks evidence-reference format | Evidence register |
| Approval workflow | Prevent unapproved data from entering final reporting | Flags Pending and Under Review records | Approval status and sign-off |
| Numeric validity | Detect invalid or non-numeric values | Tests current and prior-period values | Validation results |
| Value range | Identify impossible values | Checks negative values and percentage ranges | Exception log |
| Period-on-period movement | Identify unusual changes requiring explanation | Flags movements above a 20% threshold | Variance commentary |
| Date validity | Ensure consistent reporting dates | Checks YYYY-MM-DD format | Source-data record |

## Exception-management process

Each exception should include:

- KPI identifier
- Reporting-period row number
- Control that failed
- Severity
- Description of the issue
- Assigned owner
- Root-cause analysis
- Corrective action
- Resolution evidence
- Reviewer sign-off

High-severity exceptions should prevent the KPI from being reported until resolved. Medium-severity exceptions require documented review and approval.

## Roles and responsibilities

### Data owner

Provides the KPI value, source-system information and supporting evidence. Investigates exceptions and documents corrective action.

### Sustainability reporting analyst

Runs validation controls, maintains the exception log, performs reconciliations and prepares the reporting close pack.

### KPI reviewer

Challenges material movements, verifies evidence and confirms that the KPI is suitable for reporting.

### Reporting approver

Provides final sign-off and accepts responsibility for the reported value.

## Assurance readiness

The close pack supports assurance by preserving:

- Defined KPI ownership
- Source-system traceability
- Evidence references
- Automated validation results
- Exception history
- Review status
- Approval and sign-off
- Version-controlled reporting files

This creates a repeatable audit trail from the reported KPI back to the original source evidence.