Product Roadmap
===================

This is a high-level overview of the FAC **product** roadmap. We recognize that there are other aspects of the program that are needed for a successful launch For more detail, see our [story map](https://www.google.com/url?q=https://app.mural.co/t/gsa6/m/gsa6/1647625636085/7825fa5ead63ebb1b65eefab5ea20d24a8ab7c59?wid%3D0-1647626493256%26sender%3Dua4d37dfba3f1e69e09078790&sa=D&source=docs&ust=1654713307298233&usg=AOvVaw2VRKptBGcaZgHol3V6vXpw) or [user flows chart](https://app.mural.co/t/gsa6/m/gsa6/1656512227992/b2c078eb31eaaec991450b6b1ea91d2fe8235786?sender=u6b95794d0794b5e3888e1962). As with all agile product roadmaps, this is subject to change. The team revisits and adjusts the roadmap regularly. 

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

[Milestones are listed in GitHub here.](https://github.com/GSA-TTS/FAC/milestones?direction=asc&sort=title&state=open) The milestones are sequenced and grouped thematically and are intended to be about equal size in effort, however they are not grounded in estimation. They are made under the assumption that the FAC is adequately staffed through the engagement. 

Delivery options
===================
**NOTE** We identified two options for delivery. We've decided to adopt Option 1, but below you will also find an overview of both options.

## Option 1: Two major releases: MVP and full functionality

**Overview:** Launch a new FAC intake experience sooner for at least some of current customers on or around 4/1/2023 to begin accepting audits. Per the discussed and approved [migration plan](https://github.com/GSA-TTS/FAC/blob/main/docs/product/decisions/0004-P-migration-plan.md), the idea is to keep the old Census FAC running and import new submissions into that for data dissemination. 

**Benefits:** Soonest path to an initial public release, which will help us learn more quickly and break up overall product risk into multiple releases

**Drawbacks:** Two FAC websites at once is not ideal UX for public or agencies. We change the world on both agencies and the public twice instead of once. 

**Milestone sequence:** 
[Milestones are listed in GitHub.](https://github.com/GSA-TTS/FAC/milestones?direction=asc&sort=title&state=open) 

## Option 2: One major release

**Overview:** Replace census FAC in a single release when it's ready to fully replace the Census FAC

**Benefits:** Minimize number of transitions we put users through. 

**Drawbacks:** More time before we deliver value to the public. We don't learn as quickly from the public. More risk in a single release. 

**Milestone sequence:**
1. Pre-SAC
1. Submit general information end to end / De-risk
1. Federal awards, Excel upload patterns
1. Submit an entire SF-SAC
1. Upload and finalize audit package
1. Audit certification and processing
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
