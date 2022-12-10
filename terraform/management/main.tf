# We need the Org GUID to describe spaces
data "cloudfoundry_org" "org" {
  name = local.org_name
}

data "cloudfoundry_asg" "asgs" {
  for_each = toset(local.asgs)
  name     = each.key
}

# Ensure spaces exist
resource "cloudfoundry_space" "space" {
  for_each = toset(local.spaces)
  name     = each.key
  org      = data.cloudfoundry_org.org.id

  # Disallow SSH access in production
  allow_ssh = each.key != "production"

  # All spaces have full public egress (for now)
  asgs = [for d in data.cloudfoundry_asg.asgs : d.id]
}

# Everyone has SpaceDeveloper permission in all spaces
resource "cloudfoundry_space_users" "space_permissions" {
  for_each   = toset(local.spaces)
  space      = cloudfoundry_space.space[each.key].id
  developers = local.developers
  managers   = local.managers
}

