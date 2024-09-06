data "cloudfoundry_space" "app_space" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

resource "cloudfoundry_route" "app_route" {
  space    = data.cloudfoundry_space.app_space.id
  domain   = data.cloudfoundry_domain.public.id
  hostname = "${local.name}-${replace(var.cf_space_name, ".", "-")}"
  # Yields something like: gsa-fac-firstname-lastname.app.cloud.gov
}

resource "cloudfoundry_user_provided_service" "clam" {
  name  = "clamav_ups"
  space = data.cloudfoundry_space.app_space.id
  credentials = {
    "AV_SCAN_URL" : local.scan_url
  }
}

locals {
  name     = "gsa-fac"
  app_id   = cloudfoundry_app.fac_app.id
  scan_url = "https://fac-av-sandbox.apps.internal:61443/scan"
}

data "docker_registry_image" "web-app" {
  name = "ghcr.io/gsa-tts/fac/web-container:latest"
}

resource "cloudfoundry_app" "fac_app" {
  name      = local.name
  space     = data.cloudfoundry_space.app_space.id
  docker_image = "ghcr.io/gsa-tts/fac/web-container@${data.docker_registry_image.web-app.sha256_digest}"
  # path      = "${path.module}/${data.external.scannerzip.result.path}"
  #source_code_hash  = filesha256("${path.module}/${data.external.scannerzip.result.path}")
  timeout           = 180
  disk_quota        = 4096
  memory            = 128
  instances         = 1
  strategy          = "rolling"
  health_check_type = "port"

  service_binding {
    service_instance = cloudfoundry_user_provided_service.clam.id
  }

  routes {
    route = cloudfoundry_route.app_route.id
  }
}
