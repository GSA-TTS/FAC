## Notes
- We can use separate models for the `SingleAuditChecklist` and the `SingleAuditChecklistReport` (submitted SACs)
- When a `SingleAuditChecklist` is submitted, it is translated into a `SingleAuditChecklistReport`
- The `SingleAuditChecklistReport` model does not vary by fiscal year - it is the same across all years to facilitate consisent search and presentation of completed audits
- `SingleAuditChecklists` are validated against a JSON Schema for that fiscal year
- Question and validation error copy for a given year will be stored as part of the `SingleAuditChecklist` JSON Schema


## Questions
- If we use JSON Schema to store the question copy and validation rules for a given form-year, is there a reason to have a database model for `SingleAuditCheclist` data, or should we just store it as JSON?
  - Downsides to maintaining a database model alongside a JSON Schema:
    - Each time a new JSON Schema is created for a new fiscal year, a new database model will also need to created, leading to a continually growing collection of models/database tables (e.g., `SingleAuditChecklist_2019`, `SingleAuditChecklit_2020`, `SingleAuditChecklist_2021`, etc)
    - Maintaining field/validation parity between the JSON Schema and database model for each year will be difficult and tedious to manage without introducing bugs


## Proposal

Refactor the `SingleAuditChecklist` model so that SAC metadata (e.g. `report_id`, `fiscal_period_start/end`, `ein`, etc) are part of the model, and all remaining data (i.e. the fields that are more likely change over time) is stored as a JSON blob:

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

