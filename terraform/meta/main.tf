module "environments" {
  for_each   = toset(local.spaces)
  source     = "./bootstrap-env"
  name       = each.key
  org_name   = local.org_name
  developers = local.developers
  managers   = local.managers
  asgs       = tolist(local.internal_asgs)
  reponame   = "GSA-TTS/FAC"
}

module "environments-egress" {
  for_each   = toset(local.spaces)
  source     = "./bootstrap-env"
  name       = "${each.key}-egress"
  org_name   = local.org_name
  developers = local.developers
  managers   = local.managers
  asgs       = local.egress_asgs
}

# Migrate state from the old addresses to the new addresses
# These moved blocks only need to be here until this is applied to the live state.
# And before you ask why this is so repetitive: No, we cannot use for_each with moved blocks.
moved {
  from = cloudfoundry_space.space["dev"]
  to   = module.environments["dev"].cloudfoundry_space.space
}
moved {
  from = cloudfoundry_space_users.space_permissions["dev"]
  to   = module.environments["dev"].cloudfoundry_space_users.space_permissions
}

moved {
  from = cloudfoundry_space.space["staging"]
  to   = module.environments["staging"].cloudfoundry_space.space
}
moved {
  from = cloudfoundry_space_users.space_permissions["staging"]
  to   = module.environments["staging"].cloudfoundry_space_users.space_permissions
}

moved {
  from = cloudfoundry_space.space["production"]
  to   = module.environments["production"].cloudfoundry_space.space
}
moved {
  from = cloudfoundry_space_users.space_permissions["production"]
  to   = module.environments["production"].cloudfoundry_space_users.space_permissions
}

moved {
  from = cloudfoundry_space.space["management"]
  to   = module.environments["management"].cloudfoundry_space.space
}
moved {
  from = cloudfoundry_space_users.space_permissions["management"]
  to   = module.environments["management"].cloudfoundry_space_users.space_permissions
}
