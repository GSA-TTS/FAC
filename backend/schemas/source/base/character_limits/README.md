# Character Limits Info


## Overview

Character limits are used here (/schemas/) in generating the schemas for validation, and in the greater application (/report_submission/, /audit/) for web form fields and the like. 

Character limits were determined by pulling a large amount of data from a table and making a decision based on the stats.

1. Field length averages, medians, and min/max values were determined for string and int values.
    * Floats, or other value types, are initially set to zero.
2. Mins and maxes are separated into JSON to be included in this folder.
3. Character limits are determined based on the mins/maxes.
4. With outlier values, we use the average & median to make a decision.
    * Ex. The maximum length of 31439 in notes_to_sefa.accounting_policies, when the average & median are about 500.

**Most character limits will be unused initially. Maybe forever. Many fields do not have variable length, or their length is decided by factors other than user input.**

## Notes on Particular Fields:

### Names
    Minimum - 2
    Maximum - 100
The max with CENSUS data seemed to be 100. Kept for consistency.

### Emails
    Minimum - 6 
    Maximum - 320
'a@a.a' is 5, but names have a minimum of 2. So, 'aa@a.a' is the minimum at 6.
The max of 320 is standard (RFC 5321 and RFC 5322).

### UEIs
    Minimum - 12
    Maximum - 13
UEIs are of length 12. But we have lots of 'GSA_MIGRATION' UEIs, which are of length 13.

### ZIP Codes
    Minimum - 5
    Maximum - 9
Either in format '12345' OR '12345-6789' with the dash removed.

### Auditor Country
    Minimum - 2
    Maximum - 56
Allows for the shortest acronyms. The longest possible is "The United Kingdom of Great Britain and Northern Ireland" at length 56.

### GAAP Results
    Minimum - 15
    Maximum - 77
The shortest possible result is just "adverse_opinion" at length 15.
The longest possible result is every option - "unmodified_opinion, qualified_opinion, adverse_opinion, disclaimer_of_opinion" at length 77.

### Audit Type
    Minimum - 12
    Maximum - 16
Shortest is "single-audit" at 12. Longest is "program-specific" at 16

### Yes/No Fields:
    is_going_concern_included
    is_internal_control_deficiency_disclosed
    is_internal_control_material_weakness_disclosed
    is_material_noncompliance_disclosed
    is_low_risk_auditee
    is_aicpa_audit_guide_included
    is_additional_ueis
    is_multiple_eins
    is_secondary_auditors
Always of length 3 or 2 ("Yes" or "No")

### Static Length Fields:
    Report IDs - 25
    Dates - 10
    EINs - 9
    Cognizant/Oversight Agency - 2