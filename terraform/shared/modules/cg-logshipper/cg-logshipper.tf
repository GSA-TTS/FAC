data "cloudfoundry_domain" "internal" {
  name = "apps.internal"
}

data "cloudfoundry_space" "apps" {
  org_name = var.cf_org_name
  name     = var.client_space
}

resource "cloudfoundry_route" "logshipper" {
  space    = data.cloudfoundry_space.apps.id
  domain   = data.cloudfoundry_domain.internal.id
  hostname = "${var.cf_org_name}-${replace(var.cf_space_name, ".", "-")}-${var.name}"
}

resource "random_uuid" "username" {}
resource "random_password" "password" {
  length  = 16
  special = false
}

data "cloudfoundry_space" "egress_space" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

locals {
  username = random_uuid.username.result
  password = random_password.password.result
}

resource "cloudfoundry_user_provided_service" "logshipper_creds" {
  name  = "logshipper-creds"
  space = data.cloudfoundry_space.apps.id
  credentials = {
    "HTTP_USER" = local.username
    "HTTP_PASS" = local.password
  }
}

resource "cloudfoundry_user_provided_service" "loghipper_new_relic_creds" {
  name  = "newrelic-creds-logshipper"
  space = data.cloudfoundry_space.apps.id
  credentials = {
    "NEW_RELIC_LICENSE_KEY"   = var.new_relic_license_key
    "NEW_RELIC_LOGS_ENDPOINT" = "https://gov-log-api.newrelic.com/log/v1"
  }
}

resource "cloudfoundry_app" "cg_logshipper_app" {
  name      = var.name
  space     = data.cloudfoundry_space.apps.id
  buildpack = "binary_buildpack"
  memory    = var.logshipper_memory
  instances = var.logshipper_instances
  strategy  = "rolling"

  routes {
    route = cloudfoundry_route.logshipper.id
  }

  environment = {
    PROXYROUTE = var.https_proxy
  }
}
