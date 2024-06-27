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

    widget_line {
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

    widget_line {
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

    widget_line {
      title = "Global Requests (Non-Upload)"

      row    = 2
      column = 1
      width  = 3
      height = 3

      nrql_query {
        query = "FROM Metric SELECT count(*) AS 'Total requests', average(apm.service.transaction.duration) * 1000 AS 'Average time (ms)' WHERE appName = 'gsa-fac-${var.cf_space_name}' AND path NOT LIKE '%ExcelFileHandlerView.post' AND path NOT LIKE '%UploadReportView.post'"
      }

      legend_enabled = true
    }

    widget_line {
      title = "500 Error Code"

      row    = 3
      column = 1
      width  = 9
      height = 3

      nrql_query {
        query = "SELECT count(*) FROM Transaction FACET `request.uri` WHERE response.status = '500' and appName = 'gsa-fac-${var.cf_space_name}' SINCE 1 week AGO TIMESERIES"
      }

      legend_enabled = true
    }
  }
}
