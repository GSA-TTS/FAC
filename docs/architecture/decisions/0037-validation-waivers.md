# 37. Validation waivers

Date: 2024-06-12

## Status

Accepted

## Areas of impact

*   Content
*   CX
*   Design
*   Engineering
*   Policy
*   Product
*   UX

## Related resources

*   [Earlier discussion doc #1](https://docs.google.com/document/d/1YzlmnzOQJM-uKjin4k90m8E01avqzKuA9YynTRh_UnQ/edit)
*   [Earlier discussion doc #2](https://docs.google.com/document/d/16Oo-no6cOQvtgjzVVJp-KUJIrEwAX8j1XX7HJj3gZu4/edit)
*   [Original ADR issue](https://github.com/GSA-TTS/FAC/issues/3977)
*   [Validation Waiver tracking issue](https://github.com/GSA-TTS/FAC/issues/3978)

## Context

### Overview

The current FAC system has hard requirements for submissions. There are specific instances where these requirements need to be waived, but we currently lack support for that. This document outlines the approach we’ll use to add that support.

#### Waivers

We introduce the notion that submissions have a set of waivers, one waiver per requirement waived[^1]. The typical submission has zero waivers.

Waivers require staff intervention, probably initiated via the help desk and performed using the Django Admin interface.

[^1]: In unusual cases there may be multiple waiver entries per submission per requirement waived; our code should be able to handle this.

#### Transparency

Any waivers will be public and will be published along with the rest of the FAC data for a disseminated audit. This ADR does not deal with the concept of waiver justifications that should not be public.

#### Examples

##### Example 1

An auditee certifying official may not be available to certify, and there may be no prospect of anyone being able to certify a given submission at any point. In such cases, the Census FAC practice was to stand in as the certifying official for the purposes of completing the submission. GSA FAC would take a similar approach: the submission would be able to proceed, and the summary report would note that GSA FAC issued a waiver for that submission and that no certifying auditee associated with the submission certified it.

##### Example 2

Circumstances may make it impossible to reactivate the UEI for an auditee, preventing the start of a submission. GSA FAC in this case would waive the requirement for an active UEI (note that a _valid_ UEI would still be required) and again note in the summary report that a waiver was issued and that the UEI was not active at the point the submission started.

## Decision

We will add a process for handling waiver requests and add application features to support this.

### Process

1.  Via help desk or other channels, FAC staff learn about the possible need for a validation waiver.
2.  A FAC staff member is assigned to handle this particular case.
3.  The FAC staff member either denies the request (in which case this is the last step) or confirms that a validation waiver is appropriate.
4.  The FAC staff member and the requester agree on an individual on the list of coordinating officials (NSACs[^2] or KSAMLs[^3]) who should authorize the validation waiver.
5.  FAC staff member emails that individual at that email address, possibly with a proposal for the language of the justification.
6.  That individual corresponds with the FAC staff member (and anyone else required) to authorize the validation waiver and agree on the (brief!) text of the justification. _The NSAC or KSAML is the official “requester”_, not whoever initially contacted FAC.
7.  Once the FAC staff member is satisfied with the justification, they, or another member of FAC staff with the necessary Django admin permissions, create entry in the relevant table. This would create the entry/entries in the validation waivers table and would also, in the case of certification waivers, “submit” the relevant certification and create the relevant `SubmissionEvent` associated with the submission, using values specifically for this (probably `FAC VALIDATION WAIVER` for the name and a `fac-validation-waivers` GSA email address).
8.  The auditee completes the submission as per usual.

A similar process would exist for UEI validation waivers, which require slightly different data because no `report_id` exists at the time the request for a waiver is made.

[^2]: National Single Audit Coordinators.
[^3]: Key Single Audit Management Liaisons.

### Data structures

Our initial plan to put the waiver data into the JSON fields of the `SingleAuditChecklist` entries doesn’t quite work. We considered it as a path to faster implementation, but it appears it wouldn’t save that much time and would cause problems later.

Aside from the table we will create specifically for waiver data, we also need to enter something into the JSON fields for certification, as otherwise downstream code such as `backend/audit/cross_validation/sac_validation_shape.py` will break.

We will have two tables; the awkwardness of UEI validation (that is, that it occurs before a submission has actually been started) requires either this or some amount of weirdness in a single table.

#### SAC validation waiver table

| Field             | Contents                                               |
| ----------------- | ------------------------------------------------------ |
| `report_id`       | Primary identifier                                     |
| `timestamp`       | When the waiver was created                            |
| `approver_email`  | Email address of FAC staff member approving the waiver |
| `approver_name`   | Name of FAC staff member approving the waiver          |
| `requester_email` | Email address of NSAC/KSAML requesting the waiver      |
| `requester_name`  | Name of NSAC/KSAML requesting the waiver               |
| `justification`   | Brief plain-text justification for the waiver          |
| `waiver_type`     | Constrained set of values; see below                   |

The number of different waiver types is likely to expand over time, but we’ll start with the following:

| Waiver type                   | Reason                                                     |
| ----------------------------- | ---------------------------------------------------------- |
| `auditee_certifying_official` | No auditee certifying official is available                |
| `auditor_certifying_official` | No auditor certifying official is available                |
| `active_uei`                  | The auditee cannot activate their SAM.gov UEI registration |

Each waiver type will require code to be added to the relevant parts of the application in order to accept the waiver, and in order to have waiver information show up on the dissemination side.

Each submission could have multiple entries in this table for the same `waiver_type` value; it should not be assumed that only one result will be returned by a query for a specific `report_id` and a specific `waiver_type` value.

That last detail means that this table probably needs to exist on the dissemination side and be part of the dissemination process; we may not want to show names and email addresses but we definitely want to make clear that the waiver exists and why.

#### UEI validation waiver table

It should suffice for this table to exist only on the submission side, as its contents will be copied to the above submission-side table as soon as a relevant submission is created.

| Field             | Contents                                               |
| ----------------- | ------------------------------------------------------ |
| `uei`             | Primary identifier                                     |
| `timestamp`       | When the waiver was created                            |
| `expiration`      | When the waiver expires                                |
| `approver_email`  | Email address of FAC staff member approving the waiver |
| `approver_name`   | Name of FAC staff member approving the waiver          |
| `requester_email` | Email address of NSAC/KSAML requesting the waiver      |
| `requester_name`  | Name of NSAC/KSAML requesting the waiver               |
| `justification`   | Brief plain-text justification for the waiver          |

We will add a new code path for UEIs that fail validation during the start of the submission process, such that before rejecting the UEI we check this table. If the UEI is present and the waiver has not expired, we will consider the UEI valid and let the submission proceed.

We will add code for the creation of the `SingleAuditChecklist` so that if those same conditions apply, the data in the UEI waiver is added to the SAC validation waiver table with a `waiver_type` value of `active_uei`.

### Notable details

*   For certification waivers, the certification data will show that it was submitted by `FAC VALIDATION WAIVERS` and a `fac-validation-waivers` GSA email address. This seems appropriate in terms of what we should show in our records, and also makes implementation easier—submissions with these waivers will look to the application’s internal checks as if they were certified as normal
*   Some staff training will be required, particularly around the requirement to exchange emails at a specific address as a guard against social engineering. We may want to also insist that the email address in question is one of those associated with the submission in our system (this cannot apply to the UEI validation waiver).
*   Certification waivers do not unlock the submission. If the submission is unlocked after one is created, the process will need to be repeated (because unlocking clears the contents of the certification fields). If the process is repeated, the submission will have multiple entries in the waiver table with the same `waiver_type`, so our code will need to account for this.
*   The dissemination process will need to be updated in order to flag audits as having waivers, and to display some of the details about the waivers.

## Consequences

We will have to:

*   Go over the process with the folks who are likely to use it, and tweak it as necessary.
*   Create the validation waiver and UEI validation waiver tables on the submission side, and the validation waiver table on the dissemination side.
*   Create the Django admin interface pieces for handling the waivers.
*   Alter the UEI validation code to check for the existence of UEI waivers.
*   Determine how to display waiver information on the dissemination side.
*   Alter the dissemination code to handle bringing waiver information over from the submission side.
*   Consider whether we might want to use something like this process for some historical data migration efforts.
