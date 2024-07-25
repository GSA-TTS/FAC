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

variable "string_json" {
  type        = string
  description = "The JSON used for managing CORS headers."
}

