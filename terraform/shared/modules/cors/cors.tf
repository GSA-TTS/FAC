resource "null_resource" "cors_script" {
  provisioner "local-exec" {
    working_dir = path.module
    interpreter = ["/bin/bash", "-c"]
    command     = "./cors-script.sh ${var.cf_org_name} ${var.cf_space_name} ${var.decoded_json}"
  }
}
