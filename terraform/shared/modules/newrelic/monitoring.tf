locals {
  high_level_page = templatefile("${path.module}/high_level_page.json.tftpl", {
    env                  = var.cf_space_name
    new_relic_account_id = var.new_relic_account_id
    uptime_sla           = { critical = 0.95, warning = 0.99 }   # Uptime Percentage
    transactions_sla     = { critical = 100, warning = 300 }     # Number of Transactions per hour
    success_rate_sla     = { critical = 0.975, warning = 0.985 } # Success Rate Percentage
    latency_sla          = { critical = 1000, warning = 800 }    # Average Latency over a week, in ms
  })

  endpoint_page = templatefile("${path.module}/endpoints.json.tftpl", {
    env                  = var.cf_space_name
    new_relic_account_id = var.new_relic_account_id
    endpoint_config = [
      { name             = "UEI Validation"
        uri              = "/api/sac/ueivalidation"
        transactions_sla = { critical = 1, warning = 5 }         # Number of Transactions per hour
        success_rate_sla = { critical = 0.975, warning = 0.985 } # Success Rate Percentage
        latency_sla      = { critical = 1000, warning = 800 }    # Average Latency over a week, in ms
      },
      { name             = "Submit Audit"
        uri              = "/audit/submission"
        transactions_sla = { critical = 100, warning = 250 }    # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Success Rate Percentage
        latency_sla      = { critical = 500, warning = 450 }    # Average Latency over a week, in ms
      }
    ]
  })
}

locals {
  template_renderer = templatefile("${path.module}/monitoring_dashboard.json.tftpl", {
    env   = var.cf_space_name
    pages = [local.high_level_page, local.endpoint_page]
  })
}

resource "newrelic_one_dashboard_json" "fac_monitoring" {
  json = local.template_renderer
}
