# 1. Record architecture decisions

Date: 2023-03-09

## Status

Accepted

## Context

SAM.gov is intended to be considered the single source of truth for UEIs (Universal Entity Identifiers), and the information associated with them (entity name, address, etc.). The SAM.gov rollout continues, and this implies two things. First, submitters may encounter challenges or delays in obtaining their UEI. Second, it may be that SAM.gov's API for validating UEIs and obtaining associated information may not be available. 

## Decision

We will use SAM.gov, but need to acknowledge the current state of the system (the SAM.gov software and the people who use it) surrounding it.


                      ┌───────────────┐
                      │               │    Found     Pre-populate fields,
       ──────────────►│ Check SAM.gov ├────────────► Mark UEI as validated.
User enters UEI       │               │
                      └──────┬────────┘
                             │
                             │           Do not pre-populate fields,
                             └────────►  Mark UEI as not validated.
                             Not found

UEIs will always be validated. This means we will determine that they have the correct shape.

When a submitter enters their UEI, we will attempt to validate it with the SAM.gov API. If we can, we will pre-populate the entity name with the information returned. We will also record that the UEI was validated at time of submission.

If we cannot validate the UEI, we will record the UEI and the fact that we could not validate it at the time of submission.

In the submission process, there is a later point where the UEI might be edited. If it is, we will (at that point) allow the edit to take place, but we will mark the UEI as non-validated.

## Consequences

There are data cleanliness consequences. To mitigate this, we are able to put into place later processes to check UEIs and/or data associated with them.

There are operational considerations. To mitigate this, we will revisit SAM.gov uptime and the state of UEI transition at a later point, and revisit the question of how to handle UEIs that cannot be validated at submission-time. However, this operational posture is in keeping with the AY22 submission, and does not represent a regression from the C-FAC to G-FAC.

There are paths to iterative improvement. As systems improve, we will be able to iteratively improve our system and its interaction with others. This pathway reduces user burden now, and leaves pathways for systemic improvement through future revisions.