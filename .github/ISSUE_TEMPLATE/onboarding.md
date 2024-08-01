---
name: Onboarding
about: An onboarding checklist for folks joining the team!
title: Onboarding checklist for {GitHub Username}
labels: ''
assignees: ''

---

**Instructions for the issue creator:**
1. Fill in the GitHub username of the new person (if known) and the name of the onboarding buddy.
1. Remove irrelevant checklists (eg designers should never see the engineer checklist.]
1. Remove the horizontal line below and everything above it (these instructions).

---

# Welcome to the team @{GitHub Username}!

{ONBOARDING BUDDY'S GH USERNAME} will be your onboarding buddy and can help you if you get stuck on any of the steps in the checklist below. There's also a separate checklist that your onboarding buddy will tackle!

## For you

Here's a checklist to get you started and to make sure you've got access to :all-the-things:!

- [ ] Review [the project README](https://docs.google.com/document/d/1g8nYqYS_ifFlZB-DBgfeSoJRMB__EqWsmLnacyk-bDI/) in Google Drive
- [ ] Join the Slack channels in [the project README](https://docs.google.com/document/d/1g8nYqYS_ifFlZB-DBgfeSoJRMB__EqWsmLnacyk-bDI/)
- [ ] Review our [process documentation](https://github.com/GSA-TTS/FAC#fac-documentation)
- [ ] Get access to our GitHub repositories
  - [ ] If you're not already a member of BOTH the [GSA](https://github.com/orgs/GSA/people) and [GSA-TTS](https://github.com/orgs/GSA-TTS/people) GitHub organizations, [follow the process outlined here](https://github.com/GSA/GitHub-Administration#joining-the-gsa-enterprise-organization), requesting access to the appropriate org(s). When it's time to send the mail, look up the Product Lead (see [the staffing list](https://docs.google.com/document/d/1g8nYqYS_ifFlZB-DBgfeSoJRMB__EqWsmLnacyk-bDI/edit#heading=h.us8xylqg455c)) then start with this template, mailing from your GSA email address:

    ```text
    To: gsa-github.support@gsa.gov
    Cc: [the product lead]
    Subject: GSA and GSA-TTS GitHub organization membership
    Body:
    [Edit the following text to put in your GitHub username and your GSA email address, then remove this instruction text.]
    Please add my GitHub account (https://github.com/myusername) to the following GitHub organizations:
    - https://github.com/GSA
    - https://github.com/GSA-TTS

    I will be working on the FAC project:
    - https://github.com/GSA-TTS/FAC

    I have cc'd the FAC Product Lead for awareness.

    Thank you!
    ```
    - (Note this step could take a few days; humans handle these requests.)
  - [ ] Once you are added to the GSA-TTS org, ask [the person(s) with the "Maintainer" role to add you to the `FAC-team` team](https://github.com/orgs/GSA-TTS/teams/fac-team/members). This will grant you read/write access to our repositories.
  - [ ] Have the team calendar owner (@jadudm) share the calendar invite link to our new team member.

**For designers, also...**
- [ ] Review the [design onboarding document](https://docs.google.com/document/d/1EILl0nZr59T4PFJJMtFbmnQDJPksgzIFPuoFDN0bk0g/edit#heading=h.bhu3dgydlbvr)
- [ ] Visit https://touchpoints.digital.gov/ and set up a touchpoints account
- [ ] If you don't already have a Figma license, request one from your supervisor.
- [ ] If you don't already have a Mural ccount, follow the instructions to get one [here](https://handbook.tts.gsa.gov/tools/mural/).

**For engineers, also...**
- [ ] Familiarize yourself with Python, Django, and Cloud.gov—all tools used in this project.
  - [ ] If you need to catch up on the latest in Python development, check out the [Python developer's guide](https://devguide.python.org/).
  - [ ] Work through the [Django Tutorial](https://docs.djangoproject.com/en/4.0/intro/tutorial01/) and writing your first Django app.
  - [ ] If it's not already set up on your machine & account, enable [commit signing](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits). Also see the pinned messages in the Slack development channel.
  - [ ] If you're not already, get [setup with Cloud.gov](https://cloud.gov/docs/getting-started/setup/)
    - [ ] Once your account exists, make a PR to [add yourself to the list of developers](https://github.com/GSA-TTS/FAC/tree/main/terraform/meta/config.tf) with access to our spaces.
  - [ ] Practice deploying a [python application](https://github.com/cloud-gov/cf-hello-worlds/tree/main/python-flask) to Cloud.gov using the Cloud.gov command line interface (CLI): https://cloud.gov/docs/getting-started/your-first-deploy/.
  - [ ] Survey existing TTS projects which use Django+Cloud.gov like: [Tock](https://github.com/18F/tock) and the [DOJ CRT Portal](https://github.com/usdoj-crt/crt-portal).
- [ ] Get set up for [local development](https://github.com/GSA-TTS/FAC/blob/main/docs/development.md#local-development) so you can start contributing
- [ ] Review [NIST SP 800-161 Rev.1](https://csrc.nist.gov/pubs/sp/800/161/r1/final) on supply chain risk management. Reply to this onboarding ticket in a comment when you have completed this review.


## For your onboarding buddy

Note: If you're not able to do any of these yourself, you're still responsible for making sure that the right person makes them happen!

- [ ] Add to the [FAC-team@GSA.gov](https://groups.google.com/a/gsa.gov/g/fac-team) Google Group
- [ ] Add to standing meeting invites (should happen automatically via addition to the Google Group membership)

**For designers, also...**
- [ ] Add as an editor on active Figma projects
- [ ] [Add as a form manager to the touchpoints recruitment intercept](https://touchpoints.app.cloud.gov/admin/forms/9412c559/permissions)

**For engineers, also...**
- [ ] [Add as a member of the FAC group in New Relic](https://one.newrelic.com/admin-portal/organizations/users-list) (@GSA-TTS/fac-admins can do this)

**For product leads/owners, also...**
- [ ] Make them Owner of [the various Google Groups in the project README](https://docs.google.com/document/d/1g8nYqYS_ifFlZB-DBgfeSoJRMB__EqWsmLnacyk-bDI/edit#heading=h.81zynabayrrg)
- [ ] Add them to [the FAC-admins team in GitHub](https://github.com/orgs/GSA-TTS/teams/fac-admins/members) and make them a Maintainer.
- [ ] Also give them the `Maintainer` role in [the FAC-team team in GitHub](https://github.com/orgs/GSA-TTS/teams/fac-team/members).
