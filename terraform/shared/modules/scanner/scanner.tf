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

resource "cloudfoundry_user_provided_service" "clam" {
  name  = "clamav_ups"
  space = data.cloudfoundry_space.scanner_space.id
  credentials = {
    "AV_SCAN_URL" : local.scan_url
  }
}

module "quarantine" {
  source = "github.com/18f/terraform-cloudgov//s3?ref=v0.9.1"

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-file-scanner-quarantine"
  recursive_delete = var.recursive_delete
  s3_plan_name     = "basic"
  tags             = ["s3"]
}

locals {
  app_id   = cloudfoundry_app.scanner_app.id
  scan_url = "https://fac-av-${var.cf_space_name}-fs.apps.internal:61443/scan"
}

resource "cloudfoundry_app" "scanner_app" {
  name      = var.name
  space     = data.cloudfoundry_space.scanner_space.id
  buildpack = "https://github.com/cloudfoundry/python-buildpack"
  path      = "${path.module}/${data.external.scannerzip.result.path}"
  #source_code_hash  = filesha256("${path.module}/${data.external.scannerzip.result.path}")
  timeout           = 180
  disk_quota        = var.disk_quota
  memory            = var.scanner_memory
  instances         = var.scanner_instances
  strategy          = "rolling"
  health_check_type = "port"

  service_binding {
    service_instance = cloudfoundry_user_provided_service.clam.id
  }

  service_binding {
    service_instance = var.s3_id
  }

  service_binding {
    service_instance = module.quarantine.bucket_id
  }

  service_binding {
    service_instance = var.db_id
  }

  service_binding {
    service_instance = var.logdrain_id
  }

  routes {
    route = cloudfoundry_route.scanner_route.id
  }

  environment = {
    PROXYROUTE = var.https_proxy
  }
}
