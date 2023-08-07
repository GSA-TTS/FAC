# Import existing resources previously provisioned by hand
# Note this is a new experimental block as of Terraform 1.5.0
# More info: https://developer.hashicorp.com/terraform/language/import
# And before you ask why this is so repetitive: No, we cannot use for_each with import blocks.

### dev
import {
  to = module.environments["dev"].cloudfoundry_space.space
  id = "06525ba3-19c2-451b-96e9-ea4a9134e8b9"
}
# import {
#   to = module.environments["dev"].cloudfoundry_space_users.space_permissions
#   id = "06525ba3-19c2-451b-96e9-ea4a9134e8b9"
# }
# import {
#   to = module.environments["dev"].cloudfoundry_service_instance.space_deployer
#   id = "6d4ae7a6-0dfa-4a4d-953b-5dddf2ba30aa"
# }

### staging
import {
  to = module.environments["staging"].cloudfoundry_space.space
  id = "7bbe587a-e8ee-4e8c-b32f-86d0b0f1b807"
}
# import {
#   to = module.environments["staging"].cloudfoundry_space_users.space_permissions
#   id = "7bbe587a-e8ee-4e8c-b32f-86d0b0f1b807"
# }
# import {
#   to = module.environments["staging"].cloudfoundry_service_instance.space_deployer
#   id = "fe49c495-6db9-4daf-a7d4-9362e44e83fb"
# }

### production
import {
  to = module.environments["production"].cloudfoundry_space.space
  id = "5593dba8-7023-49a5-bdbe-e809fe23edf9"
}
# import {
#   to = module.environments["production"].cloudfoundry_space_users.space_permissions
#   id = "5593dba8-7023-49a5-bdbe-e809fe23edf9"
# }
# import {
#   to = module.environments["production"].cloudfoundry_service_instance.space_deployer
#   id = "7b17e5b5-67bf-4e79-9be6-52d5f29dcac9"
# }

### preview
import {
  to = module.environments["preview"].cloudfoundry_space.space
  id = "c21cdcb1-b760-4f3e-968d-469819b448e9"
}
# import {
#   to = module.environments["management"].cloudfoundry_space_users.space_permissions
#   id = "c21cdcb1-b760-4f3e-968d-469819b448e9"
# }
# import {
#   to = module.environments["management"].cloudfoundry_service_instance.space_deployer
#   id = ""
# }
