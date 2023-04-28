# We need the Org GUID to describe spaces
data "cloudfoundry_org" "org" {
  name = local.org_name
}

data "cloudfoundry_asg" "asgs" {
  for_each = toset(local.asgs)
  name     = each.key
}

locals {
  egress_spaces = [for s in local.spaces : "${s}-egress"]
  all_spaces    = setunion(local.spaces, local.egress_spaces)
}

# Ensure spaces exist
resource "cloudfoundry_space" "space" {
  for_each = toset(local.all_spaces)
  name     = each.key
  org      = data.cloudfoundry_org.org.id

  # Disallow SSH access in production and production-egress
  allow_ssh = (each.key != "production" && each.key != "production-egress")

  asgs = [for d in data.cloudfoundry_asg.asgs : d.id]
}

# Grant the expected people access
resource "cloudfoundry_space_users" "space_permissions" {
  for_each   = toset(local.all_spaces)
  space      = cloudfoundry_space.space[each.key].id
  developers = local.developers
  managers   = local.managers
}

### 
# Ensure a deployer account exists in each space, and that it has the
# SpaceDeveloper role on the corresponding -egress space
###

data "cloudfoundry_service" "service-account" {
  name = "cloud-gov-service-account"
}

resource "cloudfoundry_service_instance" "space-deployer" {
  for_each     = toset(local.spaces)
  name         = "${each.key}-deployer"
  space        = cloudfoundry_space.space[each.key].id
  service_plan = "space-deployer"
}

resource "cloudfoundry_service_key" "space-deployer-key" {
  for_each         = toset(local.spaces)
  name             = "${each.key}-deployer-key"
  service_instance = cloudfoundry_service_instance.space-deployer[each.key].id
}

resource "cloudfoundry_space_users" "egress-deployer" {
  for_each   = toset(local.spaces)
  space      = cloudfoundry_space.space["${each.key}-egress"].id
  developers = [cloudfoundry_service_key.space-deployer-key[each.key].credentials.username]
}
