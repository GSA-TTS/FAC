module "environments" {
  for_each   = toset(local.spaces)
  source     = "./bootstrap-env"
  name       = each.key
  org_name   = local.org_name
  developers = local.developers
  managers   = local.managers
  asgs       = tolist(local.internal_asgs)
  reponame   = "GSA-TTS/FAC"
}
