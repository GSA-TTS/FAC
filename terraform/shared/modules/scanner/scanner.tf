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
  hostname = "${var.name}-${replace(var.cf_space_name, ".", "-")}"
  # Yields something like: fac-file-scanner-spacename.apps.internal
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
  buildpack = "https://github.com/cloudfoundry/python-buildpack"
  path      = "${path.module}/${data.external.scannerzip.result.path}"
  # source_code_hash  = filesha256("${path.module}/${data.external.scannerzip.result.path}")
  timeout           = 180
  disk_quota        = var.disk_quota
  memory            = var.scanner_memory
  instances         = var.scanner_instances
  strategy          = "rolling"
  health_check_type = "port"

  service_binding {
    service_instance = var.s3_id
  }

  service_binding {
    service_instance = var.db_id
  }

  routes {
    route = cloudfoundry_route.scanner_route.id
  }

  environment = {
    PROXYROUTE = var.https_proxy
  }
}
