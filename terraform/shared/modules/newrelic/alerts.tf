data "newrelic_entity" "gsa-fac" {
  name = "gsa-fac-${var.cf_space_name}"
  type = "APPLICATION"
  domain = "APM" 
}

resource "newrelic_alert_policy" "alert_policy" {
  name = "${var.cf_space_name}-alert-policy"
}

resource "newrelic_notification_destination" "email_destination" {
  account_id = var.new_relic_account_id
  name = "email_destination"
  type = "EMAIL"

  property {
    key = "email"
    value = "daniel.swick@gsa.gov, matthew.jadud@gsa.gov, alexander.steel@gsa.gov"
  }
}

resource "newrelic_notification_channel" "email_channel" {
  account_id = var.new_relic_account_id
  name = "${var.cf_space_name}_email_notification_channel"
  type = "EMAIL"
  product = "IINT"
  destination_id = newrelic_notification_destination.email_destination.id

  property {
    key = "subject"
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
      operator = "EXACTLY_MATCHES"
      values = [newrelic_alert_policy.alert_policy.id]
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
  name = "Infected File Found!"
  enabled = true

  violation_time_limit_seconds = 259200

  nrql {
    query = "SELECT count(*) FROM Log WHERE tags.space_name ='${var.cf_space_name}' and message LIKE '%ScanResult.INFECTED%'"
  }

  critical {
    operator = "above_or_equals"
    threshold = 1
    threshold_duration = 300
    threshold_occurrences = "at_least_once"
  }
  fill_option = "static"
  fill_value = 0
  aggregation_window = 60
  aggregation_method = "event_flow"
  aggregation_delay = 120
}

/*
Alert if the percentage of transactions resulting in an error surpasses a fixed threshold
*/
resource "newrelic_nrql_alert_condition" "error_transactions" {
  account_id = var.new_relic_account_id
  policy_id = newrelic_alert_policy.alert_policy.id
  
  name = "Error Transactions (%)"
  type = "static"

  nrql {
    query = "SELECT percentage(count(*), WHERE error is true) FROM Transaction"
  }

  critical {
    operator = "above"
    threshold = 5
    threshold_duration = 300
    threshold_occurrences = "all"
  }

  warning {
    operator = "above"
    threshold = 3
    threshold_duration = 300
    threshold_occurrences = "all"
  }
  fill_option = "none"
  aggregation_window = 60
  aggregation_method = "event_flow"
  aggregation_delay = 120
}