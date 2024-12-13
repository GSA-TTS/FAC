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

    docker = {
      source  = "kreuzwerker/docker"
      version = "~>3.0.2"
    }
  }
}
