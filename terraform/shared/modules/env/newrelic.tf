resource "cloudfoundry_user_provided_service" "credentials" {
  name  = "newrelic-creds"
  space = data.cloudfoundry_space.apps.id
  credentials = {
    "NEW_RELIC_LICENSE_KEY"   = var.new_relic_license_key
    "NEW_RELIC_LOGS_ENDPOINT" = "https://gov-log-api.newrelic.com/log/v1"
  }
  tags = ["newrelic", "logshipper"]
}
