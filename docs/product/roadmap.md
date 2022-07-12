Product Roadmap
===================

This is a high-level overview of the FAC **product** roadmap. We recognize that there are other aspects of the program that are needed for a successful launch For more detail, see our [story map](https://www.google.com/url?q=https://app.mural.co/t/gsa6/m/gsa6/1647625636085/7825fa5ead63ebb1b65eefab5ea20d24a8ab7c59?wid%3D0-1647626493256%26sender%3Dua4d37dfba3f1e69e09078790&sa=D&source=docs&ust=1654713307298233&usg=AOvVaw2VRKptBGcaZgHol3V6vXpw) or [user flows chart](https://app.mural.co/t/gsa6/m/gsa6/1654109929324/5da173ea5f7ba75104e4e624451e58496a7164c8?sender=ua4d37dfba3f1e69e09078790). As with all agile product roadmaps, this is subject to change. The team revisits and adjusts the roadmap regularly. 

Product Vision
===================

* The new grants clearinghouse will be a trusted, transparent and quickly actionable source of grants information to speed reporting, audit resolution, and risk mitigation.
* Fully transition the FAC PMO from Census to TTS
* Transition the [current Census FAC product](https://facweb.census.gov/) into something TTS can maintain
* Modernize the product in a number of beneficial ways to the public and government users
* Reduce risk and prove value by delivering incremental product updates 

Milestones
===================

These milestones are sequenced and grouped thematically and are intended to be about equal size in effort, however they are not grounded in estimation. They are made under the assumption that the FAC is adequately staffed through the engagement. 

## Milestone: Pre-SAC

**Value delivered:**
Guide auditees in their first steps to submitting a new audit. Present a homepage to them with a clear CTA, explain why they need to log in to submit a new audit, guide them through the "Pre-SAC" forms where they: 
* Verify their entity meets single audit criteria
* Submit basic information about the audit, including their UEI
* Specify who needs access to an audit

Additional value here is preventing entities that don't meet the criteria from submitting erroneous audits and protects the FAC from publicizing data that should not be made public.

**Specific deliverables:**
* (DONE ✅) Technical foundation
* (DONE ✅) Login.gov integration
* (90% ✅) Create a new audit (pre SAC forms)
* (60% ✅) design/exploration - "Submit an entire audit package" milestone

## Milestone: Submit general information end to end / De-risk

**Value delivered:**
To de-risk our product plans, we will focus on an end-to-end solution that bridges data input to dissemination to the current FAC. This will include a fully fleshed out SF-SAC general information page. We will also build out the API to de-risk unknows in end-to-end implementation and unblock our partners at Census by providing specifics of API format. 

Submit general information end to end:
* (20% ✅) [General information - SF-SAC data entry](https://github.com/GSA-TTS/FAC/issues/185)
* [API to transfer general information data to Census](https://github.com/GSA-TTS/FAC/issues/310)

De-risk and potentially de-scope audit package features: 
* [PDR - Certify audit submission](https://github.com/GSA-TTS/FAC/issues/319)
  * Option 1: Special roles/UX in the app to sign digitally (current, user-preferred solution)
  * Option 2: Copy solve to ask people to sign the PDF (lightweight solution)
    * Risk: Could lead to more audit churn if they are uploaded without signatures
    * Risk: Could lead to more scanned PDFs being uploaded rather than searchable ones, slowing down auditors
* [PDR - Excel file ingest](https://github.com/GSA-TTS/FAC/issues/328)
  * Option 1: Find a way to generate Excel file templates (current solution)
  * Option 2: Static Excel file templates
    * Risk: Potentially more confusing for the user to re-enter information
    * Risk: CPAs working on multiple audits might upload the wrong sheet
  * Option 3: Single Excel file templates
    * Risk: Limited / no client side validation, which could lead to more audit churn
    * Opportunity: More simple experience for users

## Milestone: Submit an entire audit package

**Value delivered:**
Now that auditees have filled out basic information about their audit submission, they need to be able to submit the audit itself. While the current FAC allows users to submit form data and excel files, it's most valuable (and quite possibly sufficient for MVP release) to just allow them to upload templatized excel files for their audit. It's important to validate excel files and PDF uploads to reduce the chance of submitting an incomplete audit, which consumes time of both government staff and auditee staff. This step also makes it possible for auditee and auditor certifying officials to certify that the audit can be made public.

**Specific deliverables:**
* Certify audit submission
* PDF Validation
* Excel file ingest
* Submit an audit package (post SAC forms)
* (design/exploration) Status and user business logic
* [PDR - Audit processing](https://github.com/GSA-TTS/FAC/issues/329)
  * Option 1: "Process" audits in the new FAC, send them to "dissemination pipeline" of Census FAC
  * Option 2: "Process" audits in the old FAC, send them to "processing pipeline" of Census FAC
* [PRD - PDF Validation](https://github.com/GSA-TTS/FAC/issues/307)
  * Option 1: Validate uploaded PDFs for being text, searchable and unlocked (current, user-preferred solution)
  * Option 2: No validation / incomplete validation
    * Risk: Could lead to more audit churn if they are uploaded in an unusable state


## Milestone: Status and user business logic

**Value delivered:**
Now that an auditee has submitted an audit, we need to communicate what's next for them. That includes a system to communicate audit status via confirmation and update emails as well as an audit status dashboard. If an audit has errors or is incomplete, auditees and auditors need clear instructions on how to resubmit. Status is important because it it triggers when an audit submission is ready to be certified / changes how specific users who have the authority to "certify" can act on the audit. Notifications are also critical because they trigger other people who need to certify/do things with the audit submission in order for it to be submitted/made public to actually go in and do those things.

**Specific deliverables:**
* Invite collaborator flow (send / accept invites)
* Possible - roles for certification
* Status notifications / state machine
* Email notifications (collaborator invite, status change notifications, etc)
* Invalid resubmission flow, resubmission workaround for user-generated revisions
* (80% ✅) Homepage with linking to the old Census FAC where appropriate to provide a path to the full FAC experience


## Milestone: Backend + Support

**Value delivered:**
Audit data needs to be disseminated to auditors and the general public. The easiest way to do this is to provide a pathway to transfer data to the original FAC to have the data dissemination take place there. In order to avoid building a complicated and temporary two-way sync, we need to provide auditors access to a simple backend to the new FAC to update audit status. 

**Specific deliverables:**
* “Backend” user roles + UI 
  * This is very undefined at the moment
* Minimal new content living on new site (Informational content for new system features)
* Begin customer support and help documentation
* Basic frontend analytics / DAP integration


## Milestone: Initial release

**Value delivered:**
The general public gets to use the new, more accessible FAC. The FAC product gets its first live feedback. 

**Specific deliverables:**
* ATO
* Copy updates, potentially including multi-lingual copy
* Update SAM.gov and Login.gov API credentials to production 
* Release (domain name, public launch, user relations)
    * Unknowns here for cross agency coordination


## Milestone: Agency data dissemination

**Value delivered:** In order for agencies to get information out of the FAC, they need a structured way to receive audits. The Census FAC has customized integrations for key agencies like HHS and ED, which we will no longer support. However, we will have an API that lets them build their own integration. 

**Specific deliverables:** 
* Documented API to get FAC data
* Specicial API permissions for government users versus general public
* Advise on change management efforts with key agencies as needed


## Milestone: Public data dissemination

**Value delivered:** In order for the general public to get information out of the FAC, they need to be able to be able to search/filter audits as well as export data via CSV

**Specific deliverables:**
* Search/filter audits
* Download lists of audits via CSV


## Milestone: Accommodate and transfer old-FAC data

**Value delivered:** Needed in order to fully replace the Census FAC. Auditors only have to use one system. Auditees and interested members of the public are not confused by having two websites. 

**Specific deliverables:**
* Performance optimization to accommodate 1.5TB of historical data
* Data import from old FAC
* Coordinate with Census FAC and interested parties for crossover
* Copying over FAQ’s and other pages


## Milestone: Data integrity / flexibility

**Value delivered:** For auditors, we can help flag potential issues with automated-post submission verification and also allow for form changes over time. For auditees, we can allow them to correct specific things in their revision without needing to submit an entirely new one. 

**Specific deliverables:**
* Automated post-submission verification (matching years, UEI's)
* Future-proofing data for form changes over time
* User-submitted revisions to an audit package


## Milestone: Submission enhancements

**Value delivered:** Make it easier for government users to log in via Max. Make it easier for less complicated auditee use cases by letting them input data into forms. Potentially other enhancements prioritized by user research. 

**Specific deliverables:**
* Login for government users (via Max.gov)
* Non-xls input to audit packages


Delivery options
===================

## Option 1: Two major releases: MVP and full functionality

**Overview:** Launch a new FAC intake experience sooner for at least some of current customers on or around 1/1/2023 to begin accepting audits. Per the discussed and approved [migration plan](https://github.com/GSA-TTS/FAC/blob/main/docs/product/decisions/0004-P-migration-plan.md), the idea is to keep the old Census FAC running and import new submissions into that for data dissemination. 

**Benefits:** Soonest path to an initial public release, which will help us learn more quickly and break up overall product risk into multiple releases

**Drawbacks:** Two FAC websites at once is not ideal UX for public or agencies. We change the world on both agencies and the public twice instead of once. 

**Milestone sequence:**
1. Pre-SAC
1. Submit an audit package
1. Status and user business logic
1. Backend + Support + Data Transfer
1. **Initial release** (MVP)
1. Agency data dissemination
1. Public data dissemination
1. Accommodate and transfer old-FAC data
1. Data integrity / flexibility (potentially optional)
1. Submission enhancements (potentially optional)
1. **Full FAC functionality release**


## Option 2: One major release

**Overview:** Replace census FAC in a single release when it's ready to fully replace the Census FAC

**Benefits:** Minimize number of transitions we put users through. 

**Drawbacks:** More time before we deliver value to the public. We don't learn as quickly from the public. More risk in a single release. 

**Milestone sequence:**
1. Pre-SAC
1. Submit an audit package
1. Status and user business logic
1. Backend + Support + ~~Data Transfer~~ (avoid the last one)
1. Agency data dissemination
1. Public data dissemination
1. Accommodate and transfer old-FAC data
1. Data integrity / flexibility (potentially optional)
1. Submission enhancements (potentially optional)
1. **Initial release**


(L)ATO Strategy
===================

It is crucial for us to find ways to shorten the ATO process and reduce risk of delays in order to meet our timeline commitments. The following strategy will help us do this. 

* **Lightweight ATO (LATO)** - We believe we qualify for a "lightweight" ATO for our intial release, which will take less time. 
* **Common Stack** - We believe the use of a widely known gov stack (Django, Cloud.gov, Login.gov, S3) will make our ATO process smoother
* **Public Data** - We believe the public nature of federal audit data with limited PII will not present significant data privacy issues in ATO. We don't believe we'll need SORN. 
* **Documentation Resources** - We have a security engineer coming onboard to help document security features in a SSP Template
* **Batched subsequent releases** - We must be thoughtful about the ATO implications of subsequent releases. We understand we can do minor improvements and bug fix releases without updating our ATO, but launching major new features will require us to update it. For that reason, we'll likely batch major new features into major releases. We also may incorporate incorporate a "walking skeleton" approach in an initial release to cover subsequent releases. 