module environments {
  for_each = toset(local.spaces)
  source = "../shared/modules/bootstrap-env"
  name = each.key
  org_name = local.org_name
  developers = local.developers
  managers   = local.managers
  asgs = local.asgs
}

module environments-egress {
  for_each = toset(local.spaces)
  source = "../shared/modules/bootstrap-env"
  name = "${each.key}-egress"
  org_name = local.org_name
  developers = local.developers
  managers   = local.managers
  asgs = local.egress_asgs
}
