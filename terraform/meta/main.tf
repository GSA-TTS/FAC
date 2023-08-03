module "environments" {
  for_each   = local.spaces
  source     = "./bootstrap-env"
  name       = each.key
  org_name   = local.org_name
  developers = local.developers
  managers   = local.managers
  asgs       = tolist(local.internal_asgs)
  reponame   = "GSA-TTS/FAC"
  allow_ssh  = lookup(each.value, "allow_ssh", true)
}
