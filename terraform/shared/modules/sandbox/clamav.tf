locals {
  clam_name    = "fac-av-${var.cf_space.name}"
  fs_clam_name = "fac-av-${var.cf_space.name}-fs"
}

data "docker_registry_image" "clamav" {
  name = "ghcr.io/gsa-tts/fac/clamav:latest"
}

module "clamav" {
  source = "github.com/gsa-tts/terraform-cloudgov//clamav?ref=v2.2.0"

  # This generates eg "fac-av-staging.apps.internal", avoiding collisions with routes for other projects and spaces
  name = local.clam_name

  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space.name

  clamav_image  = "ghcr.io/gsa-tts/fac/clamav@${data.docker_registry_image.clamav.sha256_digest}"
  clamav_memory = var.clamav_memory
  max_file_size = "30M"
  instances     = var.clamav_instances

  proxy_server   = module.https-proxy.domain
  proxy_port     = module.https-proxy.https_port
  proxy_username = module.https-proxy.username
  proxy_password = module.https-proxy.password
}

module "file_scanner_clamav" {
  source = "github.com/gsa-tts/terraform-cloudgov//clamav?ref=v2.2.0"

  # This generates eg "fac-av-staging-fs.apps.internal", avoiding collisions with routes for other projects and spaces
  name = local.fs_clam_name

  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space.name
  clamav_image  = "ghcr.io/gsa-tts/fac/clamav@${data.docker_registry_image.clamav.sha256_digest}"
  max_file_size = "30M"
  instances     = var.clamav_fs_instances
  clamav_memory = var.clamav_memory

  proxy_server   = module.https-proxy.domain
  proxy_port     = module.https-proxy.https_port
  proxy_username = module.https-proxy.username
  proxy_password = module.https-proxy.password
}
