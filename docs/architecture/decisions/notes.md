## Notes
- We can use separate models for the `SingleAuditChecklist` and the `SingleAuditChecklistReport` (submitted SACs)
- When a `SingleAuditChecklist` is submitted, it is translated into a `SingleAuditChecklistReport`
- The `SingleAuditChecklistReport` model does not vary by fiscal year - it is the same across all years to facilitate consisent search and presentation of completed audits
- `SingleAuditChecklists` are validated against a JSON Schema for that fiscal year


## Questions
- If we use JSON Schema to store the question copy and validation rules for a given form-year, is there a reason to have a database model for that data, or should we just store it as JSON?


## Proposal

Refactor the `SingleAuditChecklist` model so that SAC metadata (e.g. `report_id`, `fiscal_period_start/end`, `ein`, etc) are part of the model, and all remaining data is stored as a JSON blob:

### `SingleAuditChecklist`
| id | fiscal_year | report_id | ein | data (JSON) |
| -- | ----------- | --------- | --- | ---- |
| 1 | 2021 | 202100001 | ABC123XYZ | { ... } |
| 2 | 2022 | 202200002 | DEF456XYZ | { ... } |

Create a new model `SingleAuditChecklistTemplate` to hold the JSON Schema for each fiscal year, against which incoming submissions will be validated. The template can also hold the question copy for each field:

### `SingleAuditChecklistTemplate`
| id | fiscal_year | template (JSON Schema) |
| -- | ----------- | -------- |
| 1 | 2021 | { ... } |
| 2 | 2022 | { ... } |

Create new model `SingleAuditChecklistReport` to hold the normalized data for each submitted `SingleAuditChecklist`:

### `SingleAuditChecklistReport`
| id | fiscal_year | report_id | ein | met_spending_threshold | etc |
| -- | ----------- | --------- | --- | ---------------------- | --- |
| 1 | 2021 | 202100001 | ABC123XYZ | true | ... |
| 2 | 2022 | 202200001 | DEF456XYZ | true | ... |

For each fiscal year, create a translator to convert the validated form JSON into an instance of `SingleAuditChecklistReport`.

