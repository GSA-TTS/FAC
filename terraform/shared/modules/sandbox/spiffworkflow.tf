module "SpiffWorkflow" {
  #source        = "github.com/GSA-TTS/terraform-cloudgov//spiffworkflow?ref=v2.3.0"
  source        = "../spiffworkflow"
  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space.name
  git_pat_token = var.git_pat_token

  process_models_ssh_key = var.process_models_ssh_key

  process_models_repository = "git@github.com:GSA-TTS/gsa-process-models.git"
  #process_models_repository = "https://github.com/asteel-gsa/gsa-process-models.git"
  # This should be a branch (non-main), to load the examples. Edits to existing models will be pushed here.
  source_branch_for_example_models = "process-models-playground"
  # This should be an existing branch in the model repo. New models will be pushed here.
  target_branch_for_saving_changes = "publish-staging-branch"

  service_bindings = {
    "${module.spiffworkflowdb.database_name}"                 = ""
    "${cloudfoundry_service_instance.proxy_credentials.name}" = ""
  }

  tags       = ["SpiffWorkflow"]
  depends_on = [module.spiffworkflowdb]
}

module "spiffworkflowdb" {
  source        = "github.com/gsa-tts/terraform-cloudgov//database?ref=v2.3.0"
  cf_space_id   = data.cloudfoundry_space.space.id
  name          = "spiffworkflow-db"
  tags          = ["rds", "SpiffWorkflow"]
  rds_plan_name = "small-psql"
}
