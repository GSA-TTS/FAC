resource "cloudfoundry_user_provided_service" "credentials" {
  name  = "newrelic-creds"
  space = data.cloudfoundry_space.apps.id
  credentials = {
    "NEW_RELIC_LICENSE_KEY" = var.new_relic_license_key
  }
}