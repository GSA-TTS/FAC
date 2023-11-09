locals {
  path = "${path.root}/../${var.name}"
}

# Environments often need to know the base org that everything is in
resource "local_file" "cf_org" {
  count           = (var.populate_creds_locally == true) ? 1 : 0
  filename        = "${local.path}/orgname.auto.tfvars"
  file_permission = "0644"
  content         = <<-EOF
  cf_org_name = "${var.org_name}"
  EOF
}

