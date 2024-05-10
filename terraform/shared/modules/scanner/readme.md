### Description
A small, lightweight app using a `python_buildpack` to deploy a `flask` application in the environment, for the purpose of long running scans.

### Usage
```terraform
module "fac-file-scanner" {
  source            = "../path/to/source"
  name              = local.scanner_name
  cf_org_name       = var.cf_org_name
  cf_space_name     = var.cf_space_name
  https_proxy       = module.https-proxy.https_proxy
  s3_id             = module.s3-private.bucket_id
  logdrain_id       = module.cg-logshipper.logdrain_service_id
  scanner_instances = #
  scanner_memory    = #
  disk_quota        = #
}

resource "cloudfoundry_network_policy" "scanner-network-policy" {
  policy {
    source_app      = module.fac-file-scanner.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}
```
