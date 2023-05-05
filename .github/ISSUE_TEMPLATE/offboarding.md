---
name: Offboarding
about: An offboarding checklist for folks leaving the team
title: Offboarding checklist for {GitHub Username}
labels: ''
assignees: ''
---

# For everyone

- [ ] Remove from [the FAC-team Google Group](https://groups.google.com/a/gsa.gov/g/fac-team/members)
- [ ] Remove from [the FAC team in GitHub](https://github.com/orgs/GSA-TTS/teams/fac-team/members)
- [ ] Remove from the private channel #oros-fac-private in Slack (“/remove @[person]”)

**For designers, also...**

- [ ] Remove from active Figma projects

**For engineers, also...**

- [ ] Make a PR to [remove the departing team member from the list of developers and managers](https://github.com/GSA-TTS/FAC/tree/main/terraform/management/config.tf) with access to our spaces.
- [ ] [Remove the departing team member as a member of the FAC group in New Relic.](https://one.newrelic.com/admin-portal/organizations/users-list) (@GSA-TTS/fac-admins can do this)
    - [ ] If they're leaving TTS altogether, also delete their account. 


**For product leads/owners, also...**

- [ ] Make someone else the owner of [the various Google Groups in the project README](https://docs.google.com/document/d/1g8nYqYS_ifFlZB-DBgfeSoJRMB__EqWsmLnacyk-bDI/edit#heading=h.81zynabayrrg) (and remove them)
- [ ] Make someone else the Maintainer and remove the departing team member from [the FAC-admins team in GitHub](https://github.com/orgs/GSA-TTS/teams/fac-admins/members) and [the FAC-team team in GitHub](https://github.com/orgs/GSA-TTS/teams/fac-team/members).

