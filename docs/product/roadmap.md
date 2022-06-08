Product roadmap
===================

## Overview
This is a high-level overview. For more detail, see our [story map](https://www.google.com/url?q=https://app.mural.co/t/gsa6/m/gsa6/1647625636085/7825fa5ead63ebb1b65eefab5ea20d24a8ab7c59?wid%3D0-1647626493256%26sender%3Dua4d37dfba3f1e69e09078790&sa=D&source=docs&ust=1654713307298233&usg=AOvVaw2VRKptBGcaZgHol3V6vXpw) or [user flows chart](https://app.mural.co/t/gsa6/m/gsa6/1654109929324/5da173ea5f7ba75104e4e624451e58496a7164c8?sender=ua4d37dfba3f1e69e09078790). As with all agile product roadmaps, this is subject to change. The team revisits and adjusts the roadmap regularly. 

## Product Vision
* Fully transition the FAC PMO from Census to TTS
* Transition the [current Census FAC product](https://facweb.census.gov/) into something TTS can maintain
* Reduce risk and prove value by delivering incremental product updates 

## Release: MVP
**Goals:** Launch a new FAC intake experience for at least some of current FAC customers on or around 10/1 to begin accepting audits for FY2022. Per the discussed and approved [migration plan](https://github.com/GSA-TTS/FAC/blob/main/docs/product/decisions/0004-P-migration-plan.md), the idea is to keep the old Census FAC running and import FY2022 submissions into that for data disseminination. This will help limit scope and reduce risk of the MVP. 

**Success Metrics (proposed):** 
* We can accept single audits

**Key Features:**
* ✅ Technical foundation / infrastructure
* (80% ✅) Create a new audit (pre SAC forms)
* (10% ✅) SAC forms
* (in design) Submit an audit package (post SAC forms)
* Excel file ingest
* Login.gov integration
* Homepage with nav linking to old FAC static pages + 
* Minimal new content living on new site (Informational content for new system features)
* Email notifications (status change notifications, etc)
* “Frontend” user roles + UI 
    * These are the users who submit/certify audits
    * Let the person who creates an audit add other users with the same perms. 
    * Subset of folks allowed to certify.
* “Backend” user roles + UI 
    * These are admins and customer support roles
    * DJango admin for UI?
* Have a path to transfer data from new FAC to current FAC, preferably in real time
* ATO
* Release (domain name, public launch, user relations)
    * Unknowns here for cross agency coordination

## Possibly not MVP release

**Key Features:**
* Automated post-submission verification
    * Very basic, like year in excel match year submitted? UEI’s match?
* Non-xls input to audit packages
* Copying over FAQ’s and other pages
* Submitting revisions to an audit package

## Definitely not MVP release

**Goals:** Fully replace the Census FAC, which at this point can be taken off the internet. At this point the new TTS FAC will be the authoratative source for all historical FAC data. 

**Success Metrics (proposed):** 
* GSA FAC is the one stop for all single audit data - current + historical

**Key Features:**
* Data dissemination (exports, full API, etc)
* Search
* Handling disseminating public vs/ non-public data
* Performance optimization to accomodate 1.5TB of historical data
* Data import from old FAC
* Login for government users (via Max.gov)
* Not handling changes to form over time/in future (it’s likely that in some future year the questions on * the form will change, and we’re not trying to design for that for MVP)
