variable "cf_org_name" {
  type        = string
  description = "name of the organization to configure"
  default     = "gsa-tts-oros-fac"
}

variable "pgrst_jwt_secret" {
  type        = string
  description = "the JWT signing secret for validating JWT tokens from api.data.gov"
}

variable "new_relic_license_key" {
  type        = string
  description = "the license key to use when setting up the New Relic agent"
}

variable "sam_api_key" {
  type = string
}
variable "django_secret_login_key" {
  type = string
}
variable "login_client_id" {
  type = string
}
variable "login_secret_key" {
  type = string
}

variable "branch_name" {
  type        = string
  description = "the heads value for the branch you wish to deploy (default would be main)"
  # We don't specify a default here because we want to specify a branch to deploy
}
