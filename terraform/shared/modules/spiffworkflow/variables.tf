variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space in which to deploy the apps"
}

variable "app_prefix" {
  type        = string
  description = "prefix to use for the three application names (<app_prefix>-[connector|backend|frontend])"
  default     = "spiffworkflow"
}

variable "route_prefix" {
  type        = string
  description = "prefix to use for the application routes (<route_prefix>-connector.app.internal, <route_prefix>.apps.fr.cloud.gov[/api]); leave empty to generate"
  default     = ""
}

variable "rds_plan_name" {
  type        = string
  description = "PSQL database service plan to use"
  # See options at https://cloud.gov/docs/services/relational-database/#plans
  default = "small-psql"
}

variable "rds_json_params" {
  description = "A JSON string of arbitrary parameters"
  type        = string
  default     = null
  # See options at https://cloud.gov/docs/services/relational-database/#setting-optional-parameters-1
}

variable "tags" {
  description = "A list of tags to add to the module's resource"
  type        = set(string)
  default     = []
}

variable "process_models_repository" {
  type        = string
  description = "Git repository with process models (use SSH-style 'git@github.com:...')"
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

variable "source_branch_for_example_models" {
  type        = string
  description = "branch for reading process models"
}

variable "target_branch_for_saving_changes" {
  type        = string
  description = "branch for publishing process model changes"
}

variable "backend_memory" {
  type        = string
  description = "Memory to allocate to backend app, including units"
  default     = "512M"
}

variable "connector_memory" {
  type        = string
  description = "Memory to allocate to connector proxy app, including units"
  default     = "128M"
}

variable "frontend_memory" {
  type        = string
  description = "Memory to allocate to frontend app, including units"
  default     = "256M"
}

variable "backend_imageref" {
  type        = string
  description = "imageref for the specific version of the backend that you want to use. See https://github.com/orgs/GSA-TTS/packages for options."
  default     = "ghcr.io/gsa-tts/terraform-cloudgov/spiffarena-backend:latest"
}

variable "connector_imageref" {
  type        = string
  description = "imageref for the specific version of the connector that you want to use. See https://github.com/orgs/GSA-TTS/packages for options."
  default     = "ghcr.io/gsa-tts/terraform-cloudgov/spiffarena-connector:latest"
}

variable "frontend_imageref" {
  type        = string
  description = "imageref for the specific version of the frontend that you want to use. See https://github.com/orgs/GSA-TTS/packages for options."
  default     = "ghcr.io/gsa-tts/terraform-cloudgov/spiffarena-frontend:latest"
}

variable "backend_instances" {
  type        = number
  description = "the number of instances of the backend application to run (default: 1)"
  default     = 1
}

variable "connector_instances" {
  type        = number
  description = "the number of instances of the connector application to run (default: 1)"
  default     = 1
}

variable "frontend_instances" {
  type        = number
  description = "the number of instances of the frontend application to run (default: 1)"
  default     = 1
}


# Example:
# service_bindings = {
#   my-service = "",
#   (module.my-other-service.name) = "",
#   yet-another-service = <<-EOT
#      {
#        "astring"     : "foo",
#        "anarray"     : ["bar", "baz"],
#        "anarrayobjs" : [
#          {
#            "name": "bat",
#            "value": "boz"
#        ],
#      }
#      EOT
#   }
# }
variable "service_bindings" {
  description = "A map of service instance name to JSON parameter string."
  type        = map(string)
}

variable "git_pat_token" {
  type = string
  description = "the secret pat to clone the github process model repo"
  sensitive = true
}

