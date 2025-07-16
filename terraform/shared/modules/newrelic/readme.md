### Description
The new relic module is responsible for handling reporting and metrics within the app, predominately for alerting, dashboards and log review purposes. There are two files that are responsible for the bulk of the new relic reporting.

1. [Log Review](./logreview.tf) which uses an older `widget_<type> {}` style of terraform and can be updated using the [Terraform Registry Docs](https://registry.terraform.io/providers/newrelic/newrelic/3.34.1/docs/resources/one_dashboard)
2. [Monitoring](./monitoring.tf) which uses a `.tftpl` format json structure to construct the dashboard. Updating the dashboard can be done by using the [Terraform Registry Docs](https://registry.terraform.io/providers/newrelic/newrelic/3.20.1/docs/resources/one_dashboard_json) with a reference example like [#4764](https://github.com/GSA-TTS/FAC/pull/4764/files)


### Usage
```terraform
module "newrelic" {
  source               = "../path/to/source"
  cf_space_name        = var.cf_space.name
  new_relic_account_id = var.new_relic_account_id
  new_relic_api_key    = var.new_relic_api_key
}
```
