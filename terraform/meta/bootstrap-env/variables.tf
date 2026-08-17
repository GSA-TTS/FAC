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

variable "allow_ssh" {
  type        = bool
  description = "whether SSH should be enabled in the space (and corresponding egress space)"
  default     = true
}
