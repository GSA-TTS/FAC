terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry/cloudfoundry"
      version = ">=1.15.0"
    }
    github = {
      source  = "integrations/github"
      version = "~>5.12.0"
    }
  }
}
