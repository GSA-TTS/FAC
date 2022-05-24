# 8. How to Handle Bulk Data Uploads

Date: 2022-05-13

## Status

Accepted

## Context

Much of the design and dev work on the AF-SAC form data entry is dependent on us having a clear sense of how we are enabling users to bulk upload data. We need to decide how we will do this in order to unblock the rest of SF-SAC form data entry work.

@jadudm created a [FAC XLSX (Excel) File Validator](https://github.com/GSA-TTS/FAC-xlsx-validator) spike. He built it in Electron (JS) and it uses the [npm library xlsx](https://www.npmjs.com/package/xlsx) to read in an Excel file that's dropped on the window. The library reads the file and produces an object representing a Common Spreadsheet Format (CSF) in memory, which can then be parsed with some simple validation rules for determining if we think the file is valid.

@jadudm's additional notes:
> * Electron is secondary to the ADR. I think we just need to decide/document that we are committed to consuming XLSX templates. The Electron piece is a red herring, because it suggests a desktop application. I would make that a separate ADR.
> * The second question, in terms of schema, should instead be "are we using SheetJS Community Edition" as our library for parsing and processing our templates.
>
>Granted, that might mean "this library defines the CSF," but... the important thing is that the library produces a well-documented, widely used JSON structure.
>
>So, instead of saying we'll define a schema (which I think has very specific meaning), I think we say "we'll use the Common Spreadsheet Format JSON object produced by SheetJS."
>
> Later, we could have an ADR that defines a subset of this, but for now, this would simplify the ADR to answering three things:

The final questions remaining from this issue:

1. Are we committed to ingesting a set of templates that are closely modeled on the existing templates provided by Census,
2. Are we using SheetJS as our parsing library, and
3. Are we using the CSF as defined by the SheetJS Community Edition as our spreadsheet representation.
4. Which, assuming (from our conversation) that the answer to every one of those questions is "yes," the ADR itself becomes a declaration of those facts.

## Decision

@geekygirlsarah read over this issue, reviewed [FAC-xlsx-validator](https://github.com/GSA-TTS/FAC-xlsx-validator), and reviewed the npm libraries the app uses. After this, she thinks we can declare:
* We can commit to ingesting a set of Excel templates similar to the current existing ones at Census
* Use SheetJS as a parsing library
* Use the [Common Spreadsheet Format](https://github.com/sheetjs/sheetjs#common-spreadsheet-format) (CSF) for representing the data

## Considerations:

* The CSF is a common format supported by all major spreadsheet applications
* The library works in-browser, so we can include a validator on the FAC site directly, without an Electron app download
* We can still use the legacy Census spreadsheet template if we wish

## Consequences

* It will be extra time to work on a practice validator on the site (similar to @jadudm's spike), and possibly should be moved until after the 10/1/2022 launch
* Accepting bulk data uploads is definitely within scope, but determining what "valid" file upload rules will take some time and possibly involve the Census developers to help figure that out