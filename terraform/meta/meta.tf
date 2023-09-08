module "environments" {
  for_each               = local.spaces
  source                 = "./bootstrap-env"
  name                   = each.key
  org_name               = local.org_name
  developers             = local.developers
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
