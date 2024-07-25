variable "cf_org_name" {
  type        = string
  description = "name of the organization to configure"
  default     = "gsa-tts-oros-fac"
}

variable "cf_space_name" {
  type        = string
  description = "name of the space to configure"
  # No default... The calling module knows which env is for which space and we
  # shouldn't assume it!
}

variable "decoded_json" {
  type        = string
  description = "decoded json"
}
