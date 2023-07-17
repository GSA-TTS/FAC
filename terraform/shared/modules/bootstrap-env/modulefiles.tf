locals {
  # These files are kept tightly in sync with the backend config
  managed_files = toset([
    "providers.tf",
  ])

  # These are just starting points, go wild!
  customizable_files = toset([
    "variables.tf",
    "main.tf",
  ])
}

# Leave a script for properly initializing when running locally
resource "local_file" "initialization_script" {
  filename        = "${local.path}/init.sh"
  file_permission = "0755"
  content         = <<-EOF
  #!/bin/bash

  set -e
  terraform init \
    --backend-config=../shared/config/backend.tfvars \
    --backend-config=key=terraform-state-$(basename $(pwd))
  EOF
}

resource "local_file" "managed_files" {
  for_each        = local.managed_files
  filename        = "${local.path}/${each.key}"
  file_permission = "0644"
  content = templatefile("${path.module}/templates/${each.key}-template",
    { name = var.name }
  )
}

resource "local_file" "customizable_files" {
  for_each = local.customizable_files
  lifecycle {
    ignore_changes = all
  }
  filename        = "${local.path}/${each.key}"
  file_permission = "0644"
  content = templatefile("${path.module}/templates/${each.key}-template",
    { name = var.name }
  )
}