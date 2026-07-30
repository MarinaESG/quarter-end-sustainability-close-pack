# Quarter-End Sustainability Reporting Close Pack

An assurance-ready sustainability reporting portfolio project demonstrating how quarterly ESG and sustainability KPI data can be collected, validated, evidenced, reviewed and approved through a controlled reporting process.

## Portfolio statement

I built an assurance-ready quarter-end sustainability reporting close pack that links KPI ownership, source evidence, automated validation, exception management, variance review and formal sign-off within a version-controlled reporting workflow.

## Project objective

This project simulates the work performed by a sustainability reporting analyst during a quarter-end reporting close.

It converts sustainability data into a controlled reporting process with:

- Defined KPI ownership
- Source-system traceability
- Evidence references
- Automated validation checks
- Period-on-period variance review
- Exception management
- Reviewer challenge
- Formal approval and sign-off
- Version-controlled reporting files

## Business scenario

The close pack covers eight illustrative environmental KPIs for the 2026 Q2 reporting period:

- Scope 1 greenhouse gas emissions
- Scope 2 location-based emissions
- Scope 2 market-based emissions
- Scope 3 purchased goods and services
- Total energy consumption
- Total water withdrawal
- Total waste generated
- Waste diverted from disposal

The dataset contains current-period values, prior-period comparatives, named data owners, source systems, evidence references and approval status.

## Reporting workflow

1. Data owners submit KPI values and supporting evidence.
2. Evidence references and source systems are recorded.
3. Automated validation controls are run.
4. Exceptions are recorded and assigned for investigation.
5. Material movements receive documented review.
6. Evidence is reviewed for completeness and traceability.
7. KPI reviewers challenge and approve reported values.
8. Final reporting files and sign-offs are retained as an audit trail.

## Automated controls

The Python validation script performs the following checks:

| Control | Purpose |
|---|---|
| Completeness | Identifies missing mandatory reporting fields |
| Uniqueness | Detects duplicate KPI identifiers |
| Evidence traceability | Checks evidence-reference formatting |
| Approval workflow | Flags KPIs that are pending or under review |
| Numeric validity | Detects non-numeric or negative values |
| Percentage range | Checks that percentage KPIs are between 0 and 100 |
| Period-on-period movement | Flags movements exceeding the 20% review threshold |
| Date validity | Checks that dates use the YYYY-MM-DD format |

## Validation result

The illustrative dataset contains eight KPI records.

The automated validation identified four medium-severity exceptions:

- Scope 2 market-based emissions remain pending approval.
- Scope 2 market-based emissions changed by more than the 20% review threshold.
- Scope 3 purchased goods and services remains under review.
- Waste diverted from disposal remains pending approval.

No high-severity exceptions were identified.

## Repository structure

```text
quarter-end-sustainability-close-pack
├── data
│   ├── raw
│   │   └── sample_kpi_data.csv
│   └── processed
├── documentation
│   └── control_framework.md
├── evidence
│   ├── evidence_register.csv
│   └── sign_off_register.csv
├── outputs
│   ├── validation_results.csv
│   └── validation_summary.txt
├── src
│   └── validate_kpis.py
├── .gitignore
├── LICENSE
└── README.md