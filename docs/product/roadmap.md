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
* (80% ✅) Homepage with linking to the old Census FAC where appropriate to provide a path to the full FAC experience
* (80% ✅) Create a new audit (pre SAC forms)
* (20% ✅) Login.gov integration
* (design/exploration) SAC forms (Submit an audit package)


## Milestone: Submit an audit package

**Value delivered:**
Now that auditees have filled out basic information about their audit submission, they need to be able to submit the audit itself. While the current FAC allows users to submit form data and excel files, it's most valuable (and quite possibly sufficient for MVP release) to just allow them to upload templatized excel files for their audit. It's important to validate excel files and PDF uploads to reduce the chance of submitting an incomplete audit, which consumes time of both government staff and auditee staff. This step also makes it possible for auditee and auditor certifying officials to certify that the audit can be made public.

**Specific deliverables:**
* (10% ✅) SF-SAC forms (OMB form)
* Submit an audit package (post SAC forms)
* Excel file ingest
* PDF Validation (text, searchable, unlocked)
* (design/exploration) Status and user business logic


## Milestone: Status and user business logic

**Value delivered:**
Now that an auditee has submitted an audit, we need to communicate what's next for them. That includes a system to communicate audit status via confirmation and update emails as well as an audit status dashboard. If an audit has errors or is incomplete, auditees and auditors need clear instructions on how to resubmit. Status is important because it it triggers when an audit submission is ready to be certified / changes how specific users who have the authority to "certify" can act on the audit. Notifications are also critical because they trigger other people who need to certify/do things with the audit submission in order for it to be submitted/made public to actually go in and do those things.

**Specific deliverables:**
* “Frontend” user roles + UI 
* Status notifications / state machine
* Email notifications (user role invite, status change notifications, etc)
* Invalid resubmission flow, resubmission workaround for user-generated revisions


## Milestone: Backend + Support + Data Transfer

**Value delivered:**
Audit data needs to be disseminated to auditors and the general public. The easiest way to do this is to provide a pathway to transfer data to the original FAC to have the data dissemination take place there. In order to avoid building a complicated and temporary two-way sync, we need to provide auditors access to a simple backend to the new FAC to update audit status. 

**Specific deliverables:**
* “Backend” user roles + UI 
* Have a path to transfer data from new FAC to current FAC, preferably in real time
* Minimal new content living on new site (Informational content for new system features)
* Begin customer support and help documentation


## Milestone: Initial release

**Value delivered:**
The general public gets to use the new, more accessible FAC. The FAC product gets its first live feedback. 

**Specific deliverables:**
* ATO
* Copy updates, potentially including multi-lingual copy
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

**Overview:** Launch a new FAC intake experience sooner for at least some of current customers on or around 10/1 to begin accepting audits for FY2022. Per the discussed and approved [migration plan](https://github.com/GSA-TTS/FAC/blob/main/docs/product/decisions/0004-P-migration-plan.md), the idea is to keep the old Census FAC running and import FY2022 submissions into that for data dissemination. 

**Benefits:** Soonest path to an initial public release, which will help us learn more quickly and break up overall product risk into multiple releases

**Drawbacks:** Two FAC websites at once is not ideal UX for public or agencies. We change the world on both agencies and the public twice instead of once. 

**Milestone sequence**
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

**Goals:** Replace census FAC in a single release to minimize number of transitions. 

**Drawbacks:** More time before we deliver value to the public. We don't learn as quickly from the public. More risk in a single release. 

**Milestone sequence**
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


## Option 3: Integrate more closely with the current FAC

**Goals:** Avoid the risks of big rewrite and deploy more modest updates incrementally. Solve issue of Census not being willing to maintain old system past a certain date. 

NOTE: This is currently just an idea from Peter to spark discussion, not a vetted proposal

**Drawbacks:** Need to onboard specialized staff to maintain old system, likely to take longer, risks of code bloat with various integration layers. 

**Milestone sequence**
1. [NEW] hire and onboard legacy stack resources
1. Submit an audit package
1. Status and user business logic
1. [NEW] integrate and somehow release on current FAC system
1. Backend + Support + ~~Data Transfer~~ (avoid the last one)
1. [NEW] integrate and somehow release on current FAC system
1. Agency data dissemination
1. [NEW] integrate and somehow release on current FAC system
1. Public data dissemination
1. [NEW] integrate and somehow release on current FAC system
1. Accommodate and transfer old-FAC data
1. [NEW] integrate and somehow release on current FAC system
1. Data integrity / flexibility (potentially optional)
1. [NEW] integrate and somehow release on current FAC system
1. Submission enhancements (potentially optional)
1. [NEW] integrate and somehow release on current FAC system