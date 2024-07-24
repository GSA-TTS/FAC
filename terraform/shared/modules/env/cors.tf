locals {
  cors_json = jsonencode(
    {
      "CORSRules" : [
        {
          "AllowedHeaders" : [
            "Authorization"
          ],
          "AllowedMethods" : [
            "HEAD",
            "GET"
          ],
          "AllowedOrigins" : [
            "https://[ENV_DOMAIN]"
          ],
          "ExposeHeaders" : [
            "ETag"
          ]
        }
      ]
    }
  )
}

resource "null_resource" "cors_script" {
  provisioner "local-exec" {
    command = "./cors-script.sh ${locals.cors_json}"
  }
}
