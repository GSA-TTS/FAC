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
        method           = "POST"
        transactions_sla = { critical = 1, warning = 5 }         # Number of Transactions per hour
        success_rate_sla = { critical = 0.975, warning = 0.985 } # Success Rate Percentage
        latency_sla      = { critical = 1000, warning = 800 }    # Average Latency over a week, in ms
      },
      { name             = "Submit Audit"
        uri              = "/audit/submission/%" # '/audit/submission%' was also catching '/audit/submission-progress'
        method           = "POST"
        transactions_sla = { critical = 5, warning = 8 }        # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Success Rate Percentage
        latency_sla      = { critical = 1500, warning = 1200 }  # Average Latency over a week, in ms
      },
      { name             = "Homepage"
        uri              = "/"
        method           = "GET"
        transactions_sla = { critical = 100, warning = 150 }    # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Success Rate Percentage
        latency_sla      = { critical = 350, warning = 250 }    # Average Latency over a week, in ms
      },
      { name             = "Audit Submissions Homepage"
        uri              = "/audit/"
        method           = "GET"
        transactions_sla = { critical = 50, warning = 70 }      # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Success Rate Percentage
        latency_sla      = { critical = 1500, warning = 1200 }  # Average Latency over a week, in ms
      },
      { name             = "All Excel Uploads"
        uri              = "/audit/excel/%"
        method           = "POST"
        transactions_sla = { critical = 20, warning = 25 }       # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 }  # Success Rate Percentage
        latency_sla      = { critical = 12000, warning = 10000 } # Average Latency over a week, in ms
      },
      { name             = "PDF Uploads"
        uri              = "/audit/upload-report/%"
        method           = "POST"
        transactions_sla = { critical = 10, warning = 20 }       # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 }  # Success Rate Percentage
        latency_sla      = { critical = 15000, warning = 12000 } # Average Latency over a week, in ms
      },
      { name             = "Cross Validation"
        uri              = "/audit/cross-validation/%"
        method           = "POST"
        transactions_sla = { critical = 8, warning = 10 }       # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Success Rate Percentage
        latency_sla      = { critical = 800, warning = 650 }    # Average Latency over a week, in ms
      },
      { name             = "Single Summary Report Download"
        uri              = "/dissemination/summary-report/xlsx%"
        method           = "GET"
        transactions_sla = { critical = 70, warning = 80 }      # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Success Rate Percentage
        latency_sla      = { critical = 800, warning = 700 }    # Average Latency over a week, in ms
      },
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
