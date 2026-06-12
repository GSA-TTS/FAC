terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry/cloudfoundry"
      version = ">=1.15.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~>4.4.0"
    }
  }
}
