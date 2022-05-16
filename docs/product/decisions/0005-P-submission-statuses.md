# 5. Proposed user-visible submission statuses

Introduced: 20220516.

## Status

Accepted.

## Context

Proposed statuses: `In Progress`, `Submitted`, `Received`, `Available`.

In this document phases are **strong** and statuses are `code`.

### Phases
These don't map exactly to statuses but might be useful as ways to consider the workflow for audit submissions. Phases are conceptual and do not necessarily need to be communicated to users—for example, it's not clear there's any meaning in distinguishing between a submission that's been created but hasn't had any post-creation data added to it and a submission that has had some post-creation data added to it. These proceed in order unless otherwise specified.

#### Not started
The organization that should submit an audit hasn't done anything with the FAC website for the audit for this period.

#### Preliminary
The create new submission process has started but data sufficient to starting the SAC process has not been submitted. During this phase data is stored in the `User` object on the backend.

#### **Created**
A user has started the SAC process but no further information has been entered. During this phase data is stored in the `SingleAuditChecklist` object on the backend.

#### **In progress**
A user has started the SAC process but neither auditor nor auditee has certified the submission. During this phase data is stored in the `SingleAuditChecklist` object on the backend.

#### **Revision in progress**
The same as **In progress** but rather than proceeding from **Preliminary**, the submission has already been through all phases through **Received** but has been rejected for some reason after that, and after passing through the **Rejected** phase is now being worked on again.

#### **Certifiable**
The SAC data is sufficiently filled out such that there are no mandatory missing fields and there are no fields with detectable errors, but no user has certified the submission. During this phase data is stored in the `SingleAuditChecklist` object on the backend.

#### **Partly certified**
A user has completed enough of the SAC process and either the auditor or auditee has certified the submission but the other hasn't. During this phase data is stored in the `SingleAuditChecklist` object on the backend.

#### **Certified**
Both the auditor and auditee have certified the data, but the SAC has not yet been formally submitted. It's not clear that we should maintain a distinction between this and **Submitted**, or that submission should be a separate user-initiated step from certification. During this phase data is stored in the `SingleAuditChecklist` object on the backend.

#### **Submitted**
Both the auditor and auditee have certified the data, and a user associated with the SAC has formally submitted it. It's not clear that we should maintain a distinction between this and **Certified**, or that submission should be a separate user-initiated step from certification. During this phase data is stored in the `SingleAuditChecklist` object on the backend.

#### **Received**
The SAC has been formally submitted and this submission (including any additional file uploads, particularly the official audit PDF itself) is stored in FAC systems. This phase currently involves manual verification of the submission by FAC personnel; we are hoping to eliminate the entire manual verification process. During this phase data is stored in the `SingleAuditChecklist` object on the backend.

#### **Accepted**
The SAC has been formally submitted and this submission (including any additional file uploads, particularly the official audit PDF itself) is stored in FAC systems. Verification (to the extent that there is any performed by the FAC) is complete. During this phase data is stored in the `SingleAuditChecklist` object on the backend.

#### **Rejected**
The SAC has been formally submitted and this submission (including any additional file uploads, particularly the official audit PDF itself) is stored in FAC systems. During verification (or later?) some issues are identified and the submission has to be revised. This could happen, in theory, after any phase after **Submitted**. During this phase data is stored in the `SingleAuditChecklist` object on the backend.

#### **Available**
The SAC has been formally submitted and this submission (including any additional file uploads, particularly the official audit PDF itself) is stored in FAC systems. Verification (to the extent that there is any performed by the FAC) is complete. The submitted audit and attendant data/files are available for browsing/downloading from the FAC site. During this phase data is stored in the `SingleAuditChecklist` object on the backend.

### Prior discussions

See [Determine possible statuses for FAC submission](https://github.com/GSA-TTS/FAC/issues/202).

## Decision

### Proposed statuses

These are the proposed values for a `status` field in the `SingleAuditChecklist` object on the FAC backend. The assumption is that these would be visible to users.

| Status        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Corresponding Phase(s)                                                                                                      | Prior status  | Next status   | Manual step to proceed?                       |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------- | ------------- | --------------------------------------------- |
| — (None)      | Submission not started                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | **Not started**, **Preliminary**                                                                                            | —             | `In progress` | Yes                                           |
| `In progress` | A user has started the SAC process but it hasn't been formally submitted                                                                                                                                                                                                                                                                                                                                                                                                                           | **Created**, **In progress**, **Partly certified**, **Certifiable**, **Certified**, **Rejected**, **Revision in progress**, | `None`        | `Submitted`   | Yes                                           |
| `Submitted`   | The SAC data is sufficiently filled out such that there are no mandatory missing fields and there are no fields with detectable errors, and a user with the auditor role has certified the submission, and a user with the auditee role has also done so, and a user with one of those roles has formally submitted it. This will almost always be a very short-lived status, since moving to the `Received` status should be near-instant.                                                        | **Submitted**                                                                                                               | `In progress` | `Received`    | No                                            |
| `Received`    | The SAC data is sufficiently filled out such that there are no mandatory missing fields and there are no fields with detectable errors, and a user with the auditor role has certified the submission, and a user with the auditee role has also done so, and a user with one of those roles has formally submitted it.                                                                                                                                                                            | **Received**, **Accepted**                                                                                                  | `Submitted`   | `Available`   | No, unless we agree to do manual verification |
| `Available`   | The SAC data is sufficiently filled out such that there are no mandatory missing fields and there are no fields with detectable errors, and a user with the auditor role has certified the submission, and a user with the auditee role has also done so, and a user with one of those roles has formally submitted it, and all of the data has made its way to the FAC backend, and any verification on the FAC side has taken place, and the files are available for download from the FAC site. | **Available**                                                                                                               | `Received`    | —             | —                                             |

None of these proposed statuses correspond to the **Rejected** or **Revision in progress** phases. User research may determine whether or not it's necessary to make one or both of those visible to users.

### Status change requirements

#### “Nothing” to `In progress`
A user must have completed the information we're currently storing in `User.profile`, with the exception that they may have a UEI that wasn't validated by SAM.gov.

#### `In progress` to `Submitted`

*   All mandatory fields must be completed.
    *   This includes UEI—in order to progress past this point the UEI in the submission must pass verification with SAM.gov.
*   All fields with validation rules must pass validation.
*   A PDF must have been uploaded as the audit report.
*   An authorized user with the auditor role for the submission must have certified it.
*   An authorized user with the auditee role for the submission must have certified it.
*   An authorized user with either the auditee role or the auditor role for the submission must have submitted it.

#### `Submitted` to `Received`
This should be automatic and quick, as a brief last verification that everything has been received by the backend should be sufficient.

#### `Received` to `Available`
The submission (including the uploaded PDF of the audit and the Single Audit Checklist data) must be available for download. Since it's currently not completely clear how the transition plan is handling that, it's possible that this will mean some transfer that will require a confirmation check of some kind, or possibly some kind of batch process.

#### `Available` to ?
We don't currently have a model for how revisions after this point are or should be handled, but it seems likely that cases will arise where an uncaught mistake makes it all the way through to the end of the workflow only for someone to find it later, and that corrections will then have to be made.
My current assumption is that in such cases the submission will be set to `In progress` and will have to again proceed through all of the later statuses.

## Status diagram

In the following rough diagram, phases are ellipses and statuses are boxes:

![image](https://user-images.githubusercontent.com/2626258/168630560-16446868-2d4d-425d-8fbc-13839d4e172d.png)
