locals {
  dev       = var.cf_space_name == "dev" ? "fac-dev.app.cloud.gov" : ""
  preview   = var.cf_space_name == "preview" ? "fac-preview.app.cloud.gov" : ""
  staging   = var.cf_space_name == "staging" ? "fac-staging.app.cloud.gov" : ""
  prod      = var.cf_space_name == "production" ? "app.fac.gov" : ""
  admin_uri = coalesce(local.dev, local.preview, local.staging, local.prod)
}

resource "newrelic_one_dashboard" "log_review_dashboard" {
  name        = "FAC Log Review (${var.cf_space_name})"
  permissions = "public_read_only"

  page {
    name = "FAC Log Review"

    widget_billboard {
      title = "Submission Count"

      row    = 1
      column = 1
      width  = 3
      height = 3

      nrql_query {
        query = "From Transaction SELECT count(*) as 'Submissions' WHERE appName = 'gsa-fac-${var.cf_space_name}' and request.method = 'POST' and request.uri like '/audit/submission/%' since 1 week ago"
      }
    }

    widget_billboard {
      title = "Excel Uploads"


      row    = 1
      column = 4
      width  = 3
      height = 3

      nrql_query {
        query = "FROM Metric SELECT count(*) AS 'Total uploads', average(apm.service.transaction.duration) AS 'Average time (s)' WHERE appName = 'gsa-fac-${var.cf_space_name}' AND path LIKE 'audit.views.views:ExcelFileHandlerView.post'"
      }

      legend_enabled = true

    }

    widget_billboard {
      title = "Single Audit Report Uploads"

      row    = 1
      column = 7
      width  = 3
      height = 3

      nrql_query {
        query = "FROM Metric SELECT count(*) AS 'Total uploads', average(apm.service.transaction.duration) AS 'Average time (s)' WHERE appName = 'gsa-fac-${var.cf_space_name}' AND path LIKE 'audit.views.upload_report_view:UploadReportView.post'"
      }

      legend_enabled = true
    }

    widget_billboard {
      title = "Global Requests (Non-Upload)"

      row    = 1
      column = 10
      width  = 3
      height = 3

      nrql_query {
        query = "FROM Metric SELECT count(*) AS 'Total requests', average(apm.service.transaction.duration) * 1000 AS 'Average time (ms)' WHERE appName = 'gsa-fac-${var.cf_space_name}' AND path NOT LIKE '%ExcelFileHandlerView.post' AND path NOT LIKE '%UploadReportView.post'"
      }

      legend_enabled = true
    }

    widget_stacked_bar {
      title = "500 Error Code"

      row    = 3
      column = 1
      width  = 12
      height = 4

      nrql_query {
        query = "SELECT count(*) FROM Transaction FACET `request.uri` WHERE response.status = '500' and appName = 'gsa-fac-${var.cf_space_name}' SINCE 1 week AGO TIMESERIES"
      }

      legend_enabled = true
    }

    widget_stacked_bar {
      title = "Login Requests"

      row    = 4
      column = 1
      width  = 8
      height = 3

      nrql_query {
        query = "SELECT count(*) FROM Transaction FACET `request.uri` WHERE request.uri = '/openid/login/' and appName = 'gsa-fac-${var.cf_space_name}' SINCE 1 week AGO TIMESERIES"
      }

      colors {
        color = "#00ff04"
        series_overrides {
          color       = "#00ff04"
          series_name = "/openid/login/"
        }
      }

      legend_enabled = true
    }

    widget_stacked_bar {
      title = "Logout Requests"

      row    = 5
      column = 1
      width  = 8
      height = 3

      nrql_query {
        query = "SELECT count(*) FROM Transaction FACET `request.uri` WHERE request.uri = '/openid/logout/' and appName = 'gsa-fac-${var.cf_space_name}' SINCE 1 week AGO TIMESERIES"
      }
      colors {
        color = "#ff0000"
        series_overrides {
          color       = "#ff0000"
          series_name = "/openid/logout/"
        }
      }

      legend_enabled = true
    }

    widget_billboard {
      title = "Infected Files Detected"

      row    = 4
      column = 9
      width  = 3
      height = 3

      nrql_query {
        query = "SELECT count(*) AS 'Infected Files' FROM Log WHERE tags.space_name = '${var.cf_space_name}' and message LIKE '%ScanResult.INFECTED%'"
      }

      legend_enabled = true
    }

    widget_billboard {
      title = "Django /admin/login/ Count"

      row    = 5
      column = 9
      width  = 3
      height = 3

      nrql_query {
        query = "SELECT count(`message` as `/admin/login/ hits`) FROM Log WHERE `message` LIKE '${local.admin_uri}%/admin/login%' SINCE 7 days ago"
      }

      legend_enabled = true
    }

    widget_log_table {
      title = "${var.cf_space_name} api.sam.gov Connections"

      row    = 6
      column = 1
      width  = 8
      height = 3

      nrql_query {
        query = "SELECT `message` FROM Log WHERE `entity.name` = 'gsa-fac-${var.cf_space_name}' AND allColumnSearch('api.sam.gov', insensitive: true) SINCE 7 DAYS AGO"
      }

      legend_enabled = true
    }

    widget_billboard {
      title = "${var.cf_space_name} api.sam.gov Connection Count"

      row    = 6
      column = 9
      width  = 3
      height = 3

      nrql_query {
        query = "SELECT count(*) AS 'api.sam.gov connections' FROM Log WHERE `entity.name` = 'gsa-fac-${var.cf_space_name}' AND allColumnSearch('api.sam.gov', insensitive: true) SINCE 7 DAYS AGO"
      }

      legend_enabled = true
    }

    widget_log_table {
      title = "${var.cf_space_name} login.gov Connections"

      row    = 7
      column = 1
      width  = 8
      height = 3

      nrql_query {
        query = "SELECT `message` FROM Log WHERE `entity.name` = 'gsa-fac-${var.cf_space_name}' AND allColumnSearch('/api/openid_connect/userinfo', insensitive: true) SINCE 7 DAYS AGO"
      }

      legend_enabled = true
    }

    widget_billboard {
      title = "${var.cf_space_name} login.gov Connection Count"

      row    = 7
      column = 9
      width  = 3
      height = 3

      nrql_query {
        query = "SELECT count(*) AS 'login.gov connections' FROM Log WHERE `entity.name` = 'gsa-fac-${var.cf_space_name}' AND allColumnSearch('/api/openid_connect/userinfo', insensitive: true) SINCE 7 DAYS AGO"
      }

      legend_enabled = true
    }

    widget_log_table {
      title = "${var.cf_space_name} Check Tables Logs"

      row    = 8
      column = 1
      width  = 8
      height = 3

      nrql_query {
        query = "SELECT `message` FROM Log WHERE `tags.space_name` = '${var.cf_space_name}' AND allColumnSearch('CHECKTABLESPASS', insensitive: true) SINCE 7 days ago"
      }

      legend_enabled = true
    }

    widget_billboard {
      title = "${var.cf_space_name} Table Check Count - Pass"

      row    = 8
      column = 9
      width  = 3
      height = 3

      nrql_query {
        query = "SELECT count(*) FROM Log WHERE `tags.space_name` = '${var.cf_space_name}' AND allColumnSearch('CHECKTABLESPASS', insensitive: true) SINCE 7 days ago"
      }

      legend_enabled = true
    }

    widget_log_table {
      title = "${var.cf_space_name} Missing Tables Logs"

      row    = 9
      column = 1
      width  = 8
      height = 3

      nrql_query {
        query = "SELECT `message` FROM Log WHERE `tags.space_name` = '${var.cf_space_name}' AND allColumnSearch('DBMISSINGTABLES', insensitive: true) SINCE 7 days ago"
      }

      legend_enabled = true
    }

    widget_billboard {
      title = "${var.cf_space_name} Table Check Count - Fail"

      row    = 9
      column = 9
      width  = 3
      height = 3

      nrql_query {
        query = "SELECT count(*) FROM Log WHERE `tags.space_name` = '${var.cf_space_name}' AND allColumnSearch('DBMISSINGTABLES', insensitive: true) SINCE 7 days ago"
      }

      legend_enabled = true
    }

    widget_log_table {
      title = "${var.cf_space_name} Submissions within the past 2 hours"

      row    = 10
      column = 1
      width  = 8
      height = 3

      nrql_query {
        query = "SELECT `message` FROM Log WHERE allColumnSearch('POST', insensitive: true) AND allColumnSearch('/submission/', insensitive: true) AND `newrelic.source` = 'logs.APM' AND `entity.name` = 'gsa-fac-${var.cf_space_name}' SINCE 2 hours ago"
      }
      legend_enabled = true
    }
    widget_log_table {
      title = "${var.cf_space_name} Backups within the past 2 hours"

      row    = 10
      column = 9
      width  = 3
      height = 3

      nrql_query {
        query = "SELECT `timestamp`,`message` FROM Log WHERE allColumnSearch('STARTUP_CHECK', insensitive: true) AND `message` LIKE '%db_to_s3%' AND `message` LIKE '%PASS%' AND `tags.space_name` = '${var.cf_space_name}' SINCE 2 hours ago"
      }
      legend_enabled = true
    }

    widget_log_table {
      title = "${var.cf_space_name} Row Count within the past 2 hours"

      row    = 11
      column = 1
      width  = 8
      height = 3

      nrql_query {
        query = "SELECT `message` FROM Log WHERE `tags.space_name` = '${var.cf_space_name}' AND allColumnSearch('\"TABLEROWCOUNT\"', insensitive: true) SINCE 2 hours ago"
      }
      legend_enabled = true
    }
    widget_table {
      title = "${var.cf_space_name} Row Count"

      row    = 12
      column = 1
      width  = 8
      height = 3

      nrql_query {
        query = "SELECT `message` FROM Log WHERE `tags.space_name` = '${var.cf_space_name}' AND allColumnSearch('\"TABLEROWCOUNT\"', insensitive: true) SINCE 7 days ago"
      }

      legend_enabled = true
    }
  }
}
