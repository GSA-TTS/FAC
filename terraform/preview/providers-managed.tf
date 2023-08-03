# The content of this file is managed by Terraform. If you modify it, it may
# be reverted the next time Terraform runs. If you want to make changes, do it
# in ../meta/bootstrap-env/templates.

terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "~>0.50.2"
    }
  }

  backend "s3" {
    # The rest of the backend parameters must be supplied when you initialize:
    #   terraform init --backend-config=../shared/config/backend.tfvars \
    #    --backend-config=key=terraform.tfstate.$(basename $(pwd))
    #
    # For more info, see:
    # https://developer.hashicorp.com/terraform/language/settings/backends/configuration#partial-configuration
    encrypt = "true"
  }
}

provider "cloudfoundry" {
  api_url  = "https://api.fr.cloud.gov"
  user     = var.cf_user
  password = var.cf_password
}