# 45. Multiple EINs and Secondary Auditors API Inconsistency

Date: 2025-07-10

## Status

Accepted

## Areas of impact

*   Engineering
*   Policy

## Related resources

*   ADR Issue: https://github.com/GSA-TTS/FAC/issues/5087
*   Inconsistency Issue: https://github.com/GSA-TTS/FAC/issues/5045
*   Resolving PR: https://github.com/GSA-TTS/FAC/pull/5058
*   Further write-up (internal only): https://docs.google.com/document/d/1CAI5z01sCYvvLnprJc5i5rCjAzSs8X-aMY97NVbMDrA/edit?tab=t.tjp1g2wsdtzy

## Context

We have some audits where the values around `secondary_auditors_exist` and `multiple_eins_covered` is inconsistent. The cause of the inconsistency is the same for both fields. Some audits have `false` values for `secondary_auditors_exist`. However, they also have entries in `dissemination_secondaryauditor`. Likewise, some audits have `false` values for `multiple_eins_covered` despite having entries in `dissemination_additionalein`.

This is caused by users selecting the relevant "Yes" option in the General Information page, then uploading the relevant workbook. Afterwards, the user came back and updated their answer as "No". The uploaded workbook carried through to dissemination. Now, there is a discrepancy between the "No" answer and the information that is given out via API and Search.

## Decision

### The answer in the General Information form takes precedence.

To get this inconsistency, the user selected "No" _after_ uploading the relevant workbook. Therefore, we determine that the General Information is "more correct". We will use this value as the truth moving forward. In the SOT migration scripts, we omit workbook data with a "No" answer. The SOT-based APIs are therefore correct.

### Validations prevent future inconsistencies.

Validations were introduced to block submissions with conflicting data. This validation already existed for `multiple_ueis_covered`, which is why it is the only of the three "Yes/No" questions to have no issues. 

Issue to validate Multiple EINs: https://github.com/GSA-TTS/FAC/issues/5049
Issue to validate Secondary Auditors: https://github.com/GSA-TTS/FAC/issues/5050
PR to introduce validations: https://github.com/GSA-TTS/FAC/pull/5056

### A curation action must fix old records.

For a `secondary_auditors_exist` value of False, these records have rows in `dissemination_secondaryauditor`:

| report_id                     | acceptance_date |
| ----------------------------- | --------------- |
| 2023-12-GSAFAC-0000037438	    | 2024-04-11      |
| 2023-06-GSAFAC-0000001071	    | 2023-11-12      |
| 2023-09-GSAFAC-0000010054	    | 2024-01-03      |
| 2023-06-GSAFAC-0000001127	    | 2023-11-14      |
| 2022-12-GSAFAC-0000013563	    | 2024-01-16      |
| 2023-06-GSAFAC-0000014239	    | 2024-02-05      |
| 2022-06-GSAFAC-0000000725	    | 2024-02-15      |
| 2023-12-GSAFAC-0000036995	    | 2024-04-10      |
| 2023-06-GSAFAC-0000033008	    | 2024-04-01      |
| 2023-06-GSAFAC-0000001201	    | 2024-04-29      |
| 2023-06-GSAFAC-0000030357	    | 2024-03-28      |
| 2023-12-GSAFAC-0000036850	    | 2024-04-10      |
| 2023-12-GSAFAC-0000036947	    | 2024-04-10      |
| 2023-12-GSAFAC-0000036990	    | 2024-04-10      |
| 2023-12-GSAFAC-0000036992	    | 2024-04-10      |
| 2023-06-GSAFAC-0000001188	    | 2024-05-30      |
| 2023-06-GSAFAC-0000001225	    | 2024-05-30      |


For a `multiple_eins_covered` value of False, these records have rows in `dissemination_additionalein`:

| report_id                     | acceptance_date |
| ----------------------------- | --------------- |
| 2023-06-GSAFAC-0000011123	    | 2023-12-21      |
| 2023-06-GSAFAC-0000019237	    | 2024-02-27      |
| 2024-06-GSAFAC-0000010871	    | 2023-12-14      |
| 2023-06-GSAFAC-0000017475	    | 2024-03-12      |
| 2023-03-GSAFAC-0000015691	    | 2024-01-02      |
| 2023-06-GSAFAC-0000002637	    | 2024-01-22      |
| 2021-05-GSAFAC-0000000970	    | 2024-02-22      |
| 2023-09-GSAFAC-0000005934	    | 2024-02-20      |
| 2023-06-GSAFAC-0000006347	    | 2024-03-12      |
| 2023-06-GSAFAC-0000031380	    | 2024-03-28      |
| 2023-06-GSAFAC-0000018003	    | 2024-01-11      |
| 2023-12-GSAFAC-0000035082	    | 2024-04-10      |
| 2023-06-GSAFAC-0000032873	    | 2024-03-28      |
| 2023-06-GSAFAC-0000025518	    | 2024-02-21      |
| 2022-06-GSAFAC-0000054181	    | 2024-09-04      |


## Consequences

1. Some records have incorrect values. We will have to come back and update them as a curation action.
2. The few new validations will affect some users.
3. **We will have better data going forward.**
