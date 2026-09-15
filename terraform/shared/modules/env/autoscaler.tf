data "cloudfoundry_service_plan" "autoscaler" {
  service_offering_name = "app-autoscaler"
  name                  = "autoscaler-free-plan"
}

resource "cloudfoundry_service_instance" "app_autoscaler" {
  name         = "autoscaler"
  space        = var.cf_space.id
  service_plan = data.cloudfoundry_service_plan.autoscaler.id
  type         = "managed"

  parameters = jsonencode({
    instance_min_count = var.autoscale_instance_min
    instance_max_count = var.autoscale_instance_max
    scaling_rules = [
      {
        metric_type          = "memoryused"
        threshold            = 3000 # 3GBs , scale down at 75% usage for instances with 4GB of memory
        operator             = ">="
        adjustment           = "+1"
        breach_duration_secs = 60
        cool_down_secs       = 120
      },
      {
        metric_type          = "memoryused"
        threshold            = 2000 # 2GB , scale down at 50% usage for instances with 4GB of memory
        operator             = "<="
        adjustment           = "-1"
        breach_duration_secs = 300
        cool_down_secs       = 300
      }
    ]
  })
}
