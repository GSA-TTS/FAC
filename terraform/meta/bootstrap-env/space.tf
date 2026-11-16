# We need the Org GUID to describe spaces
data "cloudfoundry_org" "org" {
  name = var.org_name
}

data "cloudfoundry_security_group" "security_group" {
  for_each = toset(var.asgs)
  name     = each.key
}

# Ensure the space exists and is configured as expected
resource "cloudfoundry_space" "space" {
  name      = var.name
  org       = data.cloudfoundry_org.org.id
  allow_ssh = var.allow_ssh
}

resource "cloudfoundry_security_group_space_bindings" "space_asgs" {
  for_each       = data.cloudfoundry_security_group.security_group
  security_group = each.value.id
  running_spaces = [cloudfoundry_space.space.id]
}

resource "cloudfoundry_space_role" "manager" {
  for_each = toset(var.managers)
  username = each.value
  type     = "space_manager"
  space    = cloudfoundry_space.space.id
}

resource "cloudfoundry_space_role" "developer" {
  for_each = toset(var.developers)
  username = each.value
  type     = "space_developer"
  space    = cloudfoundry_space.space.id
}
