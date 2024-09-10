data "cloudfoundry_domain" "internal" {
  name = "apps.internal"
}

data "cloudfoundry_space" "app_space" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

resource "cloudfoundry_route" "app_route" {
  space    = data.cloudfoundry_space.app_space.id
  domain   = data.cloudfoundry_domain.internal.id
  hostname = "${var.name}-${replace(var.cf_space_name, ".", "-")}"
  # Yields something like: fac-file-scanner-spacename.apps.internal
}

data "external" "app_zip" {
  program     = ["/bin/sh", "prepare_app.sh"]
  working_dir = path.module
  query = {
    gitref = var.gitref
  }
}

resource "cloudfoundry_user_provided_service" "clam" {
  name  = "clamav_ups"
  space = data.cloudfoundry_space.app_space.id
  credentials = {
    "AV_SCAN_URL" : local.scan_url
  }
}

locals {
  app_id   = cloudfoundry_app.fac_app.id
  scan_url = "https://fac-av-${var.cf_space_name}-fs.apps.internal:61443/scan"
}

resource "cloudfoundry_app" "fac_app" {
  name             = var.name
  space            = data.cloudfoundry_space.app_space.id
  buildpacks       = ["https://github.com/cloudfoundry/apt-buildpack.git", "https://github.com/cloudfoundry/python-buildpack.git"]
  path             = "${path.module}/${data.external.app_zip.result.path}"
  source_code_hash = filesha256("${path.module}/${data.external.app_zip.result.path}")
  #command           = "./Procfile"
  timeout           = 180
  disk_quota        = var.disk_quota
  memory            = var.app_memory
  instances         = var.app_instances
  strategy          = "rolling"
  health_check_type = "port"

  service_binding {
    service_instance = cloudfoundry_user_provided_service.clam.id
  }

  service_binding {
    service_instance = var.private_s3_id
  }
  service_binding {
    service_instance = var.public_s3_id
  }

  service_binding {
    service_instance = var.db_id
  }
  service_binding {
    service_instance = var.backup_db_id
  }

  routes {
    route = cloudfoundry_route.app_route.id
  }

  #   environment = {
  #     PROXYROUTE = var.https_proxy
  #   }
}
