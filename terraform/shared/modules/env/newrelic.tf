resource "cloudfoundry_service_instance" "newrelic_creds" {
  name        = "newrelic-creds"
  type        = "user-provided"
  tags        = ["newrelic-creds"]
  space       = var.cf_space.id
  credentials = <<NRCREDS
  {
    "NEW_RELIC_LICENSE_KEY": "${var.new_relic_license_key}",
    "NEW_RELIC_LOGS_ENDPOINT": "https://gov-log-api.newrelic.com/log/v1"
  }
  NRCREDS
}

module "newrelic" {
  source               = "../newrelic"
  cf_space_name        = var.cf_space.name
  new_relic_account_id = var.new_relic_account_id
  new_relic_api_key    = var.new_relic_api_key
}
