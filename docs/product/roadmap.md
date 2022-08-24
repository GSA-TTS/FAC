Product Roadmap
===================

This is a high-level overview of the FAC **product** roadmap. We recognize that there are other aspects of the program that are needed for a successful launch For more detail, see our [story map](https://www.google.com/url?q=https://app.mural.co/t/gsa6/m/gsa6/1647625636085/7825fa5ead63ebb1b65eefab5ea20d24a8ab7c59?wid%3D0-1647626493256%26sender%3Dua4d37dfba3f1e69e09078790&sa=D&source=docs&ust=1654713307298233&usg=AOvVaw2VRKptBGcaZgHol3V6vXpw) or [user flows chart](https://app.mural.co/invitation/mural/gsa6/1656512227992?sender=melissabraxton2796&key=3178b1ba-b7c4-4453-b6bd-70b5360d43a2). As with all agile product roadmaps, this is subject to change. The team revisits and adjusts the roadmap regularly. 

Product Vision
===================

The Federal Audit Clearinghouse (FAC) is and must continue to be a trusted, transparent and quickly actionable source of grants information to speed reporting, audit resolution, and risk mitigation. The goal of the TTS FAC is to seamlessly transition auditee/auditor/agency users, make audit data more transparent, and deliver a system that is maintainable for TTS by October of 2023. 

* **Seamlessly transition auditee/auditor/agency users:**
  * Core aspects of auditee, auditor and agency workflows are carried over
  * Improvements to design and accessibility
  * Clear transition communication on what changes are happening and when
* **Make audit data more accessible and transparent:**
  * Single audit data is easily accessible to the public to increase transparency and accountability
  * Single audit data is easily accessible to government agencies so that they can make informed decisions and prevent fraud
  * Single audit data is flexible enough to connect to other data sets and systems
* **Deliver a system that is maintainable for TTS:**
  * Application is written in a modern and maintainable technology stack TTS can support
  * Remove manual processing step to remove administrative burden
  * Uncouple unmaintainable integrations (i.e. ATAS) by transitioning agency users the new API


Milestones
===================

These milestones are sequenced and grouped thematically and are intended to be about equal size in effort, however they are not grounded in estimation. They are made under the assumption that the FAC is adequately staffed through the engagement. 

## Milestone 1: Pre-SAC ✅

**Value delivered:**
Guide auditees in their first steps to submitting a new audit. Present a homepage to them with a clear CTA, explain why they need to log in to submit a new audit, guide them through the "Pre-SAC" forms where they: 
* Verify their entity meets single audit criteria
* Submit basic information about the audit, including their UEI
* Specify who needs access to an audit

Additional value here is preventing entities that don't meet the criteria from submitting erroneous audits and protects the FAC from publicizing data that should not be made public.

**Specific deliverables:**
* (DONE ✅) Technical foundation
* (DONE ✅) Login.gov integration
* (DONE ✅) Create a new audit (pre SAC forms)
* (DONE ✅) design/exploration - "Submit general information end to end / De-risk" milestone

## Milestone 2: Submit general information end to end / De-risk

**Value delivered:**
To de-risk our product plans, we will focus on an end-to-end solution that bridges data input to dissemination to the current FAC. This will include a fully fleshed out SF-SAC general information page. We will also build out the API to de-risk unknows in end-to-end implementation and unblock our partners at Census by providing specifics of API format. 

**Specific deliverables (full list [here](https://github.com/GSA-TTS/FAC/milestone/11)):**
* (20% ✅) [General information - SF-SAC data entry](https://github.com/GSA-TTS/FAC/issues/185)
* [API for accessing general SF-SAC Data](https://github.com/GSA-TTS/FAC/issues/355)
* [Audit permissions](https://github.com/GSA-TTS/FAC/issues/332) and [my audit submissions](https://github.com/GSA-TTS/FAC/issues/343) page
* [PDR/ADR - Excel file ingest](https://github.com/GSA-TTS/FAC/issues/328)
* [PDR/ADR - File Upload storage](https://github.com/GSA-TTS/FAC/issues/328)

## Milestone 3: Submit an entire SF-SAC

**Value delivered:**
Now that auditees have filled out basic information about their audit submission, they need to be able to submit the audit itself. While the current FAC allows users to submit form data and excel files, it's most valuable (and quite possibly sufficient for MVP release) to just allow them to upload templatized excel files for their audit. It's important to validate excel files and PDF uploads to reduce the chance of submitting an incomplete audit, which consumes time of both government staff and auditee staff. 

**Specific deliverables:**
* [Excel Generation/Uploading functionality](https://github.com/GSA-TTS/FAC/issues/443)
* [Federal Awards screen](https://github.com/GSA-TTS/FAC/issues/187) (Excel upload)
* [Notes to SEFA screen](https://github.com/GSA-TTS/FAC/issues/406) (placeholder)
* [Audit Information screen](https://github.com/GSA-TTS/FAC/issues/214) (form)
* [Award Findings screen](https://github.com/GSA-TTS/FAC/issues/215) (Excel upload)
* Findings Text screen (Excel upload)
* CAP Text screen (Excel upload)
* Additional EINs (Excel upload + form)
* Secondary Auditors (placeholder)
* Finalize / Check for errors


## Milestone: Upload and Certify audit package

**Value delivered:**
The last steps for the auditee/auditor flow is to upload and certify the audit package for submission. 

**Specific deliverables:**
* [Audit Start page](https://github.com/GSA-TTS/FAC/issues/212)
* ["Single audit reporting package upload" page](https://github.com/GSA-TTS/FAC/issues/360)
* [Single audit reporting package upload](https://github.com/GSA-TTS/FAC/issues/404)
* [Auditee/Auditor audit certification](https://github.com/GSA-TTS/FAC/issues/319)
* [PDR - Automated audit processing](https://github.com/GSA-TTS/FAC/issues/329)
  * Option 1: "Process" audits in the new FAC, send them to "dissemination pipeline" of Census FAC
  * Option 2: "Process" audits in the old FAC, send them to "processing pipeline" of Census FAC
* (50% ✅) (design/exploration) Status and user business logic
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
1. Submit general information end to end / De-risk
1. Submit an entire SF-SAC
1. Upload and Certify audit package
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
1. Submit general information end to end / De-risk
1. Submit an entire SF-SAC
1. Upload and Certify audit package
1. Status and user business logic
1. Backend + Support + ~~Data Transfer~~ (avoid the last one)
1. Agency data dissemination
1. Public data dissemination
1. Accommodate and transfer old-FAC data
1. Data integrity / flexibility (potentially optional)
1. Submission enhancements (potentially optional)
1. **Initial release**


Sequencing options
===================

## Option 1: End to end, gradual integration

**Overview:** With each new form page we build (there are over 10) or set of form pages, build out an API that Census is prepared to integrate with. 

**Benefits:** Surface risks and Census dependencies sooner, rather than at the end.

**Drawbacks:** Possibility of being overly concerned about shaping data to Census' needs rather than our own long-term needs. Possibility of churn with Census if we have to change parts of our own model we already integrated with them. 

## Option 2: Finish the app, then integrate end to end

**Overview:** Complete the main part of the app (all forms) and have a complete picture of the data model before building out an API specifically for Census. 

**Benefits:** Ensure our own data model makes sense first before census dependencies. 

**Drawbacks:** Possibility of having to go back and re-evaluate forms or our data model if there are major disconnects with what Census needs. 


(L)ATO Strategy
===================

It is crucial for us to find ways to shorten the ATO process and reduce risk of delays in order to meet our timeline commitments. The following strategy will help us do this. 

* **Lightweight ATO (LATO)** - We believe we qualify for a "lightweight" ATO for our intial release, which will take less time. 
* **Common Stack** - We believe the use of a widely known gov stack (Django, Cloud.gov, Login.gov, S3) will make our ATO process smoother
* **Public Data** - We believe the public nature of federal audit data with limited PII will not present significant data privacy issues in ATO. We don't believe we'll need SORN. 
* **Documentation Resources** - We have a security engineer coming onboard to help document security features in a SSP Template
* **Batched subsequent releases** - We must be thoughtful about the ATO implications of subsequent releases. We understand we can do minor improvements and bug fix releases without updating our ATO, but launching major new features will require us to update it. For that reason, we'll likely batch major new features into major releases. We also may incorporate incorporate a "walking skeleton" approach in an initial release to cover subsequent releases. 
