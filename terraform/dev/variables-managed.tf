# The content of this file is managed by Terraform. If you modify it, it may
# be reverted the next time Terraform runs. If you want to make changes, do it
# in ../meta/bootstrap-env/templates.

variable "cf_user" {
  type        = string
  description = "cloud.gov deployer account user"
}

variable "cf_password" {
  type        = string
  description = "secret; cloud.gov deployer account password"
  sensitive   = true
}
