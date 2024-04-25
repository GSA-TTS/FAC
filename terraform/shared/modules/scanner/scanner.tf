data "cloudfoundry_domain" "internal" {
  name = "apps.internal"
}

data "cloudfoundry_space" "scanner_space" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

resource "cloudfoundry_route" "scanner_route" {
  space    = data.cloudfoundry_space.scanner_space.id
  domain   = data.cloudfoundry_domain.internal.id
  hostname = "${var.cf_org_name}-${replace(var.cf_space_name, ".", "-")}-${var.name}"
  # Yields something like: orgname-spacename-name.apps.internal
}

data "external" "scannerzip" {
  program     = ["/bin/sh", "prepare-scanner.sh"]
  working_dir = path.module
  query = {
    gitref = var.gitref
  }
}

locals {
  app_id = cloudfoundry_app.scanner_app.id
}

resource "cloudfoundry_app" "scanner_app" {
  name      = var.name
  space     = data.cloudfoundry_space.scanner_space.id
  buildpack = "python_buildpack"
  path      = "${path.module}/${data.external.scannerzip.result.path}"
  # source_code_hash  = filesha256("${path.module}/${data.external.scannerzip.result.path}")
  timeout           = 180
  disk_quota        = var.disk_quota
  memory            = var.scanner_memory
  instances         = var.scanner_instances
  strategy          = "rolling"
  health_check_type = "process"

  routes {
    route = cloudfoundry_route.scanner_route.id
  }

  service_binding {
    service_instance = var.clamav_id
  }

  service_binding {
    service_instance = var.s3_id
  }

  service_binding {
    service_instance = var.db_id
  }
}

