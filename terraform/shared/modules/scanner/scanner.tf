data "cloudfoundry_domain" "internal" {
  name = "apps.internal"
}

resource "cloudfoundry_route" "scanner_route" {
  space        = var.cf_space.id
  domain       = data.cloudfoundry_domain.internal.id
  host         = "${var.name}-${replace(var.cf_space.name, ".", "-")}"
  destinations = [{ app_id = cloudfoundry_app.scanner_app.id }]
  # Yields something like: fac-file-scanner-spacename.apps.internal
}

data "external" "scannerzip" {
  program     = ["/bin/sh", "prepare-scanner.sh"]
  working_dir = path.module
  query = {
    gitref = var.gitref
  }
}

resource "cloudfoundry_service_instance" "clam_ups_fs" {
  name        = "clamav_ups"
  type        = "user-provided"
  tags        = ["clamav-ups"]
  space       = var.cf_space.id
  credentials = <<CLAMAVUPS
  {"AV_SCAN_URL": "${local.scan_url}"}
  CLAMAVUPS
}

module "quarantine" {
  source       = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v2.3.0"
  cf_space_id  = var.cf_space.id
  name         = "fac-file-scanner-quarantine"
  s3_plan_name = "basic"
  tags         = ["s3"]
}

locals {
  app_id   = cloudfoundry_app.scanner_app.id
  scan_url = "https://fac-av-${var.cf_space.name}-fs.apps.internal:61443/scan"
  services = merge({
    "${cloudfoundry_service_instance.clam_ups_fs.name}" = ""
    "${module.quarantine.bucket_name}"                  = ""
  }, var.service_bindings)
}


resource "cloudfoundry_app" "scanner_app" {
  name       = var.name
  space_name = var.cf_space.name
  org_name   = var.cf_org_name

  buildpacks       = ["https://github.com/cloudfoundry/python-buildpack"]
  path             = "${path.module}/${data.external.scannerzip.result.path}"
  source_code_hash = filesha256("${path.module}/${data.external.scannerzip.result.path}")

  timeout           = 180
  disk_quota        = var.disk_quota
  memory            = var.scanner_memory
  instances         = var.scanner_instances
  strategy          = "rolling"
  health_check_type = "port"

  service_bindings = [
    for service_name, params in local.services : {
      service_instance = service_name
      params           = (params == "" ? "{}" : params) # Empty string -> Minimal JSON
    }
  ]
  environment = {
    PROXYROUTE = "${var.https_proxy}"
  }
  depends_on = [module.quarantine]
}
