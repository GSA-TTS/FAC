data "cloudfoundry_domain" "public" {
  name = "app.cloud.gov"
}

data "cloudfoundry_space" "app_space" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

resource "cloudfoundry_route" "app_route" {
  space    = data.cloudfoundry_space.app_space.id
  domain   = data.cloudfoundry_domain.public.id
  hostname = "fac-${replace(var.cf_space_name, ".", "-")}"
  # Yields something like: fac-sandbox.app.cloud.gov
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


resource "cloudfoundry_user_provided_service" "credentials" {
  name             = "fac-key-service"
  space            = data.cloudfoundry_space.app_space.id
  credentials_json = <<JSON
  {
    "SAM_API_KEY": "${var.sam_api_key}",
    "DJANGO_SECRET_LOGIN_KEY": "${var.django_secret_login_key}",
    "LOGIN_CLIENT_ID": "${var.login_client_id}",
    "SECRET_KEY":"${var.login_secret_key}"
  }
  JSON
}

locals {
  app_id   = cloudfoundry_app.fac_app.id
  scan_url = "https://fac-av-${var.cf_space_name}-fs.apps.internal:61443/scan"
}

resource "cloudfoundry_app" "fac_app" {
  name                            = var.name
  space                           = data.cloudfoundry_space.app_space.id
  buildpacks                      = ["https://github.com/cloudfoundry/apt-buildpack.git", "https://github.com/cloudfoundry/python-buildpack.git"]
  path                            = "${path.module}/${data.external.app_zip.result.path}"
  source_code_hash                = filesha256("${path.module}/${data.external.app_zip.result.path}")
  disk_quota                      = var.disk_quota
  memory                          = var.app_memory
  instances                       = var.app_instances
  strategy                        = "rolling"
  timeout                         = 600
  health_check_type               = "port"
  health_check_timeout            = 180
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
    service_instance = var.https_proxy_creds_id
  }

  service_binding {
    service_instance = var.new_relic_creds_id
  }

  service_binding {
    service_instance = cloudfoundry_user_provided_service.credentials.id
  }

  routes {
    route = cloudfoundry_route.app_route.id
  }

  # # Uncomment when you have everything built, but its crashed
  # environment = {
  #   PROXYROUTE            = var.https_proxy
  #   ENV                   = "SANDBOX"
  #   DISABLE_COLLECTSTATIC = 1
  #   DJANGO_BASE_URL = "https://fac-${var.cf_space_name}.app.cloud.gov"
  #   AV_SCAN_URL = "https://fac-av-${var.cf_space_name}.apps.internal:61443/scan"
  # }

  # Use for the first deployment
  environment = {
    # PROXYROUTE            = var.https_proxy
    ENV = "SANDBOX"
    # DISABLE_COLLECTSTATIC = 0
    DJANGO_BASE_URL = "https://fac-${var.cf_space_name}.app.cloud.gov"
    AV_SCAN_URL     = "https://fac-av-${var.cf_space_name}.apps.internal:61443/scan"
    ALLOWED_HOSTS   = "fac-${var.cf_space_name}.app.cloud.gov"
  }
}
