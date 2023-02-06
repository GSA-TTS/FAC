# 15. Store uploaded Excel files

Date: 2023-02-06

## Status

Accepted

## Context

The FAC needs to allow users to asynchronously collaborate on in-progress report submissions, where one user completes part of the submission and another user continues working on it.

The users typically work in Excel, and we have explored a number of options for extracting information from Excel and then recreating Excel files for users to download in order to continue working on submissions

We conducted research exploring different implementation options, including:

- [Using XBRL/Arelle](https://github.com/GSA-TTS/FAC/issues/755) to convert between our SingleAuditChecklist schema and an Excel workbook.
- [Using a combination of ExcelJS and JSON Schema](0011-excel-generation-validation.md) to dynamically generate Excel workbooks and extract/validate their contents during submission.

In summary, requiring full bi-directional Excel–database translation is a major feature in itself that would slow our ability to make incremental progress towards the MVP, so in the short term we are proceeding with storing Excel files and allowing users to retrieve them.

This applies only to in-progress submissions; once a submission is finalized, users will not be able to to upload Excel files as part of the typical workflow.

## Decision

Excel files will be uploaded using the same [file uploading infrastructure](0010-file-uploads.md) that we will use for attachments. Once uploaded, the contents of the file will be extracted and [validated](#validation).

If the contents are valid, the Excel file will be stored in a private S3 bucket (and only authorized users will be able to access the file in that bucket).

If the contents are insufficiently valid, the validation errors will be returned to the user so that they can address the issues.

If the contents aren’t fully valid but are sufficient for storage, the user will receive some warnings about the issues but the file will still be stored.

We will make the latest version of the Excel file available to all users authorized to work on the submission. Any user may upload a new file, which will replace the file associated with that submission—**this is a last-write wins environment**.

Last-write-wins here also applies to the submission data we store in our database; if an uploaded file passes the first five levels of validation below, we update the database to match the contents of that most-recently-uploaded file.

### Validation
-   Validation on the client side—is this file under some size limit, and does it have the correct extension? `JavaScript`.
    - Rejection here: file not uploaded.
-   Validation at the security level—is this file safe? `ClamAV`.
    - Rejection here: file not stored.
-   Validation at the basic level—is this a valid Excel file? `openpyxl`.
    - Rejection here: file not stored.
-   Validation at the type level—are you answering integer questions with integer values? Custom code.
    - Rejection here: file stored, with warning? This is a product decision.
-   Validation at the inter-question level—if you answered Y to question 1, does your answer to question 1b make sense in light of that? Custom code.
    - Rejection here: file stored, with warning? This is a product decision.
-   **If the Excel file passes the above validations levels, the data will be extracted and stored in our database**.
-   Validation at the finalization level—is this submission ready to be certified? Custom code.
    - Rejection here: file stored, possibly without a warning, as certification is a specific step and full check for finalization-readiness is a specific stage. The data will still be stored in the database in the case of validation failure here.

## Consequences

- Allows end-to-end Excel workflow to progress without having to figure out Excel generation.
- We will need to build and maintain the Excel templates because they won't be generated
- We will need to update the `Access` models to accommodate this; since there should be one Excel file per `SingleAuditChecklist` instance, this should be tractable.
- We will need to add file upload and download to our Django views, and handle the above validation logic.
- We will need to add the `ClamAV` functionality.
- In the future, if we insist on storing Excel files, we will need to follow various retention policy requirements regarding them.
