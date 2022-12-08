locals {
  org_name = "gsa-tts-oros-fac"
  spaces = [
    "dev", 
    "staging", 
    "production", 
    "management"
  ]

  developers  = [
    "bret.mogilefsky@gsa.gov",
    "lindsayn.young@gsa.gov",
    "jason.nakai@gsa.gov",
    "jeanmarie.mariadassou@gsa.gov",
    "matt.henry@gsa.gov",
    "sarah.withee@gsa.gov",
    "tadhg.ohiggins@gsa.gov",
    "timothy.ballard@gsa.gov",
  ]
  
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

  asgs = [
    "trusted_local_networks",
    "public_networks_egress"
  ]
}

