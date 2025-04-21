data "cloudfoundry_domain" "public" {
  name = "app.cloud.gov"
}

data "cloudfoundry_org" "app_org" {
  name = var.cf_org_name
}

data "cloudfoundry_space" "app_space" {
  name = var.cf_space_name
  org  = data.cloudfoundry_org.app_org.id
}

resource "cloudfoundry_route" "app_route" {
  space        = data.cloudfoundry_space.app_space.id
  domain       = data.cloudfoundry_domain.public.id
  host         = "fac-${replace(var.cf_space_name, ".", "-")}"
  destinations = [{ app_id = cloudfoundry_app.fac_app.id }]
  # Yields something like: fac-sandbox.app.cloud.gov
}

data "external" "app_zip" {
  program     = ["/bin/sh", "prepare_app.sh"]
  working_dir = path.module
  query = {
    gitref = var.gitref
  }
}

resource "cloudfoundry_service_instance" "key_service" {
  name        = "fac-key-service"
  type        = "user-provided"
  tags        = ["fac-key-service"]
  space       = data.cloudfoundry_space.app_space.id
  credentials = <<KEYSSVC
  {
    "SAM_API_KEY": "${var.sam_api_key}",
    "DJANGO_SECRET_LOGIN_KEY": "${var.django_secret_login_key}",
    "LOGIN_CLIENT_ID": "${var.login_client_id}",
    "SECRET_KEY":"${var.login_secret_key}"
  }
  KEYSSVC
}

locals {
  app_id    = cloudfoundry_app.fac_app.id
  scan_url  = "https://fac-av-${var.cf_space_name}-fs.apps.internal:61443/scan"
  app_route = coalesce(var.route, "${var.name}.app.cloud.gov")
  services = merge({
    "${cloudfoundry_service_instance.key_service.name}" = ""
  }, var.service_bindings)
}

resource "cloudfoundry_app" "fac_app" {
  name       = var.name
  space_name = var.cf_space_name
  org_name   = var.cf_org_name

  path             = "${path.module}/${data.external.app_zip.result.path}"
  source_code_hash = filesha256("${path.module}/${data.external.app_zip.result.path}")

  buildpacks        = var.buildpacks
  memory            = var.app_memory
  disk_quota        = var.disk_quota
  instances         = var.app_instances
  strategy          = "rolling"
  health_check_type = "port"

  service_bindings = [
    for service_name, params in local.services : {
      service_instance = service_name
      params           = (params == "" ? "{}" : params) # Empty string -> Minimal JSON
    }
  ]
  environment = merge({
    REQUESTS_CA_BUNDLE = "/etc/ssl/certs/ca-certificates.crt"
  }, var.environment_variables)
}
