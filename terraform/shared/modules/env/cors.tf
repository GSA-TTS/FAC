locals {
  cors_headers = var.cors_json
}
resource "null_resource" "cors_script" {
  provisioner "local-exec" {
    command = "./cors-script.sh ${locals.cors_headers}"
  }
  depends_on = [module.s3-public]
}
