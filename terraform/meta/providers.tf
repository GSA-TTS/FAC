terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry/cloudfoundry"
      version = "1.1.0"
    }
    cloudfoundry-community = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "~>0.53.1"
    }
  }

  backend "s3" {
    # We are using "partial configuration" here. The rest of the backend
    # parameters are provided when you initialize terraform, eg run:
    #
    #   terraform init \
    #    --backend-config=../shared/config/backend.tfvars \
    #    --backend-config=key=terraform-state-$(basename $(pwd))
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

# Backwards compatability provider
# https://github.com/GSA-TTS/terraform-cloudgov/blob/main/UPGRADING.md#using-v1-and-v2-together
provider "cloudfoundry-community" {
  api_url  = "https://api.fr.cloud.gov"
  user     = var.cf_user
  password = var.cf_password
}
