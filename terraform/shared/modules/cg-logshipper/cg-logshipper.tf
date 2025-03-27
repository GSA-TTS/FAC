locals {
  username = random_uuid.username.result
  password = random_password.password.result
  # The syslog_drain must be registered on the public domain for cloudfoundry.
  # Cloud Foundry uses the syslog URL to route messages to the service.
  # The syslog URL has a scheme of syslog, syslog-tls, or https, and can include a port number.
  # More information here:
  # https://docs.cloudfoundry.org/devguide/services/log-management.html
  # https://docs.cloudfoundry.org/devguide/services/user-provided.html#syslog
  syslog_drain = "https://${local.username}:${local.password}@${cloudfoundry_route.logshipper_route.host}.app.cloud.gov/?drain-type=all"
  domain       = cloudfoundry_route.logshipper_route.domain
  app_id       = cloudfoundry_app.logshipper_app.id
  route        = "${var.cf_space.name}-${var.name}.app.cloud.gov"

  logshipper_creds_name = "logshipper-creds"

  services = merge({
    "${local.logshipper_creds_name}" = ""
    # "${module.logshipper-storage.bucket_name}" = ""
    "log-storage" = ""
  }, var.service_bindings)
}

data "cloudfoundry_domain" "public" {
  name = "app.cloud.gov"
}

module "logshipper-storage" {
  source       = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v2.2.0"
  cf_space_id  = var.cf_space.id
  name         = "log-storage"
  s3_plan_name = "basic"
  tags         = ["logshipper-s3"]
}

resource "cloudfoundry_route" "logshipper_route" {
  space        = var.cf_space.id
  domain       = data.cloudfoundry_domain.public.id
  host         = "fac-${var.cf_space.name}-${var.name}"
  destinations = [{ app_id = cloudfoundry_app.logshipper_app.id }]
  # Yields something like: fac-dev-logshipper.app.cloud.gov
}

resource "cloudfoundry_service_instance" "logshipper_creds" {
  name        = local.logshipper_creds_name
  type        = "user-provided"
  tags        = ["logshipper-creds"]
  space       = var.cf_space.id
  credentials = <<CREDS
  {
    "HTTP_USER": "${local.username}",
    "HTTP_PASS": "${local.password}"
  }
  CREDS
}

resource "cloudfoundry_service_instance" "logdrain" {
  name             = var.syslog_drain_name
  type             = "user-provided"
  tags             = ["syslog-drain"]
  space            = var.cf_space.id
  syslog_drain_url = local.syslog_drain
}

resource "random_uuid" "username" {}
resource "random_password" "password" {
  length  = 16
  special = false
}

data "external" "logshipper_zip" {
  program     = ["/bin/sh", "prepare-logshipper.sh"]
  working_dir = path.module
  query = {
    gitref = var.gitref
  }
}

resource "cloudfoundry_app" "logshipper_app" {
  name       = var.name
  space_name = var.cf_space.name
  org_name   = var.cf_org_name

  buildpacks       = ["https://github.com/cloudfoundry/apt-buildpack.git", "nginx_buildpack"]
  path             = "${path.module}/${data.external.logshipper_zip.result.path}"
  source_code_hash = filesha256("${path.module}/${data.external.logshipper_zip.result.path}")

  disk_quota        = var.disk_quota
  memory            = var.logshipper_memory
  instances         = var.logshipper_instances
  strategy          = "rolling"
  health_check_type = "process"

  sidecars = [{
    name          = "fluentbit"
    command       = "/home/vcap/deps/0/apt/opt/fluent-bit/bin/fluent-bit -Y -c fluentbit.conf"
    process_types = ["web"]
  }]

  service_bindings = [
    for service_name, params in local.services : {
      service_instance = service_name
      params           = (params == "" ? "{}" : params) # Empty string -> Minimal JSON
    }
  ]

  environment = {
    PROXYROUTE = var.https_proxy
  }
}
