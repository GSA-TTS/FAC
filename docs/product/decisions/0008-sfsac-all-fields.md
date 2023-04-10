# 1. Require all fields in SF-SAC XLSX uploads

Introduced: 2023-04-10

## Status
For consideration

## Context

Much of the SF-SAC was, and will continue to be, submitted as spreadsheets.

However, users are not required to complete all of the fields in a spreadsheet row. This creates opportunities for user error, and therefore for data validation problems.

For example, consider that the SF-SAC "Federal Awards" template had a column that asks if the row is a load or loan guarantee. If the user answers `Y`, then they are required to complete additional columns. However, if they answer `N`, they can (optionally) leave the subsequent columns blank. Or, they could say `N/A`. (Different conditional columns also have different behavior in this regard, which is confusing.)

## Decision

Every column in every row should require a value.

In the above example, if the user answers `Y`, then the next few columns are obviously required (e.g. "loan amount remaining.") If they answer `N`, however, they should be *required* to enter `N/A`, `0`, or some other appropriate value in the related, remaining columns. In this regard, we are asking for auditors and auditees to positively confirm, without question, their answer to the relevant question. 

The problem with empty columns in a row is that we cannot tell the difference between a user who has *chosen* to leave the column blank vs. a user who *forgot* to enter a value. By requiring a positive action on every field, we increate the quality of the data in the FAC, and help users make fewer errors.

This does not change the reporting burden, as the fields already exist and had to be completed. 

## Consequences

Documentation will need to be updated, but it will become simpler: every field has values that **must** be present. There are no longer any **should** values.

This change makes some things explicit for users that may have been tacit in the past. 

Validation rules need to be refined, but this will be a simplification of existing rules.