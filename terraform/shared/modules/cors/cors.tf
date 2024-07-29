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
  # Using timestamp() seems to be breaking the terraform plans, so opting for the
  # resource to be updated if a change occurs to the 'cors-script.sh'
  triggers = {
    md5 = "${filemd5("${path.module}/cors-script.sh")}"
  }
}
