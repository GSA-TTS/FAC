# 11. Store Question Copy as JSON

Date: 2022-09-15

## Status

Pending

## Context

Question copy needs to be stored in a way that allows the copy for a particular question to vary by year, while preserving our ability to render forms from prior years with the original text, as well as to associate conceptually equivalent fields across years even if the question text changes. 

## Decision

Question copy will be stored in a JSON format, with a disctint file for each year:

```
| backend/
| --- questions/
|     --- 2020.json
|     --- 2021.json
|     --- 2022.json
```

Internally, each file will contain a single JSON dictionary, which maps a stable question ID to the appropriate question copy for that particular year. Each file will contain data only for the set of questions that are part of that year's form. For example, starting in 2022, the form began using an auditee UEI in place of an EIN. Therefore, the post-2022 question files will only contain the question copy for `auditee-uei`, and will not have an entry for `auditee-ein`. It may prove necessary or desirable to prefix question IDs with their form section number:

```
{
  "01-organization-type": "Which organizational type best describes this entity?",
  "01-met-spending-threshold": "Did this entity spend $750,000 or more in federal awards during its audit period in accordance with Uniform Guidance?",
  "01-is-usa-based": "Is this entity based in a US State, Territory, or Commonwealth?",
  "02-auditee-name": "Auditee Name",
  "02-auditee_fiscal_period_start": "Auditee fiscal period start for this submission",
  "03-auditee-uei": "Auditee Unique Entity Identifier (UEI)"
}
```

## Consequences

- The JSON files containing the question copy for each year will be the source of truth for this data, though it will likely appear elsewhere in the code base. Specifically, the question copy may be included as part of the validation schema for audit submissions. The generation of these schemas should be configured to automatically pull the question copy from these JSON files to avoid having to keep multiple question sources synchronized.
- Question IDs should remain the same if/when the copy associated with the question changes. This is what will allow us to merge conceptually equivalent fields across years in a later step, facilitating a better search & presentation experience for public audit report access.