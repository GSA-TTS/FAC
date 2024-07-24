
resource "null_resource" "cors_script" {
  provisioner "local-exec" {
    command = "./cors-script.sh ${locals.cors_json}"
  }
  depends_on = [module.s3-public]
}
