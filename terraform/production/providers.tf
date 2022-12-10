terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "~>0.50.2"
    }
  }

  backend "s3" {
    bucket  = "cg-2f8babdc-0bd4-4281-b9ab-584a634566b1"
    key     = "terraform.tfstate.production"
    encrypt = "true"
    region  = "us-gov-west-1"
    profile = "fac-terraform-backend"
  }
}

provider "cloudfoundry" {
  api_url      = "https://api.fr.cloud.gov"
  user         = var.cf_user
  password     = var.cf_password
  app_logs_max = 30
}
