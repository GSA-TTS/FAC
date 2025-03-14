# We need the Org GUID to describe spaces
data "cloudfoundry_org" "org" {
  name = var.org_name
}

data "cloudfoundry_asg" "asgs" {
  provider = cloudfoundry-community
  for_each = toset(var.asgs)
  name     = each.key
}

# Ensure the space exists and is configured as expected
resource "cloudfoundry_space" "space" {
  provider                 = cloudfoundry-community
  name                     = var.name
  org                      = data.cloudfoundry_org.org.id
  allow_ssh                = var.allow_ssh
  delete_recursive_allowed = false
}

resource "cloudfoundry_space_asgs" "space_asgs" {
  provider     = cloudfoundry-community
  space        = cloudfoundry_space.space.id
  running_asgs = values(data.cloudfoundry_asg.asgs)[*].id
}

resource "cloudfoundry_space_users" "space_permissions" {
  provider   = cloudfoundry-community
  space      = cloudfoundry_space.space.id
  developers = var.developers
  managers   = var.managers
}
