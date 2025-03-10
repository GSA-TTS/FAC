locals {
  high_level_page = templatefile("${path.module}/high_level_page.json.tftpl", {
    env                  = var.cf_space_name
    new_relic_account_id = var.new_relic_account_id
    uptime_sla           = { critical = 0.95, warning = 0.99 }   # Uptime Percentage
    transactions_sla     = { critical = 100, warning = 300 }     # Number of Transactions per hour
    success_rate_sla     = { critical = 0.975, warning = 0.985 } # Success Rate Percentage
    latency_sla          = { critical = 1000, warning = 800 }    # Average Latency over a week, in ms
  })

  healthcheck_pages = templatefile("${path.module}/widgets.json.tftpl", {
    env                  = var.cf_space_name
    new_relic_account_id = var.new_relic_account_id
    page_name            = "Healthcheck"
    widgets_config = [
      { name             = "UEI Validation"
        uri              = "/api/sac/ueivalidation"
        method           = "POST"
        transactions_sla = { critical = 1, warning = 5 }         # Number of Transactions per hour
        success_rate_sla = { critical = 0.975, warning = 0.985 } # Success Rate Percentage
        latency_sla      = { critical = 1000, warning = 800 }    # Average Latency over a week, in ms
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
    ]
  })

  file_uploads = templatefile("${path.module}/widgets.json.tftpl", {
    env                  = var.cf_space_name
    new_relic_account_id = var.new_relic_account_id
    page_name            = "File Uploads"
    widgets_config = [
      { name             = "Workbook Uploads"
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
    ]
  })

  file_downloads = templatefile("${path.module}/widgets.json.tftpl", {
    env                  = var.cf_space_name
    new_relic_account_id = var.new_relic_account_id
    page_name            = "File Downloads"
    widgets_config = [
      { name             = "Single Summary Report Download"
        uri              = "/dissemination/summary-report/xlsx%"
        method           = "GET"
        transactions_sla = { critical = 70, warning = 80 }      # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Success Rate Percentage
        latency_sla      = { critical = 800, warning = 700 }    # Average Latency over a week, in ms
      },
      { name             = "Workbook Downloads"
        uri              = "/audit/excel/%"
        method           = "GET"
        transactions_sla = { critical = 20, warning = 25 }       # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 }  # Success Rate Percentage
        latency_sla      = { critical = 12000, warning = 10000 } # Average Latency over a week, in ms
      },
    ]
  })

  submission_pages = templatefile("${path.module}/widgets.json.tftpl", {
    env                  = var.cf_space_name
    new_relic_account_id = var.new_relic_account_id
    page_name            = "Validation and Submission"
    widgets_config = [
      { name             = "Cross Validation"
        uri              = "/audit/cross-validation/%"
        method           = "POST"
        transactions_sla = { critical = 8, warning = 10 }       # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Success Rate Percentage
        latency_sla      = { critical = 800, warning = 650 }    # Average Latency over a week, in ms
      },
      { name             = "Unlock After Certification"
        uri              = "/audit/unlock-after-certification/%"
        method           = "POST"
        transactions_sla = { critical = 3, warning = 5 }        # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Success Rate Percentage
        latency_sla      = { critical = 800, warning = 650 }    # Average Latency over a week, in ms
      },
      { name             = "Submit Audit"
        uri              = "/audit/submission/%" # '/audit/submission%' was also catching '/audit/submission-progress'
        method           = "POST"
        transactions_sla = { critical = 5, warning = 8 }        # Number of Transactions per hour
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Success Rate Percentage
        latency_sla      = { critical = 1500, warning = 1200 }  # Average Latency over a week, in ms
      }
    ]
  })

  # Management pages use the simplified "management_widgets.json.tftpl" due to their lower traffic.
  management_pages = templatefile("${path.module}/management_widgets.json.tftpl", {
    env                  = var.cf_space_name
    new_relic_account_id = var.new_relic_account_id
    page_name            = "Audit Management"
    managment_uri        = "/audit/manage-submission%"
    latency_sla          = { critical = 800, warning = 650 } # Target average latency over two weeks, in ms
    widgets_config = [
      { name             = "Remove In Progress Submission"
        uri              = "/audit/manage-submission/remove-report/%"
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Target Success Rate Percentages
      },
      { name             = "Audit Management Homepage"
        uri              = "/audit/manage-submission/20%"
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Target Success Rate Percentages
      },
      { name             = "Change Auditor Certifying Official"
        uri              = "/audit/manage-submission/auditor-certifying-official/%"
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Target Success Rate Percentages
      },
      { name             = "Change Auditee Certifying Official"
        uri              = "/audit/manage-submission/auditee-certifying-official/%"
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Target Success Rate Percentages
      },
      { name             = "Add Editor"
        uri              = "/audit/manage-submission/add-editor/%"
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Target Success Rate Percentages
      },
      { name             = "Remove Editor"
        uri              = "/audit/manage-submission/remove-editor/%"
        success_rate_sla = { critical = 0.99, warning = 0.995 } # Target Success Rate Percentages
      },
    ]
  })
}

locals {
  template_renderer = templatefile("${path.module}/monitoring_dashboard.json.tftpl", {
    env   = var.cf_space_name
    pages = [local.high_level_page, local.healthcheck_pages, local.file_uploads, local.file_downloads, local.submission_pages, local.management_pages]
  })
}

resource "newrelic_one_dashboard_json" "fac_monitoring" {
  json = local.template_renderer
}
