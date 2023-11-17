# 32. Track deletion using other models

Date: 2023-11-17

## Status

Accepted

## Areas of impact

- [ ]   Compliance
- [ ]   Content
- [ ]   CX
- [ ]   Design
- [x]   Engineering
- [ ]   Policy
- [ ]   Product
- [ ]   Process
- [ ]   UX

## Related resources

*   [Epic: Modify user roles after audit creation](https://github.com/GSA-TTS/FAC/issues/2654).
*   Many ZenDesk tickets from users who want to change the auditee and/or auditor certifying officials for a submission.
*   [The code for the `Access` class](https://github.com/GSA-TTS/FAC/blob/main/backend/audit/models.py#L623).
*   [Expanded user role management ADR](https://github.com/GSA-TTS/FAC/blob/main/docs/architecture/decisions/0031-user-access-management.md).

## Context

As outlined in the [expanded user role management ADR](https://github.com/GSA-TTS/FAC/blob/main/docs/architecture/decisions/0031-user-access-management.md), we need to delete `Access` entries. It’s also quite likely that we might need to delete a variety of other objects, in particular `User` entries, in the future.

Here “deletion” means “remove from the code paths that deal with active elements of our application” and not “scour from the earth and from history”.

For record-keeping purposes, we should not destroy the information that was in these entries, but store it for potential future investigation.

In the case of `Access` entries, if we were to delete the entires without doing anything else, we could run into this scenario:

1.  User A adds User C as a auditee certifying official
2.  User C makes some of the changes to the submission.
3.  User A realizes that the auditee certifying official should actually be User Z.
4.  User C’s `Access` entry is deleted and a new one is created for User Z.
5.  Some time later, there are questions about who did the edits in step 2.

Since the `Access` object active at the time is now gone, figuring out that link would require more work than seems ideal.

## Decision

*   Create a new `DeletedAccess` class that would be created whenever the application deletes an `Access` object.
*   This would have all of the fields in `Access`[^1] plus:
    *   `removed_at` (UTC timestamp)
    *   `removed_by_user` (reference to a user object)
    *   `removed_by_email_address` (email address of removing user) (these last two are not actually redundant).
    *   `removal_event` (this would mostly be something like `access-change`, but could theoretically in future include things like `account-inactivity`, `security-incident`, `data-correction`, etc.)

This approach has the advantage of not touching any of the existing `Access` code or related code paths, lowering the likelihood of breaking existing features; the same would apply to `User`, etc.

This would also be the path to follow for future entries of other kinds that we might might need to remove—if we need to remove `User` entries, we would put them in a `DeletedUser` table with the same four additional fields.

[^1]: `sac`, `role`, `fullname`, `email`, and `user`.
