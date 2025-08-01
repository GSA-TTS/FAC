### Description
The application module is responsible for pulling the latest code from a given branch, compiling the static files and then deploying a running application to the sandbox environment. This differs slightly from other environments in the fact that we process an application deployment with the manifests through github. Sandbox however, was the benchmark to determine if it was feasible to deploy the application through terraform and as such, does exactly that when working in the immutable environment, sandbox.

### Usage
```terraform
module "fac-app" {
  source                  = "../path/to/source"
  gitref                  = "refs/heads/${var.branch_name}"
  cf_org_name             = var.cf_org_name
  cf_space_name           = var.cf_space.name
  name                    = local.app_name
  app_memory              = "#M"
  disk_quota              = "#M"
  app_instances           = #
  django_secret_login_key = var.django_secret_login_key
  sam_api_key             = var.sam_api_key
  login_client_id         = var.login_client_id
  login_secret_key        = var.login_secret_key
  environment_variables = {
    ENV                   = "SANDBOX"
    DISABLE_COLLECTSTATIC = 1
    DJANGO_BASE_URL       = "https://fac-${var.cf_space.name}.app.cloud.gov"
    AV_SCAN_URL           = "https://fac-av-${var.cf_space.name}.apps.internal:61443/scan"
    ALLOWED_HOSTS         = "fac-${var.cf_space.name}.app.cloud.gov"
  }
  service_bindings = {
    "${module.s3-private.bucket_name}"                        = ""
    "${module.s3-public.bucket_name}"                         = ""
    "${module.database.database_name}"                        = ""
    "${module.snapshot-database.database_name}"               = ""
    "${cloudfoundry_service_instance.newrelic_creds.name}"    = ""
    "${cloudfoundry_service_instance.proxy_credentials.name}" = ""
    "${module.logshipper.syslog_drain_name}"                  = ""
  }
  depends_on = [cloudfoundry_service_instance.newrelic_creds, module.https-proxy, module.logshipper]
}
```
