data "cloudfoundry_domain" "public" {
  name = "app.cloud.gov"
}

data "cloudfoundry_space" "apps" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

module "s3-logshipper-storage" {
  source = "github.com/18f/terraform-cloudgov//s3?ref=v0.8.0"

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "log-storage"
  recursive_delete = false
  s3_plan_name     = "basic"
  tags             = ["logshipper-s3"]
}

resource "cloudfoundry_service_key" "logshipper-s3-service-key" {
  name             = "fac-to-gsa"
  service_instance = module.s3-logshipper-storage.bucket_id
}

resource "cloudfoundry_route" "logshipper" {
  space    = data.cloudfoundry_space.apps.id
  domain   = data.cloudfoundry_domain.public.id
  hostname = "fac-${var.cf_space_name}-${var.name}"
  # Yields something like: fac-spacename-name
}

resource "cloudfoundry_user_provided_service" "logshipper_creds" {
  name  = "cg-logshipper-creds"
  space = data.cloudfoundry_space.apps.id
  credentials = {
    "HTTP_USER" = local.username
    "HTTP_PASS" = local.password
  }
  tags = ["logshipper-creds"]
}

resource "cloudfoundry_user_provided_service" "logdrain_service" {
  name             = "fac-logdrain"
  space            = data.cloudfoundry_space.apps.id
  syslog_drain_url = local.syslog_drain
}

resource "random_uuid" "username" {}
resource "random_password" "password" {
  length  = 16
  special = false
}

locals {
  username     = random_uuid.username.result
  password     = random_password.password.result
  syslog_drain = "https://${local.username}:${local.password}@${cloudfoundry_route.logshipper.hostname}.app.cloud.gov/?drain-type=all"
  domain       = cloudfoundry_route.logshipper.endpoint
  app_id       = cloudfoundry_app.cg_logshipper_app.id
  sidecar_json = jsonencode(
    {
      "name" : "fluentbit",
      "command" : "/home/vcap/deps/0/apt/opt/fluent-bit/bin/fluent-bit -Y -c fluentbit.conf",
      "process_types" : ["web"],
    }
  )
}

data "external" "logshipperzip" {
  program     = ["/bin/sh", "prepare-logshipper.sh"]
  working_dir = path.module
  query = {
    gitref = var.gitref
  }
}

resource "cloudfoundry_app" "cg_logshipper_app" {
  name       = var.name
  space      = data.cloudfoundry_space.apps.id
  buildpacks = ["https://github.com/cloudfoundry/apt-buildpack", "nginx_buildpack"]
  path       = "${path.module}/${data.external.logshipperzip.result.path}"
  # source_code_hash  = filesha256("${path.module}/${data.external.logshipperzip.result.path}")
  timeout           = 180
  disk_quota        = var.disk_quota
  memory            = var.logshipper_memory
  instances         = var.logshipper_instances
  strategy          = "rolling"
  health_check_type = "process"

  provisioner "local-exec" {
    command = "cf curl /v3/apps/${self.id}/sidecars  -d '${local.sidecar_json}'"
  }

  service_binding {
    service_instance = var.new_relic_id
  }

  service_binding {
    service_instance = cloudfoundry_user_provided_service.logshipper_creds.id
  }

  service_binding {
    service_instance = module.s3-logshipper-storage.bucket_id
  }

  routes {
    route = cloudfoundry_route.logshipper.id
  }

  environment = {
    PROXYROUTE = var.https_proxy
  }
}
