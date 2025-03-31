# Since we're not platform admins, we need to look for user details in the
# context of our specific org.
data "cloudfoundry_org" "org" {
  name = local.org_name
}

# We need to include the meta deployer user in the set of users with the
# SpaceDeveloper role so it can manage the deployer service and binding in
# each space. We need to add it using the user ID rather than username in order
# to ensure it has the expected permissions. See
# https://github.com/cloudfoundry-community/terraform-provider-cloudfoundry/issues/436

# This id is accessed with data.cloudfoundry_user.meta_deployer.users.0.id
# https://registry.terraform.io/providers/cloudfoundry/cloudfoundry/latest/docs/data-sources/user#nested-schema-for-users
data "cloudfoundry_user" "meta_deployer" {
  name     = var.cf_user
}

module "environments" {
  for_each               = local.spaces
  source                 = "./bootstrap-env"
  name                   = each.key
  org_name               = local.org_name
  developers             = concat(local.developers, [data.cloudfoundry_user.meta_deployer.users.0.id])
  managers               = local.managers
  reponame               = "GSA-TTS/FAC"
  allow_ssh              = lookup(each.value, "allow_ssh", true)
  populate_creds_locally = var.populate_creds_locally
  # Apply egress ASGs if explicitly requested
  #
  # NOTE: This implies that we should have a 1:1 mapping between environments
  # and spaces. But that doesn't seem to be the case... We want to be able to
  # specify a staging configuration that spans across the `staging` and
  # `staging-egress` spaces, eg to set up network policies and inject client
  # credentials. So I think we'll be removing this option and having the
  # bootstrap-env module manage both spaces in a future PR!
  asgs = lookup(each.value, "allow_egress", false) ? tolist(local.egress_asgs) : tolist(local.internal_asgs)
}

locals {
  # Filters the list of spaces with a value of true for "uses_backups". We only want to share the bucket to those spaces.
  spaces_that_use_backups = join(" ", [for key, config in local.spaces : lookup(config, "uses_backups", false) ? key : ""])
}

data "cloudfoundry_org" "organization" {
  name = local.org_name
}

data "cloudfoundry_space" "space" {
  name = "production"
  org  = data.cloudfoundry_org.organization.id
}

module "s3-backups" {
  source = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v2.3.0"
  cf_space_id  = data.cloudfoundry_space.space.id
  name         = "backups"
  s3_plan_name = "basic"
  tags         = ["s3"]
}
