module "sandbox" {
  source = "../shared/modules/sandbox"
  cf_space = {
    id   = data.cloudfoundry_space.space.id
    name = "sandbox"
  }
  pgrst_jwt_secret        = var.pgrst_jwt_secret
  new_relic_license_key   = var.new_relic_license_key
  django_secret_login_key = var.django_secret_login_key
  sam_api_key             = var.sam_api_key
  login_client_id         = var.login_client_id
  login_secret_key        = var.login_secret_key
  branch_name             = var.branch_name
  backups_s3_id           = module.sandbox-backups-bucket.bucket_id

  database_plan         = "medium-gp-psql"
  https_proxy_instances = 1
  json_params = jsonencode(
    {
      "storage" : 50,
    }
  )
}

module "sandbox-backups-bucket" {
  source = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v2.3.0"

  cf_space_id  = data.cloudfoundry_space.space.id
  name         = "backups"
  s3_plan_name = "basic"
  tags         = ["s3"]
}

# Stuff used for apps in this space
data "cloudfoundry_org" "org" {
  name = var.cf_org_name
}

data "cloudfoundry_space" "space" {
  name = "sandbox"
  org  = data.cloudfoundry_org.org.id
}
