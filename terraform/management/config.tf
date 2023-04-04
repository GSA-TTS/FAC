locals {
  org_name = "gsa-tts-oros-fac"
  spaces = [
    "dev",
    "staging",
    "production",
    "management"
  ]

  # All spaces have the same SpaceDevelopers for now
  developers = [
    # Mirrors @GSA-TTS/FAC-team (developers)
    # https://github.com/orgs/GSA-TTS/teams/fac-team/members
    # TODO: Automate updates via GitHub's GraphQL API
    "bret.mogilefsky@gsa.gov",
    "lindsayn.young@gsa.gov",
    "james.person@gsa.gov",
    "jeanmarie.mariadassou@gsa.gov",
    "matt.henry@gsa.gov",
    "tadhg.ohiggins@gsa.gov",
    "timothy.ballard@gsa.gov",
    "matthew.jadud@gsa.gov",
    "edward.zapata@gsa.gov",
    "hassandeme.mamasambo@gsa.gov",
  ]

  # All spaces have the same SpaceManagers for now
  managers = [
    # The OrgManager user explicitly sets itself as a SpaceManager for each space
    var.cf_user,

    # Mirrors @GSA-TTS/FAC-admins
    # https://github.com/orgs/GSA-TTS/teams/fac-admins/members
    # TODO: Automate updates via GitHub's GraphQL API
    "bret.mogilefsky@gsa.gov",
    "jeanmarie.mariadassou@gsa.gov",
    "tadhg.ohiggins@gsa.gov",
  ]

  # All spaces have full public egress (for now)
  asgs = [
    "trusted_local_networks",
    "public_networks_egress"
  ]
}

