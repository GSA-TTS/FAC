# 11. Excel Generation and Validation

Date: 2022-08-23

## Status

Pending review

## Context

The process for submitting entries to the FAC relies on uploading audit data via Excel templates. Design has been clear that this is so critical to workflows that it's a priority over web forms and could actually be done in place of them for MVP. There is already an accepted PDR for ["how to handle bulk data uploads"](https://github.com/GSA-TTS/FAC/blob/main/docs/architecture/decisions/0008-bulk-data-uploads.md) which uncovered an Excel File validator as well as a corresponding spike in that effort. The part that we don't have clarity around, which is the subject of this ADR, is creating Excel file templates.

### Regarding maintainability:

The Excel process under discussion would have at least three levels of validation:

1. The backend validation rules: any SAC submitted, regardless of how it is submitted, must pass backend validation.
2. The frontend validation rules: the frontend libraries being used to translate Excel into JSON for submission need to validate that JSON and flag errors before anything is submitted to the backend.
3. The Excel validation rules: the Excel files need to contain validation rules so that users know within Excel that their entries are valid or have errors.

### Ticket acceptance criteria:

1. We have identified a solution or set of solutions that meets the maintainability criteria laid out above.
2. Compared a few libraries for excel file generation and considered security/compliance considerations.
3. Consider the complexity of current excel templates / validation when making a recommendation
4. Estimate effort various approaches
5. (as a team) Compare estimates with user needs and make a technology decision for MVP

## Decisions

1. We believe sticking with one library to do everything (for the frontend and/or backend) will reduce the overhead needed to learn and work with Excel files. 
2. We believe that having one "source of truth" for all validation rules for exporting or importing data via Excel files will be best for the project. 
3. We believe that finding a frontend/JavaScript library to deal with Excel files will be the better way to approach the problem of generation and validation. The frontend can get the data needed from the backend API, generate the file, and send it to the user. Similarly, a file can be uploaded and read via JS, parse out the data it needs from the validation rules, then send just the data to the backend API. (A file could still be saved on the backend if desired, but don't make Python process the file.) This results in one place to deal with the Excel files.
4. We believe [ExcelJS](https://www.npmjs.com/package/exceljs) to be the best JS library to work with Excel files. It offers the ability to import and export CSV and XLSX files, work with cell-level validation, conditional formatting, cell formatting, and has easily readable and usable code. It is also open source and has most recent activity merged in from Nov 2021.
5. After reviewing some of the generated templates used on the old FAC system, we believe the cell validations they use are rather simplistic, and are easily carried over into the newer FAC. Also taking a template and customizing it by adding user/organization information to it is a simple process with ExcelJS. Therefore, integrating this type of Excel validation should be a low hurdle to be implemented on the new system.
6. We think there needs to be one method to store validation rules so it can be used by the frontend and backend to know what to insert into or export from Excel files. We believe JSON Schema _could_ be a way to store the rules. The format can be read by JS and Python, but we have not tested it enough to ensure it would meet our needs.
7. We are unable to really estimate various approaches right now as much of _how_ the FAC will be filled out, will be stored, and will be processed on the backend hasn't been determined yet. However, we believe once those have started to be determined, it should be a reasonably small burden to add Excel validation and/or file generation to those workflows.
8. We have not met as a team to estimate user needs yet.


## Consequences

1. We need to determine how the user will (from the frontend) fill out the forms and where they would be able to get one of these Excel templates. That will determine how and where the code to do the generation would be and how it'd integrate.
2. We need to determine how the system will save data on the backend. This will determine what kind of data we need to get from the Excel file and save to the backend. 
3. Depending on how we decide to move forward regarding UEI status and associated data (received from Sam.gov, manually typed in, etc.) may have an impact on how the files are generated.
4. Depending on how this is implemented along with the rest of the FAC workflow, it may require some user research to determine the best way to do it.
5. We could reuse Census' old template, or we could make our own. If we make our own, it may also involve user research and/or policy revisions to make sure it's adequate for the needs of all users involved (like auditors, auditees, processors, etc.)
6. Given the flow of processing Excel files on the frontend and sending the important data to the backend, Excel files won't ever get saved. This means the concerns of the File Upload ADR won't apply here.
7. If a validation rule system (like JSON Schema) was used, it would have to be independent of Django's ORM models. This means updates to one would have to also be applied to the other. If this is not done, they would be out of sync and/or invalid data could be passed back and forth.
8. A validation rule system might also mean needing two schemas, one for a finalized submission and one for an in-progress submission, as we allow parts of the form to be filled out at a time.
9. Testing this would probably mean writing unit tests along with a JSON Schema (or other library) along with example JSON structures that validate both working and not working examples.
10. Testing Excel would probably mean providing some example files that pass and don't pass validation, then using the library and unit tests  to ensure the files extract data and match expected results.