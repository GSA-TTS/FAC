# 4. FAC Migration Plan

Introduced: 20220513

## Status

Approved

## Context

Provide clarity for the migration plan from the old Census FAC to the new TTS FAC. 

## Decision

#### On 10/1/22, the following will happen:

* The new TTS FAC is live and will begin accepting all audits for FY2022, which is the first day they can be submitted
* The new TTS FAC will have zero legacy data from the old Census FAC, which will make end user experiences like pre-filled forms from prior years impossible at launch. 
* The old Census FAC will continue to operate, but we _assume_ will not accept audits for FY2022
* The old Census FAC will pull in new SAC entries from new TTS FAC via the API, keeping existing systems attached to the old FAC (ATAS, etc) smoothly operating for a temporary period of time. 
* Agencies will be told that they have six months to transition to the new TTS FAC's API, which is documented with guidance on how to transition from the old data model to the new

#### On 4/1/23 (6 months later), the following will happen:

* All relevant data from every SAC entry in the old Census FAC will be migrated over to the new TTS FAC
* The new TTS FAC will have undergone performance optimization to accomodate for the estimated 1.5TB in legacy data
* The old Census FAC will be taken off the internet
* The new TTS FAC will be the authoratative source for all historical FAC data

#### Important considerations to reach these goals:

* Document how every field from the old system will or will not be migrated to and from the old system using the (FAC Field Rosetta Stone)[https://docs.google.com/spreadsheets/d/1e-NQPeXk9pcQhA9PEbywkfoJa1bcTunKsVsBjqFYVK4/edit#gid=1955175057] document (internal, not public). 