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
  policy_id      = newrelic_alert_policy.main.id
  name           = "Infected File Found"
  title_template = "${upper(var.cf_space_name)}: {{conditionName}}"
  fill_option    = "static"
  fill_value     = 0
  runbook_url    = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

  nrql {
    query = "SELECT count(*) FROM Log WHERE tags.space_name ='${var.cf_space_name}' AND message LIKE '%ScanResult.INFECTED%'"
  }

  critical {
    operator              = "above_or_equals"
    threshold             = 1
    threshold_duration    = 300
    threshold_occurrences = "at_least_once"
  }
}

resource "newrelic_nrql_alert_condition" "broken_link" {
  count          = var.cf_space_name == "production" ? 1 : 0 // Only deploy to production
  policy_id      = newrelic_alert_policy.main.id
  name           = "Broken Link Detected"
  title_template = "${upper(var.cf_space_name)}: {{conditionName}}"
  runbook_url    = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

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
  name               = "Unusual Error Rate Detected"
  title_template     = "${upper(var.cf_space_name)}: {{conditionName}}"
  type               = "baseline"
  baseline_direction = "upper_and_lower"
  runbook_url        = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

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
  name               = "Unusual Response Time Detected"
  title_template     = "${upper(var.cf_space_name)}: {{conditionName}}"
  type               = "baseline"
  baseline_direction = "upper_and_lower"
  runbook_url        = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

  nrql {
    query = "SELECT average(apm.service.transaction.duration) * 1000 AS 'Response time (ms)' FROM Metric WHERE entity.guid = '${data.newrelic_entity.gsa-fac.guid}'"
  }

  warning {
    operator              = "above"
    threshold             = 3
    threshold_duration    = 300
    threshold_occurrences = "all"
  }
}

resource "newrelic_nrql_alert_condition" "throughput" {
  policy_id          = newrelic_alert_policy.main.id
  name               = "Unusual Request Volume Detected"
  title_template     = "${upper(var.cf_space_name)}: {{conditionName}}"
  type               = "baseline"
  baseline_direction = "upper_and_lower"
  runbook_url        = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

  nrql {
    query = "SELECT rate(count(apm.service.transaction.duration), 1 minute) AS 'Throughput' FROM Metric WHERE entity.guid = '${data.newrelic_entity.gsa-fac.guid}'"
  }

  warning {
    operator              = "above"
    threshold             = 3
    threshold_duration    = 300
    threshold_occurrences = "all"
  }
}

resource "newrelic_nrql_alert_condition" "slow_transactions" {
  policy_id      = newrelic_alert_policy.main.id
  name           = "Transaction Duration Exceeds Threshold"
  title_template = "${upper(var.cf_space_name)}: {{conditionName}}"
  runbook_url    = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

  nrql {
    query = "SELECT count(*) FROM Transaction WHERE appName = 'gsa-fac-${var.cf_space_name}' AND duration > 5 FACET name"
  }

  warning {
    operator              = "above"
    threshold             = 10
    threshold_duration    = 120
    threshold_occurrences = "at_least_once"
  }
}

resource "newrelic_nrql_alert_condition" "synth_uptime_check" {
  policy_id      = newrelic_alert_policy.main.id
  name           = "Ping of application failed"
  title_template = "${upper(var.cf_space_name)}: {{conditionName}}"
  runbook_url    = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

  critical {
    operator              = "above"
    threshold             = 1
    threshold_duration    = 120
    threshold_occurrences = "all"
  }

  nrql {
    query = "SELECT filter(count(*), WHERE result = 'FAILED') AS 'Failures' FROM SyntheticCheck WHERE entityGuid IN ('${data.newrelic_entity.ping.guid}') FACET monitorName"
  }
}

resource "newrelic_nrql_alert_condition" "db_slow_queries" {
  policy_id      = newrelic_alert_policy.main.id
  name           = "DB Statement Duration Exceeds Threshold"
  title_template = "${upper(var.cf_space_name)}: {{conditionName}}"
  runbook_url    = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

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

resource "newrelic_nrql_alert_condition" "transaction_error" {
  policy_id      = newrelic_alert_policy.main.id
  name           = "Transaction Errors Occured"
  title_template = "${upper(var.cf_space_name)}: {{conditionName}}"
  runbook_url    = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

  critical {
    operator              = "above_or_equals"
    threshold             = 5
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  nrql {
    query = "SELECT count(*) FROM TransactionError WHERE (error.message != 'bad role' and appName = 'gsa-fac-${var.cf_space_name}') FACET error.message, request.uri, error.class "
  }
}

resource "newrelic_nrql_alert_condition" "http_500_errors" {
  policy_id      = newrelic_alert_policy.main.id
  name           = "HTTP 500 Errors Detected"
  title_template = "${upper(var.cf_space_name)}: {{conditionName}}"
  runbook_url    = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

  warning {
    operator              = "above"
    threshold             = 5
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  nrql {
    query = "SELECT count(*) FROM Transaction FACET `request.uri` WHERE response.status = '500' and appName = 'gsa-fac-${var.cf_space_name}'"
  }
}

resource "newrelic_nrql_alert_condition" "http_499_errors" {
  policy_id      = newrelic_alert_policy.main.id
  name           = "HTTP 499 Errors Detected"
  title_template = "${upper(var.cf_space_name)}: {{conditionName}}"
  runbook_url    = "https://github.com/GSA-TTS/fac-team/blob/main/troubleshooting/new-relic-queries.md"

  critical {
    operator              = "above_or_equals"
    threshold             = 10
    threshold_duration    = 120
    threshold_occurrences = "all"
  }

  nrql {
    query = "FROM Log SELECT count(*) WHERE tags.space_name ='${var.cf_space_name}' AND (message LIKE '%context canceled%' OR message LIKE '%endpoint_failure%' OR message LIKE '%HTTP/1.1\" 499%')"
  }
}