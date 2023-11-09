variable "new_relic_license_key" {
  type        = string
  description = "the license key to use when setting up the New Relic agent"
}

variable "pgrst_jwt_secret" {
  type        = string
  description = "the JWT signing secret for validating JWT tokens from api.data.gov"
}
