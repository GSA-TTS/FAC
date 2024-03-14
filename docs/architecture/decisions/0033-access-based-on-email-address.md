# 33. Make email address primary for `Access`

Date: 2023-11-20

## Status

Accepted

## Areas of impact

- [ ]   Compliance
- [ ]   Content
- [x]   CX
- [ ]   Design
- [x]   Engineering
- [x]   Policy
- [ ]   Product
- [ ]   Process
- [ ]   UX

## Related documents/links

*   [If a user deletes and recreates their login.gov account, we retain a copy of both accounts](https://github.com/GSA-TTS/FAC/issues/2782)

## Context

Our current user login/creation path:

1.  Get info from login.
2.  Look to see if the login.gov identifier is in our system.
3.  If yes, log that user in and skip remaining steps.
4.  If no, create new user with this login.gov identifier and primary email address.
5.  Go through all email addresses in user’s login.gov info and associate any _unclaimed_ `Access` entries with any of those email addresses with this user.

This turns out to not work if users delete their login.gov accounts and create new ones with the same email address (which is the login.gov recommended path for dealing with losing access to your account), which is creating problems for our users. The problem looks something like this:

1.  User creates login account A with email address a@a.com
2.  User logs in to FAC; we create user with loginid A, email a@a.com, and associate it with _submissions set X_ with loginid A.
3.  User deletes login account A, creates B with email a@a.com
4.  User logs in to FAC; we create user with loginid B, email a@a.com. This does not get associated with _submissions set X_.
5.  The user has lost access to account A, but can log in with the email address that should have access to _submissions set X_. Our system currently cannot reconcile this.

## Decision

Change the user login path to this instead (the first four steps are unchanged):

1.  Get info from login.
2.  Look to see if loginid is in our system.
3.  If yes, log that user in.
4.  If no, create new user with loginid and primary email address.
5.  Go through all email addresses in user’s login.gov info and associate _any_ (claimed or not) `Access` entries with any of those email addresses with this user.

The key change is that we no longer only associate unclaimed `Access` entries with the user upon login, but will update all `Access` entries with those email addresses to point at this user.

## Consequences

This will solve the above bug around users deleting their login.gov accounts and creating new ones with the same email address.

This has the effect of making the ownership of an email address according to login.gov absolutely primary: if login.gov thinks you own a@a.com and you log in to FAC, you will then have access to _all_ submissions that granted access to a@a.com, regardless of how long ago they were created or who might have owned a@a.com in the past.

We will need to document the above primacy of email addresses in our system for user awareness, since it’s not clear that the implications are immediately evident.

This will leave dangling `User` entries in the system that we probably need to clean up.

Since we don’t have relevant indexes on `Access`, this may eventually cause performance issues that we’ll have to look at in future.
