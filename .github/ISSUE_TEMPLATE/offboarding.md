---
name: Offboarding
about: An offboarding checklist for folks leaving the team
title: Offboarding checklist for {GitHub Username}
labels: ''
assignees: ''
---

## For everyone

- [ ] Remove from Google groups as applicable:
  - [ ] [FAC-team](https://groups.google.com/a/gsa.gov/g/fac-team/members) 
  - [ ] [fac-gov-test-users](https://groups.google.com/a/gsa.gov/g/fac-gov-test-users/members)
  - [ ] [fac-gov-api-dev](https://groups.google.com/a/gsa.gov/g/fac-gov-api-dev)
- [ ] Remove from [the FAC team in GitHub](https://github.com/orgs/GSA-TTS/teams/fac-team/members)
- [ ] Remove from the private channels #oros-fac-private and #fac-helpdesk in Slack (“/remove @[person]”)
- [ ] Remove from active Figma projects
- [ ] Remove from Mural
- [ ] Remove from Zendesk 
- [ ] Check for and remove admin access in the FAC application: this may include designated permissions and/or checked-in API  access ([for example](https://github.com/GSA-TTS/FAC/blob/fb0e7bdf1cb1807291e6b6eef068e97b4574078c/backend/support/api/admin_api_v1_1_0/create_access_tables.sql#L21))

## For GitHub contributors
- [ ] Make a PR to [remove the departing team member from the list of developers and managers](https://github.com/GSA-TTS/FAC/tree/main/terraform/meta/config.tf) with access to our spaces.
- [ ] [Remove the departing team member as a member of the FAC group in New Relic.](https://one.newrelic.com/admin-portal/organizations/users-list) (@GSA-TTS/fac-admins can do this)
    - [ ] If they're leaving TTS altogether, also delete their account. 

## For admins
- [ ] If the departing team member is a Google Group manager, designate a new manager for any groups they manage.
- [ ] If they are the on Make someone else the Maintainer and remove the departing team member from [the FAC-admins team in GitHub](https://github.com/orgs/GSA-TTS/teams/fac-admins/members) and [the FAC-team team in GitHub](https://github.com/orgs/GSA-TTS/teams/fac-team/members).
- [ ] Remove any deployment tokens associated with the PL/PO from the repository.
