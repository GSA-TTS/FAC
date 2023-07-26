locals {
  clam_name = "fac-av-${var.cf_space_name}"
}

data "docker_registry_image" "clamav" {
  name = "ghcr.io/gsa-tts/fac/clamav:latest"
}

module "clamav" {
  source = "github.com/18f/terraform-cloudgov//clamav?ref=v0.6.0"

  # This generates eg "fac-av-staging.apps.internal", avoiding collisions with routes for other projects and spaces
  name           = local.clam_name
  app_name_or_id = "gsa-fac"

  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space_name
  clamav_image  = "ghcr.io/gsa-tts/fac/clamav@sha256:${data.docker_registry_image.clamav.sha256_digest}"
  max_file_size = "30M"

  proxy_server   = module.https-proxy.domain
  proxy_port     = module.https-proxy.port
  proxy_username = module.https-proxy.username
  proxy_password = module.https-proxy.password
}

