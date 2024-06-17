resource "newrelic_one_dashboard" "search_dashboard" {
  name = "Search Dashboard (${var.cf_space_name}) - from TF"
  permissions = "public_read_only"

  page {
    name = "Search"

    widget_billboard {
      title = "Searches Per Hour"

      row    = 1
      column = 1
      width  = 3
      height = 3

      nrql_query {
        query = "SELECT count(*) as 'Total', rate(count(*), 1 minute) as 'Per Minute' FROM Transaction where request.uri like '%/dissemination/search%' and request.method = 'POST' and appName = 'gsa-fac-${var.cf_space_name}' since 1 hours AGO COMPARE WITH 1 week ago"
      }
    }

    widget_line {
      title = "Search Traffic"
      
      row = 1
      column = 4
      width = 6
      height = 3

      nrql_query {
          query = "SELECT count(*) FROM Transaction where request.uri like '%/dissemination/search%' and request.method = 'POST' and appName = 'gsa-fac-${var.cf_space_name}' since 4 hours AGO COMPARE WITH 1 week ago TIMESERIES"
      }

      legend_enabled = true

    }

    widget_line {
      title = "Search Response Time"

      row = 2
      column = 1
      width = 6
      height = 3

      nrql_query {
        query = "FROM Metric SELECT average(newrelic.timeslice.value) WHERE appName = 'gsa-fac-${var.cf_space_name}' WITH METRIC_FORMAT 'Custom/search' TIMESERIES SINCE 1 day ago COMPARE WITH 1 week ago"
      }

      legend_enabled = true
    }
  }
}