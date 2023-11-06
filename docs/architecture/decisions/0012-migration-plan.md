# 12. FAC Migration Plan

Introduced: 20220513

Updated: 20220711

## Status

Approved

## Context

Provide clarity for the migration plan from the old Census FAC to the new TTS FAC. 

## Decision

#### On or around 4/1/23, the following will happen:

* We have a LATO
* The new TTS FAC is live and will begin accepting submissions for audit year 2023.
* The old Census FAC will continue to operate and disseminate data, but will no longer accept audit submissions.
* The old Census FAC will pull in new SAC entries from new TTS FAC into the dissemination pipeline via the API, keeping existing systems attached to the old FAC (ATAS, etc) smoothly operating for a temporary period of time. 
* Agencies will be told that they have six months to transition to the new TTS FAC's API, which is documented with guidance on how to transition from the old data model to the new model.

#### By 10/1/23, the following will have happened:

* We have a "moderate" ATO
* All relevant data from every SAC entry in the old Census FAC will be migrated over to the new TTS FAC
* The new TTS FAC will have undergone performance optimization to accomodate for the estimated 1.5TB in legacy data
* The old Census FAC will be taken off the internet
* The new TTS FAC will be the authoratative source for all historical FAC data

#### Important considerations to reach these goals:

* RISK: We need to retain resources, either on Census side or GSA side, to facilitate transition in April. We are exploring various ways we can keep them on to mitigate this risk.
* Document how every field from the old system will or will not be migrated to and from the old system using the [FAC Field Rosetta Stone](https://docs.google.com/spreadsheets/d/1e-NQPeXk9pcQhA9PEbywkfoJa1bcTunKsVsBjqFYVK4/edit#gid=1955175057) document (internal, not public). 

## Note
Was previously PDR 0004; renamed/renumbered when PDRs and ADRs were merged.
