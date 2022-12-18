# We need the Org GUID to describe spaces
data "cloudfoundry_org" "org" {
  name = var.org_name
}

data "cloudfoundry_asg" "asgs" {
  for_each = toset(var.asgs)
  name     = each.key
}

# Ensure the space exists and is configured as expected
resource "cloudfoundry_space" "space" {
  name     = var.name
  org      = data.cloudfoundry_org.org.id

  # Disallow SSH access for the special name production
  allow_ssh = var.name != "production"

  developers = var.developers
  managers   = var.managers
  # TODO: Not currently possible to specify ASGs due to a bug in the Terraform provider
  #   See https://github.com/cloudfoundry-community/terraform-provider-cloudfoundry/issues/435
  # asgs = [for d in data.cloudfoundry_asg.asgs : d.id]
}

resource "cloudfoundry_space_users" "space_permissions" {
  space      = cloudfoundry_space.space.id
  developers = var.developers
  managers   = var.managers
}
