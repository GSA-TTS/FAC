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
data "cloudfoundry_user" "meta_deployer" {
  provider = cloudfoundry-community
  name     = var.cf_user
  org_id   = data.cloudfoundry_org.org.id
}

module "environments" {
  for_each               = local.spaces
  source                 = "./bootstrap-env"
  name                   = each.key
  org_name               = local.org_name
  developers             = concat(local.developers, [data.cloudfoundry_user.meta_deployer.id])
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

module "s3-backups" {
  source = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v1.1.0"

  cf_org_name = local.org_name
  # TODO: This should be the key for the first space that says "is_production =
  # true" rather than being hardcoded
  cf_space_name = "production"
  name          = "backups"
  s3_plan_name  = "basic"
  tags          = ["s3"]
}

# TODO: We should have a corresponding "unshar-backup-from-spaces" resource, in
# case a space is removed from the list

# resource "null_resource" "share-backup-to-spaces" {
#   provisioner "local-exec" {
#     environment = {
#       SPACES = "${local.spaces_that_use_backups}"
#     }
#     command = "for space in $SPACES ; do cf share-service backups -s $space; done"
#   }
#   depends_on = [
#     module.s3-backups
#   ]
# }
