# 31. User access management

Date: 2023-11-14

## Status

Accepted

## Areas of impact

- [ ]   Compliance
- [ ]   Content
- [ ]   CX
- [x]   Design
- [x]   Engineering
- [ ]   Policy
- [ ]   Product
- [ ]   Process
- [x]   UX

## Related documents/links

*   [Epic: Modify user roles after audit creation](https://github.com/GSA-TTS/FAC/issues/2654).
*   Many ZenDesk tickets from users who want to change the auditee and/or auditor certifying officials for a submission.
*   [Deleting `Access` objects](https://github.com/GSA-TTS/FAC/issues/2739)
*   An [issue from ancient times about access management](https://github.com/GSA-TTS/FAC/issues/333).

## Context

Access to submissions is controlled using Access entries that associate email addresses with roles.

Currently, access is determined in the third pre-SAC step, the final step before a submission is actually created in our system.

The user creating the submission specifies, in that step, any number of auditee/auditor contacts; each of these, and the submitter, are given editor roles on the submission. In the same step, the user also specifies a single auditee certifying official and a single auditor certifying official; their email addresses are associated with the roles that allow them to perform specific certification steps that other users cannot do.

There is no user-facing way to delete, add, or change access to a submission once it’s started.

Many users are entering incorrect email addresses for the certifying roles and only discovering this once the submission is ready for certification.

The only option for those submissions, aside from altering the database, is to abandon the in-progress submission and start a new one with the correct email addresses.

This causing significant difficulty for our users and in turn is generating a significant number of help desk tickets

## Decision

Due to the need to address this problem sooner rather than later, we need to implement a bare-minimum version of user-facing access controls. An ideal version of this access control feature is planned for the future, but this document concerns what the bare minimum is.

Rather than a unified access control page, we will implement three different pages, one each for the following:

*   Changing the auditor certifying official role.
*   Changing the auditee certifying official role.
*   Adding more users to a submission with the generic “editor” role.

We will probably add them in that order.

Some notable features we will not include in this version:

*   Pure deletion. It will not be possible to remove certifying officials without specifying new officials in their place.
*   Removing other users. It will not be possible to remove users with the “editor” role.
*   Mass addition/alteration. Each user added will have to be done through the interface one at a time.

Each of the auditor and auditee certifying official role interfaces will contain:

*   A warning notification that saving the page will remove the current user from the submission and replace them with the user entered.
*   (Possibly a warning that if the user is removing themselves, they will lose access as soon as they submit this form.) (Once we have editor addition in, we can also advise them to add themselves as an editor before doing this.)
*   A reminder that this page is for whichever of auditor/auditee it is, and that it’s not for the other roles, with links to those pages.
*   Non-editable text indicating the name and email address that will be removed.
*   Form fields for the name and email address of the new user.
*   The same validation we have for individual fields on the pre-SAC page.
*   A save button.

The page for adding editors will have:

*   A list of the names and addresses of the users who currently have edit access.
*   Form fields for the name and email address of the new user.
*   The same validation we have for individual fields on the pre-SAC page.
*   A save button.

We will add links to these pages into the UI so that users can reach them.

We will add support for [deleting `Access` objects](https://github.com/GSA-TTS/FAC/issues/2739) in order to support this feature; that change does not require a user-facing interface.

## Consequences

Users will be able to get past the blocker of having incorrect information in the certifying official roles for submissions.

We will have a user management feature that has only some critical functions and lacks others; this may generate more help desk tickets.

We will support the [deletion of `Access` objects](https://github.com/GSA-TTS/FAC/issues/2739) and track some of the details.

We will have to support redirection from the URLs from the pages that we create now to the future better version of user management.
