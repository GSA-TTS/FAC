# Leave a script for properly initializing when running locally
resource "local_file" "initialization_script" {
  filename        = "${local.path}/init.sh"
  file_permission = "0755"
  content         = <<-EOF
  #!/bin/bash

  # The content of this file is managed by Terraform. If you modify it, it may
  # be reverted the next time Terraform runs. If you want to make changes, do it
  # in ../meta/bootstrap-env/templates.
  
  set -e
  terraform init \
    --backend-config=../shared/config/backend.tfvars \
    --backend-config=key=terraform.tfstate.$(basename $(pwd))
  EOF
}

resource "local_file" "main-tf" {
  lifecycle {
    ignore_changes = all
  }
  filename        = "${local.path}/${var.name}.tf-example"
  file_permission = "0644"
  content = templatefile("${path.module}/templates/main.tf-template",
    { name = var.name }
  )
}

resource "local_file" "variables-tf" {
  filename        = "${local.path}/variables-managed.tf"
  file_permission = "0644"
  content = file("${path.module}/templates/variables.tf-template")
}

resource "local_file" "providers-tf" {
  filename        = "${local.path}/providers-managed.tf"
  file_permission = "0644"
  content = file("${path.module}/templates/providers.tf-template")
}
