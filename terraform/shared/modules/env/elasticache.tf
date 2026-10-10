data "cloudfoundry_service_plan" "elasticache" {
  service_offering_name = "aws-elasticache-redis"
  name                  = "redis-dev"
}

resource "cloudfoundry_service_instance" "elasticache" {
  count        = var.cf_space.name == "dev" ? 1 : 0
  name         = "${var.cf_org_name}-redis"
  space        = var.cf_space.id
  service_plan = data.cloudfoundry_service_plan.elasticache.id
  type         = "managed"

  parameters = jsonencode({
    engine         = "valkey"
    engine_version = "8.2"
  })
}
