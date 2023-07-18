locals {
  cf_api_url             = "https://api.fr.cloud.gov"
  s3_service_name        = "fac-terraform-state"
  credentials            = jsondecode(cloudfoundry_service_key.bucket_creds.credentials)
  populate_creds_locally = true
}

module "s3" {
  source = "github.com/18f/terraform-cloudgov//s3"

  cf_org_name   = "gsa-tts-oros-fac"
  cf_space_name = "production"
  name          = local.s3_service_name
}

resource "cloudfoundry_service_key" "bucket_creds" {
  name             = "${local.s3_service_name}-access"
  service_instance = module.s3.bucket_id
}

output "bucket_credentials" {
  value     = cloudfoundry_service_key.bucket_creds.credentials
  sensitive = true
}

# Populate Terraform state credentials for use during local development
# Run `init.sh` in any environment directory to configure the backend for that directory
resource "local_file" "backend.tfvars" {
  count           = local.populate_creds_locally ? 1 : 0
  filename        = "${local.path}/../shared/config/backend.tfvars"
  file_permission = "0600"
  content         = <<-EOF
  access_key  = "${local.credentials.access_key_id}"
  secret_key  = "${local.credentials.secret_access_key}"
  bucket      = "${local.credentials.bucket}"
  endpoint    = "${local.credentials.fips_endpoint}"
  region      = "${local.credentials.region}"
  EOF
}
