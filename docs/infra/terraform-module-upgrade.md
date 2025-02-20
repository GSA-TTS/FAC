## Archive of steps taken to upgrade from cloudfoundry-community to cloudfoundry provider

#### Provider Update:
```tf
cloudfoundry = {
    source  = "cloudfoundry/cloudfoundry"
    version = "1.1.0"
}

provider "cloudfoundry" {
  api_url      = "https://api.fr.cloud.gov"
  user         = var.cf_user
  password     = var.cf_password
}
```

#### Using the GUID for space/orgs:
```tf
data "cloudfoundry_org" "org" {
  name = var.cf_org_name
}

data "cloudfoundry_space" "space" {
  name = var.cf_space_name
  org  = data.cloudfoundry_org.org.id
}
```

#### Plan failure to illustrate what is happening:
```
│ Error: Resource instance managed by newer provider version
│
│ The current state of module.sandbox.module.clamav.cloudfoundry_app.clamav_api was created by a newer provider version than
│ is currently selected. Upgrade the cloudfoundry provider to work with this state.
╵
╷
│ Error: Resource instance managed by newer provider version
│
│ The current state of module.sandbox.module.database.cloudfoundry_service_instance.rds was created by a newer provider version than
│ is currently selected. Upgrade the cloudfoundry provider to work with this state.

╷
│ Error: Resource instance managed by newer provider version
│
│ The current state of module.sandbox.module.snapshot-database.cloudfoundry_service_instance.rds was created by a newer provider version than
│ is currently selected. Upgrade the cloudfoundry provider to work with this state.
```

#### Modifying the tfstate:

Due to us using a partial configuration, the exact steps cannot be done directly interfacing with the s3. As such, we will download the state to our local `aws s3 cp s3://$BUCKET/terraform.tfstate.sandbox .`, move the existing state inside the bucket to a different name `aws s3 mv s3://$BUCKET/terraform.tfstate.sandbox s3://$BUCKET/terraform.tfstate.sandbox.bak` and then proceed to modify the state, reuploading with the original name.

Unconfigure the backend s3 {} block in `providers.tf`, simply commenting it out will do, then run `terraform init -migrate-state`. This will allow us to work with a local state file and actually read the contents. Remember to delete the `terraform.tfstate` that it generates, as we are using the state `terraform.tfstate.sandbox` which was downloaded from s3.

**Example:**
Follow the steps in the [cloudfoundry provider migration guide](https://github.com/cloudfoundry/terraform-provider-cloudfoundry/blob/main/migration-guide/Readme.md) to migrate an existing use of the v1 module to v2. As an example, here are the steps for upgrading a database module:

1. Update source line to point to v2 module and change `cf_space_name` to `cf_space_id`
1. Verify that `terraform validate` passes
1. Run: `terraform state show module.database.cloudfoundry_service_instance.rds | grep -m 1 id` and copy the ID
1. Run: `terraform state rm module.database.cloudfoundry_service_instance.rds`
1. Run: `terraform import module.database.cloudfoundry_service_instance.rds ID_FROM_STEP_3`
1. Run: `terraform apply` to fill in new computed attributes

#### Live Examples:
**Validate you can see the contents**
```
terraform state list -state=terraform.tfstate.sandbox
```

**Clamav API**
```
cf delete fac-av-${env} -r -f
terraform state rm -state=terraform.tfstate.sandbox module.sandbox.module.clamav.cloudfoundry_app.clamav_api
# let clamav rebuild itsself
```

**Backup RDS**
```
terraform state show -state=terraform.tfstate.sandbox module.sandbox.module.snapshot-database.cloudfoundry_service_instance.rds
terraform state show -state=terraform.tfstate.sandbox module.sandbox.module.snapshot-database.cloudfoundry_service_instance.rds | grep -m 1 id
c5f6bddd-77a8-4af1-a1c1-157c24a0920b
terraform state rm -state=terraform.tfstate.sandbox module.sandbox.module.snapshot-database.cloudfoundry_service_instance.rds
```

**RDS**
```
terraform state show -state=terraform.tfstate.sandbox module.sandbox.module.database.cloudfoundry_service_instance.rds
terraform state show -state=terraform.tfstate.sandbox module.sandbox.module.database.cloudfoundry_service_instance.rds | grep -m 1 id
4f22d420-7be5-43b5-b298-bb73760b6aa8
terraform state rm -state=terraform.tfstate.sandbox module.sandbox.module.database.cloudfoundry_service_instance.rds
```

**Private S3**
```
terraform state show -state=terraform.tfstate.sandbox module.sandbox.module.s3-private.cloudfoundry_service_instance.bucket
terraform state show -state=terraform.tfstate.sandbox module.sandbox.module.s3-private.cloudfoundry_service_instance.bucket | grep -m 1 id
d4da0886-ab87-40aa-a2c3-ce415e298752
terraform state rm -state=terraform.tfstate.sandbox module.sandbox.module.s3-private.cloudfoundry_service_instance.bucket
```

**Public S3**
```
terraform state show -state=terraform.tfstate.sandbox module.sandbox.module.s3-public.cloudfoundry_service_instance.bucket | grep -m 1 id
24ab1bca-286e-4a4f-ae5d-3b46d7e6547c
terraform state rm -state=terraform.tfstate.sandbox module.sandbox.module.s3-public.cloudfoundry_service_instance.bucket
```

**Backups S3**
```
terraform state show -state=terraform.tfstate.sandbox module.sandbox-backups-bucket.cloudfoundry_service_instance.bucket | grep -m 1 id
a9785caf-cc2b-4135-a79f-819022933e00
terraform state rm -state=terraform.tfstate.sandbox module.sandbox-backups-bucket.cloudfoundry_service_instance.bucket
```

#### Add an import block to the `main.tf` file `(sandbox.tf/preview.tf/dev.tf/etc)`
```
import {
  to = module.sandbox.module.snapshot-database.cloudfoundry_service_instance.rds
  id = "c5f6bddd-77a8-4af1-a1c1-157c24a0920b"
}

import {
  to = module.sandbox.module.database.cloudfoundry_service_instance.rds
  id = "4f22d420-7be5-43b5-b298-bb73760b6aa8"
}

import {
  to = module.sandbox.module.s3-private.cloudfoundry_service_instance.bucket
  id = "d4da0886-ab87-40aa-a2c3-ce415e298752"
}

import {
  to = module.sandbox.module.s3-public.cloudfoundry_service_instance.bucket
  id = "24ab1bca-286e-4a4f-ae5d-3b46d7e6547c"
}

import {
  to = module.sandbox-backups-bucket.cloudfoundry_service_instance.bucket
  id = "a9785caf-cc2b-4135-a79f-819022933e00"
}
```

#### Final Steps:
Upload the state file to s3 `aws s3 cp ./terraform.tfstate.sandbox s3://$BUCKET/terraform.tfstate.sandbox`
Uncomment the `backend s3 {}` configuration in `providers.tf`.
Open `helper_scripts/init.sh` and modify the terraform command to look like this and then rerun to actually upgrade the providers with the latest version:
```
terraform init \
  --backend-config=../shared/config/backend.tfvars \
  --backend-config=key=terraform.tfstate.$basename \
  -upgrade
```

Your init output should look like so:
```
Initializing the backend...

Successfully configured the backend "s3"! Terraform will automatically
use this backend unless the backend configuration changes.
Upgrading modules...
- sandbox in ../shared/modules/sandbox
Downloading git::https://github.com/gsa-tts/terraform-cloudgov.git?ref=v2.1.0 for sandbox.clamav...
- sandbox.clamav in .terraform/modules/sandbox.clamav/clamav
Downloading git::https://github.com/gsa-tts/terraform-cloudgov.git?ref=v2.1.0 for sandbox.database...
- sandbox.database in .terraform/modules/sandbox.database/database
- sandbox.fac-app in ../shared/modules/app
- sandbox.https-proxy in ../shared/modules/sandbox-proxy
Downloading git::https://github.com/gsa-tts/terraform-cloudgov.git?ref=v2.1.0 for sandbox.s3-private...
- sandbox.s3-private in .terraform/modules/sandbox.s3-private/s3
Downloading git::https://github.com/gsa-tts/terraform-cloudgov.git?ref=v2.1.0 for sandbox.s3-public...
- sandbox.s3-public in .terraform/modules/sandbox.s3-public/s3
Downloading git::https://github.com/gsa-tts/terraform-cloudgov.git?ref=v2.1.0 for sandbox.sandbox-backups-bucket...
- sandbox.sandbox-backups-bucket in .terraform/modules/sandbox.sandbox-backups-bucket/s3
Downloading git::https://github.com/gsa-tts/terraform-cloudgov.git?ref=v2.1.0 for sandbox.snapshot-database...
- sandbox.snapshot-database in .terraform/modules/sandbox.snapshot-database/database
```

Do a `helper_scripts/plan.sh`
```
terraform plan \
  -var-file="../shared/config/preview.tfvars" \
  -out preview.tfplan
```
and `helper_scripts/apply.sh`
```
terraform apply sandbox.tfplan
```
to finalize the changes, upgrading all existing modules to the latest version.


-------------------

#### Notes
```
basename=$(basename "$(pwd)")
terraform init \
  --backend-config=../shared/config/backend.tfvars \
  --backend-config=key=terraform.tfstate."$basename"

terraform plan \
  -var-file="../shared/config/preview.tfvars" \
  -out preview.tfplan

terraform apply env.tfplan
```

#### Preview Output of items to import
```

