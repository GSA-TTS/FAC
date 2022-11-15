terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "0.15.0"
    }
  }

  backend "s3" {
    bucket  = "CHANGEME-BUCKET-FROM-BOOTSTRAP"
    key     = "terraform.tfstate.staging"
    encrypt = "true"
    region  = "us-gov-west-1"
    profile = "fac-terraform-backend"
  }
}