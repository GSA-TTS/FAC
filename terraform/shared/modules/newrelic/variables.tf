variable "new_relic_account_id" {
  type        = number
  description = "New Relic Account ID"
}

variable "new_relic_api_key" {
  type        = string
  description = "New Relic API key"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name for New Relic"
}