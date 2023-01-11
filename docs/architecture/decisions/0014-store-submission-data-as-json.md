# 14. Store submission data as JSON

Date: 2023-01-04

## Status

Accepted

## Context

We need to store the data that users submit as part of their Single Audit Checklist packages. The storage mechanism needs to accomodate the following:
- The Single Audit Checklist schema can (and in fact does) change over time. These changes include the addition of new fields, the removal of deprecated fields, and adjustments to the field validation logic.
- The FAC needs to maintain the ability to accept and validate backdated submissions, using the schema and validation logic for the submission year (i.e. not the most recent schema/validation version).
- Users can choose to submit their audit package through a web form or by uploading an Excel file.

## Decision

We will partition the Single Audit Checklist data model into high-level sections, and store some or all of those sections in the database as JSON documents. The partitioning of the data model will align with the way the different sections are broken up during the submission process (e.g. the first two sections are "General Information" and "Federal Awards"). For each section that we opt to store as JSON, there will be a single database column that uses Django's built-in `JSONField` type. In addition, each section will have a [JSON Schema](https://json-schema.org/) document that fully specifies the validation rules for the section. The JSON Schema for each section will serve as the source of truth for the schema and validation rules.

## Consequences

* Year-over-year schema/validation rule changes won't necessarily require database migrations
* Schema and validation rules for sections stored as JSON will be portable to other systems
* Increased code base complexity resulting from schema and validation rules living outside the object-relational mapper
* Additional burden on developers to be familiar with JSON Schema
