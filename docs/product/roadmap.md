Product roadmap
===================

## Overview
This is a high-level overview of the FAC **product** roadmap. We recognize that there are other aspects of the program that are needed for a successful launch For more detail, see our [story map](https://www.google.com/url?q=https://app.mural.co/t/gsa6/m/gsa6/1647625636085/7825fa5ead63ebb1b65eefab5ea20d24a8ab7c59?wid%3D0-1647626493256%26sender%3Dua4d37dfba3f1e69e09078790&sa=D&source=docs&ust=1654713307298233&usg=AOvVaw2VRKptBGcaZgHol3V6vXpw) or [user flows chart](https://app.mural.co/t/gsa6/m/gsa6/1654109929324/5da173ea5f7ba75104e4e624451e58496a7164c8?sender=ua4d37dfba3f1e69e09078790). As with all agile product roadmaps, this is subject to change. The team revisits and adjusts the roadmap regularly. 

## Product Vision
* The new grants clearinghouse will be a trusted, transparent and quickly actionable source of grants information to speed reporting, audit resolution, and risk mitigation.
* Fully transition the FAC PMO from Census to TTS
* Transition the [current Census FAC product](https://facweb.census.gov/) into something TTS can maintain
* Modernize the product in a number of beneficial ways to the public and government users
* Reduce risk and prove value by delivering incremental product updates 

## Release: MVP
**Goals:** Launch a new FAC intake experience for at least some of current FAC customers on or around 10/1 to begin accepting audits for FY2022. Per the discussed and approved [migration plan](https://github.com/GSA-TTS/FAC/blob/main/docs/product/decisions/0004-P-migration-plan.md), the idea is to keep the old Census FAC running and import FY2022 submissions into that for data dissemination. This will help limit scope and reduce risk of the MVP. 

IMPORTANT NOTE: This system does not meet our full obligations as the Clearinghouse

**Success Metrics (proposed):** 
* We can accept single audits

**Assumptions** These milestones are sequenced and grouped thematically and are intended to be about equal size in effort, however they are not grounded in estimation. They are made under the assumption that the FAC is adequately staffed through the engagement. 

**Milestone 1:** Pre-SAC
* (80% ✅) Create a new audit (pre SAC forms)
* (10% ✅) SAC forms
* (design) Submit an audit package (post SAC forms)
* Login.gov integration
* Homepage with nav linking to old FAC static pages

**Milestone 2:** SAC
* (front + backend implementation) Submit an audit package (post SAC forms)
* Excel file ingest
* PDF Validation (text, searchable, unlocked)
* (design/exploration) user roles

**Milestone 3:** Status and user business logic
* “Frontend” user roles + UI 
* Status notifications / state machine
* Email notifications (user role invite, status change notifications, etc)
* Invalid resubmission flow, resubmission workaround for user-generated revisions

**Milestone 4:** Backend + Support
* “Backend” user roles + UI 
* Have a path to transfer data from new FAC to current FAC, preferably in real time
* Minimal new content living on new site (Informational content for new system features)
* Begin customer support and help documentation

**Milestone 5:** Release
* ATO
* Release (domain name, public launch, user relations)
    * Unknowns here for cross agency coordination

## Possibly not MVP release

**Key Features:**
* Automated post-submission verification
    * Very basic, like year in excel match year submitted? UEI’s match?
* Non-xls input to audit packages
* Copying over FAQ’s and other pages

## Full FAC functionality release

**Goals:** Fully replace the Census FAC, which at this point can be taken off the internet. At this point the new TTS FAC will be the authoritative source for all historical FAC data. 

**Success Metrics (proposed):** 
* GSA FAC is the one stop for all single audit data - current + historical

**Key Features:**
* Data dissemination (exports, full API, etc)
* Search
* Handling disseminating public vs/ non-public data
* Performance optimization to accommodate 1.5TB of historical data
* Data import from old FAC
* Login for government users (via Max.gov)
* Not handling changes to form over time/in future (it’s likely that in some future year the questions on * the form will change, and we’re not trying to design for that for MVP)
