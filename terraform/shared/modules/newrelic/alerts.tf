# data "newrelic_entity" "gsa-fac" {
#   name   = "gsa-fac-${var.cf_space_name}"
#   type   = "APPLICATION"
#   domain = "APM"
# }

resource "newrelic_alert_policy" "alert_policy" {
  name = "${var.cf_space_name}-alert-policy"
}

resource "newrelic_notification_destination" "email_destination" {
  account_id = var.new_relic_account_id
  name       = "email_destination"
  type       = "EMAIL"

  property {
    key   = "email"
    value = "bret.mogilefsky@gsa.gov"
  }
}

resource "newrelic_notification_channel" "email_channel" {
  account_id     = var.new_relic_account_id
  name           = "${var.cf_space_name}_email_notification_channel"
  type           = "EMAIL"
  product        = "IINT"
  destination_id = newrelic_notification_destination.email_destination.id

  property {
    key   = "subject"
    value = "{{issueTitle}}"
  }
}

resource "newrelic_workflow" "alert_workflow" {
  name = "${var.cf_space_name}_alert_workflow"

  muting_rules_handling = "DONT_NOTIFY_FULLY_MUTED_ISSUES"

  issues_filter {
    name = "filter"
    type = "FILTER"

    predicate {
      attribute = "labels.policyIds"
      operator  = "EXACTLY_MATCHES"
      values    = [newrelic_alert_policy.alert_policy.id]
    }
  }

  destination {
    channel_id = newrelic_notification_channel.email_channel.id
  }
}

/*
Alert if a log entry indicates that the fac-file-scanner found an infected file
*/
resource "newrelic_nrql_alert_condition" "infected_file_found" {
  policy_id = newrelic_alert_policy.alert_policy.id
  name      = "Infected File Found!"
  enabled   = true

  violation_time_limit_seconds = 259200

  nrql {
    query = "SELECT count(*) FROM Log WHERE tags.space_name ='${var.cf_space_name}' and message LIKE '%ScanResult.INFECTED%'"
  }

  critical {
    operator              = "above_or_equals"
    threshold             = 1
    threshold_duration    = 300
    threshold_occurrences = "at_least_once"
  }
  fill_option        = "static"
  fill_value         = 0
  aggregation_window = 60
  aggregation_method = "event_flow"
  aggregation_delay  = 120
}

/*
Alert if the percentage of transactions resulting in an error surpasses a fixed threshold
*/
resource "newrelic_nrql_alert_condition" "error_transactions" {
  account_id = var.new_relic_account_id
  policy_id  = newrelic_alert_policy.alert_policy.id

  name = "Error Transactions (%)"
  type = "static"

  nrql {
    query = "SELECT percentage(count(*), WHERE error is true) FROM Transaction"
  }

  critical {
    operator              = "above"
    threshold             = 5
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  warning {
    operator              = "above"
    threshold             = 3
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  fill_option        = "none"
  aggregation_window = 60
  aggregation_method = "event_flow"
  aggregation_delay  = 120
}

# --------------------------------------------------------------

data "newrelic_entity" "gsa-fac" {
  name = "gsa-fac-${var.cf_space_name}"
}

data "newrelic_entity" "link_crawler" {
  count  = var.cf_space_name == "preview" ? 0 : 1                                                                    // This resource does not exist for preview
  name   = var.cf_space_name == "production" ? "FAC Link Crawler (prod)" : "FAC Link Crawler (${var.cf_space_name})" // Production environment uses abbreviated "prod" in monitor name
  type   = "MONITOR"
  domain = "SYNTH"
}

data "newrelic_entity" "ping" {
  name   = var.cf_space_name == "preview" ? "FAC Ping ${title(var.cf_space_name)}" : "Fac Ping ${title(var.cf_space_name)}" // To account for naming convention differences
  type   = "MONITOR"
  domain = "SYNTH"
}

resource "newrelic_alert_policy" "main" {
  name                = title("${var.cf_space_name} Alerts")
  incident_preference = "PER_CONDITION"
}

resource "newrelic_nrql_alert_condition" "infected_file" {
  policy_id   = newrelic_alert_policy.main.id
  name        = "Infected File Found!"
  enabled     = true
  fill_option = "static"

  nrql {
    query = "SELECT count(*) FROM Log WHERE tags.space_name ='${var.cf_space_name}' and message LIKE '%ScanResult.INFECTED%'"
  }

  critical {
    operator              = "above_or_equals"
    threshold             = 1
    threshold_duration    = 300
    threshold_occurrences = "at_least_once"
  }
}

resource "newrelic_nrql_alert_condition" "broken_link" {
  count     = var.cf_space_name == "production" ? 1 : 0 // Only deploy to production
  policy_id = newrelic_alert_policy.main.id
  name      = "Broken Link Detected on app.fac.gov"

  critical {
    operator              = "above"
    threshold             = 1
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  nrql {
    query = "SELECT filter(count(*), WHERE result = 'FAILED') AS 'Failures' FROM SyntheticCheck WHERE entityGuid IN ('${data.newrelic_entity.link_crawler[0].guid}') FACET monitorName"
  }
}

resource "newrelic_nrql_alert_condition" "error_rate" {
  policy_id          = newrelic_alert_policy.main.id
  name               = "gsa-fac-${var.cf_space_name} - Error rate"
  type               = "baseline"
  baseline_direction = "upper_and_lower"

  critical {
    operator              = "above"
    threshold             = 10
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  nrql {
    query = "SELECT (count(apm.service.error.count) / count(apm.service.transaction.duration)) * 100 AS 'Error %' FROM Metric WHERE entity.guid = '${data.newrelic_entity.gsa-fac.guid}'"
  }
}

resource "newrelic_nrql_alert_condition" "response_time" {
  policy_id          = newrelic_alert_policy.main.id
  name               = "gsa-fac-${var.cf_space_name} - Response time (ms)"
  enabled            = false
  type               = "baseline"
  baseline_direction = "upper_and_lower"

  nrql {
    query = "SELECT average(apm.service.transaction.duration) * 1000 AS 'Response time (ms)' FROM Metric WHERE entity.guid = '${data.newrelic_entity.gsa-fac.guid}'"
  }

  warning {
    disable_health_status_reporting = false
    operator                        = "above"
    threshold                       = 3
    threshold_duration              = 300
    threshold_occurrences           = "all"
  }
}

resource "newrelic_nrql_alert_condition" "throughput" {
  policy_id          = newrelic_alert_policy.main.id
  name               = "gsa-fac-${var.cf_space_name} - Throughput"
  enabled            = false
  type               = "baseline"
  baseline_direction = "upper_and_lower"

  nrql {
    query = "SELECT rate(count(apm.service.transaction.duration), 1 minute) AS 'Throughput' FROM Metric WHERE entity.guid = '${data.newrelic_entity.gsa-fac.guid}'"
  }

  warning {
    disable_health_status_reporting = false
    operator                        = "above"
    threshold                       = 3
    threshold_duration              = 300
    threshold_occurrences           = "all"
  }
}

resource "newrelic_nrql_alert_condition" "long_running_web_fn" {
  policy_id = newrelic_alert_policy.main.id
  name      = "Long Running Web Function ( > 200ms)"
  enabled   = false

  critical {
    operator              = "above"
    threshold             = 20
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }

  nrql {
    query = "SELECT count(*) FROM Transaction  WHERE appName = 'gsa-fac-${var.cf_space_name}' EXTRAPOLATE FACET name where name not like 'WebTransaction/Function/api.views:Sprite.get'"
  }
}

resource "newrelic_nrql_alert_condition" "synth_uptime_check" {
  policy_id = newrelic_alert_policy.main.id
  name      = "Ping of app.fac.gov failed"
  enabled   = true

  critical {
    operator              = "above"
    threshold             = 1
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  nrql {
    query = "SELECT filter(count(*), WHERE result = 'FAILED') AS 'Failures' FROM SyntheticCheck WHERE entityGuid IN ('${data.newrelic_entity.ping.guid}') FACET monitorName"
  }
}

resource "newrelic_nrql_alert_condition" "db_slow_queries" {
  policy_id = newrelic_alert_policy.main.id
  name      = "Production DB Statement Duration"
  enabled   = false

  critical {
    operator              = "above"
    threshold             = 150
    threshold_duration    = 120
    threshold_occurrences = "all"
  }

  nrql {
    query = "SELECT average(`duration.ms`) FROM Span FACET `db.statement` WHERE entity.name ='gsa-fac-${var.cf_space_name}'"
  }

}

resource "newrelic_nrql_alert_condition" "http_500_errors" {
  policy_id = newrelic_alert_policy.main.id
  name      = "Production Request Received a 500 Status"

  critical {
    operator              = "above"
    threshold             = 0
    threshold_duration    = 60
    threshold_occurrences = "all"
  }

  nrql {
    query = "SELECT count(*) FROM Transaction FACET `request.uri` WHERE response.status = '500' and appName = 'gsa-fac-${var.cf_space_name}'"
  }
}

resource "newrelic_nrql_alert_condition" "slow_transactions" {
  policy_id = newrelic_alert_policy.main.id
  name      = "Slow Transactions"
  enabled   = false

  nrql {
    query = "SELECT count(*) from Transaction where appName = 'gsa-fac-${var.cf_space_name}' facet name"
  }

  warning {
    operator              = "above"
    threshold             = 15
    threshold_duration    = 300
    threshold_occurrences = "all"
  }
}

resource "newrelic_nrql_alert_condition" "transaction_error" {
  policy_id = newrelic_alert_policy.main.id
  name      = "Transaction Error Occured"

  critical {
    operator              = "above_or_equals"
    threshold             = 1
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }

  nrql {
    query = "select count(*) from TransactionError where (error.message != 'bad role' and appName = 'gsa-fac-${var.cf_space_name}') FACET error.message, request.uri, error.class "
  }
}