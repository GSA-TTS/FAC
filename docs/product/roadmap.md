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

### Milestone 1: Pre-SAC

**Value delivered:**
Guide auditees in their first steps to submitting a new audit. Present a homepage to them with a clear CTA, explain why they need to log in to submit a new audit, guide them through the "Pre-SAC" forms where they: 
* Verify their entity meets single audit criterea
* Submit basic information about the audit, including their UEI
* Specify who needs access to an audit

**Specific deliverables:**
* (80% ✅) Homepage with nav linking to old FAC static pages
* (80% ✅) Create a new audit (pre SAC forms)
* (20% ✅) Login.gov integration
* (design/exploration) SAC forms (Submit an audit package)

### Milestone 2: SAC forms (Submit an audit package)

**Value delivered:**
Now that auditees have filled out basic information about their audit submission, they need to be able to submit the audit itself. While the current FAC allows users to submit form data and excel files, it's most valuable (and quite possibly sufficient for MVP release) to just allow them to upload templatized excel files for their audit. It's important for to validate excel files and PDF uploads to reduce the chance of audit rejection, which consumes time of both government staff and auditee staff. 

**Specific deliverables:**
* (10% ✅) SAC forms
* Submit an audit package (post SAC forms)
* Excel file ingest
* PDF Validation (text, searchable, unlocked)
* (design/exploration) Status and user business logic

### Milestone 3: Status and user business logic

**Value delivered:**
Now that an auditee has submitted an audit, we need to communicate what's next for them. That includes a system to communicate audit status via confirmation and update emails as well as an audit status dashboard. If an audit is rejected, the auditee must be given clear instructions for how to re-submit. 

**Specific deliverables:**
* “Frontend” user roles + UI 
* Status notifications / state machine
* Email notifications (user role invite, status change notifications, etc)
* Invalid resubmission flow, resubmission workaround for user-generated revisions

### Milestone 4: Backend + Support

**Value delivered:**
Audit data needs to be disseminated to auditors and the general public. The easiest way to do this is to provide a pathway to transfer data to the original FAC to have the data dissemination take place there. In order to avoid building a complicated and temporary two-way sync, we need to provide auditors access to a simple backend to the new FAC to update audit status. 

**Specific deliverables:**
* “Backend” user roles + UI 
* Have a path to transfer data from new FAC to current FAC, preferably in real time
* Minimal new content living on new site (Informational content for new system features)
* Begin customer support and help documentation

### Milestone 5: Release

**Value delivered:**
The general public gets to use the new, more acessible FAC. The FAC product gets its first live feedback. 

**Specific deliverables:**
* ATO
* Copy updates, potentially including multi-lingual copy
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
* Submitting revisions to an audit package
