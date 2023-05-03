locals {
  swagger_name = "swagger"
}

resource "cloudfoundry_route" "swagger" {
  space    = data.cloudfoundry_space.apps.id
  domain   = data.cloudfoundry_domain.public.id
  hostname = "fac-${var.cf_space_name}-${local.swagger_name}"
}

resource "cloudfoundry_app" "swagger" {
  name              = local.swagger_name
  space             = data.cloudfoundry_space.apps.id
  docker_image      = "swaggerapi/swagger-ui"
  health_check_type = "process"
  timeout           = 20
  memory            = 256
  disk_quota        = 256
  instances         = var.swagger_instances
  strategy          = "blue-green"
  routes {
    route = cloudfoundry_route.swagger.id
  }
  environment = {
    API_URL : "https://${cloudfoundry_route.postgrest.endpoint}"
    SWAGGER_JSON_URL : "https://${cloudfoundry_route.postgrest.endpoint}"
  }
}

