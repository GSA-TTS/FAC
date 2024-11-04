locals {
  clam_name = "fac-av-${var.cf_space_name}"
}

data "docker_registry_image" "clamav" {
  name = "ghcr.io/gsa-tts/fac/clamav:latest"
}

module "clamav" {
  source = "github.com/gsa-tts/terraform-cloudgov//clamav?ref=v0.9.0"

  # This generates eg "fac-av-staging.apps.internal", avoiding collisions with routes for other projects and spaces
  name           = local.clam_name
  app_name_or_id = "gsa-fac"

  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space_name
  clamav_image  = "ghcr.io/gsa-tts/fac/clamav@${data.docker_registry_image.clamav.sha256_digest}"
  max_file_size = "30M"
  instances     = var.clamav_instances
  clamav_memory = var.clamav_memory

  proxy_server   = module.https-proxy.domain
  proxy_port     = module.https-proxy.port
  proxy_username = module.https-proxy.username
  proxy_password = module.https-proxy.password
  depends_on = [ module.fac-app.app_id ]
  # depends_on     = [ module.https-proxy.https_proxy ]
}

# resource "cloudfoundry_network_policy" "clamav-network-policy" {
#   policy {
#     source_app      = module.clamav.app_id
#     destination_app = module.https-proxy.app_id
#     port            = "61443"
#     protocol        = "tcp"
#   }
# }
