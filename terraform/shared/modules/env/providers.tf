terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "~>0.50.2"
    }

    docker = {
      source = "kreuzwerker/docker"
      version = "~>3.0.2"
    }
  }
}
