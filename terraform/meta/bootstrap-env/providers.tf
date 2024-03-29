terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "~>0.51.3"
    }
    github = {
      source  = "integrations/github"
      version = "~>5.12.0"
    }
  }
}