locals {
  deployer_service_instance = "${var.name}-deployer"
  deployer_service_key      = "${local.deployer_service_instance}-key"
  deployer_creds            = cloudfoundry_service_key.deployer_creds.credentials
}

data "cloudfoundry_service" "service_account" {
  name = "cloud-gov-service-account"
}

resource "cloudfoundry_service_instance" "space_deployer" {
  name         = local.deployer_service_instance
  space        = cloudfoundry_space.space.id
  service_plan = data.cloudfoundry_service.service_account.service_plans["space-deployer"]
  # We shouldn't attempt to manage service instances before we know that the space
  # permissions allow us to do that.
  depends_on = [
    cloudfoundry_space_users.space_permissions
  ]
}
resource "cloudfoundry_service_key" "deployer_creds" {
  name             = local.deployer_service_key
  service_instance = cloudfoundry_service_instance.space_deployer.id
  # We shouldn't attempt to manage service keys before we know that the space
  # permissions allow us to do that.
  depends_on = [
    cloudfoundry_space_users.space_permissions
  ]
}

# If we need to work with terraform locally, then we can specify
# "var.populate_creds_locally = true" and the meta module will populate the
# deployer credentials needed for working in each environment.
resource "local_sensitive_file" "deployer_creds" {
  count           = var.populate_creds_locally ? 1 : 0
  filename        = "${local.path}/deployer-creds.auto.tfvars"
  file_permission = "0600"
  content         = <<-EOF
  cf_user     = "${local.deployer_creds["username"]}"
  cf_password = "${local.deployer_creds["password"]}"
  EOF
}

# data "github_repository" "repo" {
#   full_name = var.reponame
# }

# resource "github_actions_environment_secret" "cf_username" {
#   count           = var.populate_creds_in_github ? 1 : 0
#   repository      = data.github_repository.repo.name
#   environment     = var.name
#   secret_name     = "CF_USERNAME"
#   plaintext_value = local.deployer_creds["username"]
# }

# resource "github_actions_environment_secret" "cf_password" {
#   count           = var.populate_creds_in_github ? 1 : 0
#   repository      = data.github_repository.repo.name
#   environment     = var.name
#   secret_name     = "CF_PASSWORD"
#   plaintext_value = local.deployer_creds["password"]
# }

