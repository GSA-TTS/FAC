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

  asgs = [for d in data.cloudfoundry_asg.asgs : d.id]

  # Until the CF provider can properly handle ASGs, we're handling removal of the public_egress ASG manually outside of Terraform.
  # https://github.com/cloudfoundry-community/terraform-provider-cloudfoundry/issues/405
  lifecycle {
    ignore_changes = [
      asgs,
    ]
  }
}

resource "cloudfoundry_space_users" "space_permissions" {
  for_each   = toset(local.spaces)
  space      = cloudfoundry_space.space[each.key].id
  developers = local.developers
  managers   = local.managers
}

