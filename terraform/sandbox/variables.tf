variable "cf_org_name" {
  type        = string
  description = "name of the organization to configure"
  default     = "gsa-tts-oros-fac"
}

variable "cf_user" {
  type        = string
  description = "cloud.gov deployer account user"
}

variable "cf_password" {
  type        = string
  description = "secret; cloud.gov deployer account password"
  sensitive   = true
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

variable "process_models_ssh_key" {
  type        = string
  description = "Private SSH key with read/write access to var.process_models_repository repository"
  sensitive   = true
  # Should look like:
  # -----BEGIN OPENSSH PRIVATE KEY-----
  # ...
  # ...
  # ...
  # -----END OPENSSH PRIVATE KEY-----
}

variable "git_pat_token" {
  type        = string
  description = "the secret pat to clone the github process model repo"
  sensitive   = true
}
