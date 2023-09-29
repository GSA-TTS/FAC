# 17. SAM.gov integration for MVP

Date: 2023-03-09

## Status

Accepted

## Context

SAM.gov is intended to be considered the single source of truth for UEIs (Universal Entity Identifiers), and the information associated with them (entity name, address, etc.). The SAM.gov rollout continues, and this implies two things. First, submitters may encounter challenges or delays in obtaining their UEI. Second, it may be that SAM.gov's API for validating UEIs and obtaining associated information may not be available. 

## Decision

We will use SAM.gov, but need to acknowledge the current state of the system (the SAM.gov software and the people who use it) surrounding it.


```
                      ┌───────────────┐
                      │               │    Found     Pre-populate fields,
       ──────────────►│ Check SAM.gov ├────────────► Mark UEI as validated.
User enters UEI       │               │
                      └──────┬────────┘
                             │
                             │           Do not pre-populate fields,
                             └────────►  Mark UEI as not validated.
                             Not found
```

When a submitter enters their UEI, we will check it with the SAM.gov API. If we can, we will pre-populate the entity name with the information returned. We will also record that the UEI was checked at time of submission.

If we cannot check the UEI, we will record the UEI entered and the fact that we could not check it at the time of submission.

We are able to guarantee, in either case, that the UEI is either 1) the correct shape (correct number of characters, meets other static checks appropriate to the UEI) OR 2) is an empty string. 

Once the UEI is submitted, users will not have an opportunity to change it later in the process. The submission process will indicate this to the user.

## Consequences

There are data cleanliness consequences. To mitigate this, we are able to put into place later processes to check UEIs and/or data associated with them.

There are operational considerations. To mitigate this, we will revisit SAM.gov uptime and the state of UEI transition at a later point, and revisit the question of how to handle UEIs that cannot be validated at submission-time. However, this operational posture is in keeping with the AY22 submission, and does not represent a regression from the C-FAC to G-FAC.

There are paths to iterative improvement. As systems improve, we will be able to iteratively improve our system and its interaction with others. This pathway reduces user burden now, and leaves pathways for systemic improvement through future revisions.
