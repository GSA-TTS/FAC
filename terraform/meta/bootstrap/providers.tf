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
}

provider "cloudfoundry" {
  api_url      = local.cf_api_url
  user         = var.cf_user
  password     = var.cf_password
  app_logs_max = 30
}

provider "cloudfoundry-community" {
  api_url  = "https://api.fr.cloud.gov"
  user     = var.cf_user
  password = var.cf_password
}
