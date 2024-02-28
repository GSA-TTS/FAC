locals {
  clam_name = "fac-av-${var.cf_space_name}"
  module_versions = {
    clamav = "^8.x", # major version 8
  }
}

module "version" {
  for_each           = local.module_versions
  source             = "github.com/18f/terraform-cloudgov//semver"
  version_constraint = each.value
}

data "docker_registry_image" "clamav" {
  name = "ghcr.io/gsa-tts/fac/clamav:latest"
}

module "clamav" {
  source = "github.com/18f/terraform-cloudgov//clamav?ref=v${module.version["clamav"].target_version}"

  # This generates eg "fac-av-staging.apps.internal", avoiding collisions with routes for other projects and spaces
  name           = local.clam_name
  app_name_or_id = "gsa-fac"

  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space_name
  clamav_image  = "ghcr.io/gsa-tts/fac/clamav@${data.docker_registry_image.clamav.sha256_digest}"
  max_file_size = "30M"
  instances     = var.clamav_instances

  proxy_server   = module.https-proxy.domain
  proxy_port     = module.https-proxy.port
  proxy_username = module.https-proxy.username
  proxy_password = module.https-proxy.password
}

