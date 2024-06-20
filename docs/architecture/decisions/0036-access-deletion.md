# 36. Access deletion: allow deletion of Audit Editor role

Date: 2024-05-28

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

*   [Original ADR issue](https://github.com/GSA-TTS/FAC/issues/3881)

## Context

### Overview

There are occasional requests from users to remove other users from submissions—that is, to delete the `Access` instances that allow those other users to view and edit in-progress submissions.

This document only deals with in-progress submissions; submissions that have been disseminated are a separate category. The management of disseminated submissions on the intake side may need to be revisited when we deal with resubmission.

### Current support

Note that while users have names recorded in the system, only user email addresses matter for purposes of authentication/access. Therefore all references to adding/removing/changing a user refer to adding/removing/changing an email address associated with a role.

Any reference to user management is only with respect to a specific submission; users cannot change the access of any users with respect to the application as a whole.

There are three roles:

*   **Audit Editor**
*   **Auditee Certifying Official**
*   **Auditor Certifying Official**

Users with these roles can all view the entire submission and make edits. Only users with the **Auditee Certifying Official** and **Auditor Certifying Official** roles can complete the certification step matching their role.

Submissions may have multiple users with the **Audit Editor** role, but only one each with the **Auditee Certifying Official** and **Auditor Certifying Official** roles.

In addition, submissions must have users for each of the **Auditee Certifying Official** and **Auditor Certifying Official** roles, and these cannot be the same user.

Only users with the **Audit Editor** role can modify access to the submission, and only these operations are possible:

*   Add a user with the **Audit Editor** role
*   Add the user for the **Auditee Certifying Official** role, if no such user exists
*   Add the user for the **Auditor Certifying Official** role, if no such user exists
*   Change the user for the **Auditee Certifying Official** role
*   Change the user for the **Auditor Certifying Official** role

In particular, the following three operations are not supported:

*   Changing or removing a user with the **Audit Editor** role
*   Removing a user with the **Auditee Certifying Official** role without supplying a new user to replace them
*   Removing a user with the **Auditor Certifying Official** role without supplying a new user to replace them

Note that the user who originally created the submission is automatically granted the **Audit Editor** role. So far, experience suggests that users who create submissions are users who tend to have responsibilities around managing those submissions; this is part of the rationale for restricting access management functions to users with that role.

### Removing Audit Editor access

This is the easiest feature to add. It would probably be wise to prevent users from removing their own access to submissions, as this is unlikely to be intentional. Allowing it would almost definitely increase support request volume.

### Removing Certifying Official access

Providing this functionality will lead to problems as users attempt to go through the certification steps for their submissions only to discover that no-one on their team is able to access one or both of those steps because those roles have been removed.

For this reason, we will not add this functionality as part of this feature but will evaluate how many requests for this we receive.

### User stories

> Story 1: As an **Audit Editor** acting for an entity which has an in-progress submission in the midst of which the relationship with the auditing firm was severed, I want to remove access for all of the staff from that firm, so that they cannot access or alter the submission.

We should support this use case by allowing users with the **Audit Editor** role to remove other users, including the Certifying Official users.

-----

> Story 2: As an **Auditor Certifying Official** using my personal email address who has just resigned my position, I want to remove myself from the role, so that I no longer have access to materials outside of my purview.

For the moment, we will not support this use case, but will evaluate how much of a demand there is for removing Certifying Officials without requirement replacement users for their roles.

## Decision

We will add a feature granting users with the **Audit Editor** role the ability to remove that role from others.

We will not allow users with the **Audit Editor** role to remove themselves from that role. (In practice, this will mean that they must add another user with that role, and that user must then remove them.)

We will not add the ability to remove Certifying Official roles without supplying new users for those roles; we will evaluate how many requests we get that are for exactly this operation.

We will not add any out-of-band processes for adding or removing users from submissions.

## Consequences

We will have to do the following:

*   Add a **Remove** link to the current access management table
*   Add a **Remove** page for deleting an **Auditor Access** role
*   Create a method for `audit.views.manage_submission_access.ChangeOrAddRoleView` to support deletion
*   Ensure that the new method does not allow deletion when the email in the `Access` object being deleted matches the email of the current user
*   Add documentation for this feature
*   Track how many requests we get for removing Certifying Official roles without supplying a replacement
*   Potentially add documentation suggesting that larger organizations always add at least two of their staff in the **Audit Editor** role, to ensure that they do not get stuck without access to an audit if one of their staff members leaves
