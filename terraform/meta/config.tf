locals {
  org_name = "gsa-tts-oros-fac"
  spaces = {
    "dev"     = {},
    "preview" = {},
    "staging" = {
      uses_backups = true
    },
    "production" = {
      allow_ssh     = false,
      uses_backups  = true,
      is_production = true
    },
  }

  # All spaces have the same SpaceDevelopers for now
  developers = [
    # Mirrors @GSA-TTS/FAC-team (developers)
    # https://github.com/orgs/GSA-TTS/teams/fac-team/members
    # TODO: Automate updates via GitHub's GraphQL API
    "bret.mogilefsky@gsa.gov",
    "james.person@gsa.gov",
    "matthew.jadud@gsa.gov",
    "hassandeme.mamasambo@gsa.gov",
    "alexander.steel@gsa.gov",
    "sudha.kumar@gsa.gov",
    "philip.dominguez@gsa.gov",
    "robert.novak@gsa.gov",
    "ranye.mclendon@gsa.gov",
  ]

  # All spaces have the same SpaceManagers for now
  managers = [
    # The OrgManager user explicitly sets itself as a SpaceManager for each space
    var.cf_user,

    # Mirrors @GSA-TTS/FAC-admins
    # https://github.com/orgs/GSA-TTS/teams/fac-admins/members
    # TODO: Automate updates via GitHub's GraphQL API
    "bret.mogilefsky@gsa.gov",
    "matthew.jadud@gsa.gov",
    "alexander.steel@gsa.gov",
  ]

  internal_asgs = [
    # Why are these both here? See Slack:
    # https://gsa-tts.slack.com/archives/C09CR1Q9Z/p1691079035528469
    "trusted_local_networks",
    "trusted_local_networks_egress",
  ]

  # All egress spaces include full public egress
  egress_asgs = [
    "trusted_local_networks",
    "public_networks_egress"
  ]
}

