locals {
  script_path = "${var.cf_space_name}-cors.json"
}
resource "null_resource" "cors_header" {
  provisioner "local-exec" {
    working_dir = path.module
    interpreter = ["/bin/bash", "-c"]
    command     = "./cors-script.sh ${var.cf_org_name} ${var.cf_space_name} ${local.script_path}"
  }
  # https://github.com/hashicorp/terraform/issues/8266#issuecomment-454377049
  # A clever way to get this to run every time, otherwise we would be relying on
  # an md5 hash, which, once this goes into the system, will rarely (if ever)
  # be updated
  triggers = {
    md5 = "${filemd5("${path.module}/cors-script.sh")}"
  }
}
