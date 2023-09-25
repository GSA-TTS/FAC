variable "name" {
  type        = string
  description = "name of the environment"
}

variable "org_name" {
  type        = string
  description = "cloud.gov organization name where the environment lives"
}

variable "developers" {
  type        = list(string)
  description = "list of accounts that should have the SpaceDeveloper role"
}

variable "managers" {
  type        = list(string)
  description = "list of accounts that should have the SpaceManager role"
}

variable "asgs" {
  type        = list(string)
  description = "list of application security groups that should apply to the space"
}

variable "populate_creds_in_github" {
  type        = bool
  description = "whether to also populate environment secrets in GitHub"
  default     = false
}

variable "reponame" {
  type        = string
  description = "the OWNER/REPOSITORY in GitHub where deployer secrets for the environment should be set up"
}

variable "allow_ssh" {
  type        = bool
  description = "whether SSH should be enabled in the space (and corresponding egress space)"
  default     = true
}

variable "populate_creds_locally" {
  type        = bool
  description = "whether to create files for working with the environment locally; specify true during local development"
  default     = false
}
