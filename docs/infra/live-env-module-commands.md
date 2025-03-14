## Information regarding the commands and steps taken to catalog all terraform resources that need upgrading

#### Preview
```
# Live RDS
terraform state show -state=terraform.tfstate.preview module.preview.module.database.cloudfoundry_service_instance.rds | grep -m 1 id
7a2931da-7968-46b2-9b86-88dc27ecb826
terraform state rm -state=terraform.tfstate.preview module.preview.module.database.cloudfoundry_service_instance.rds

# Backup RDS
terraform state show -state=terraform.tfstate.preview module.preview.module.snapshot-database.cloudfoundry_service_instance.rds | grep -m 1 id
cbb796d4-3c0d-4ebd-80b0-0e7c6183d681
terraform state rm -state=terraform.tfstate.preview module.preview.module.snapshot-database.cloudfoundry_service_instance.rds

# Public S3
terraform state show -state=terraform.tfstate.preview module.preview.module.s3-public.cloudfoundry_service_instance.bucket | grep -m 1 id
fb529fd2-75cc-4c07-8a90-893f443a2a67
terraform state rm -state=terraform.tfstate.preview module.preview.module.s3-public.cloudfoundry_service_instance.bucket

# Private S3
terraform state show -state=terraform.tfstate.preview module.preview.module.s3-private.cloudfoundry_service_instance.bucket | grep -m 1 id
13f6f615-c772-4529-987a-5b76ab0eea6d
terraform state rm -state=terraform.tfstate.preview module.preview.module.s3-private.cloudfoundry_service_instance.bucket

# Backups S3
terraform state show -state=terraform.tfstate.preview module.preview-backups-bucket.cloudfoundry_service_instance.bucket | grep -m 1 id
01abcf56-c8c6-4d61-965b-894cf375ab0d
terraform state rm -state=terraform.tfstate.preview module.preview-backups-bucket.cloudfoundry_service_instance.bucket

#Logshipper S3
terraform state show -state=terraform.tfstate.preview module.preview.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket | grep -m 1 id
c65050a7-fbba-4e27-8e69-0163835f17e3
terraform state rm -state=terraform.tfstate.preview module.preview.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket

#Scanner S3
terraform state show -state=terraform.tfstate.preview module.preview.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket | grep -m 1 id
5cef0c0b-1e68-451a-8e32-bc175a491bfa
terraform state rm -state=terraform.tfstate.preview module.preview.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket

terraform state rm -state=terraform.tfstate.preview module.preview.module.clamav.cloudfoundry_app.clamav_api
terraform state rm -state=terraform.tfstate.preview module.preview.module.file_scanner_clamav.cloudfoundry_app.clamav_api
```
#### Preview Imports
```
# terraform/preview/imports.tf
import {
  to = module.preview.module.database.cloudfoundry_service_instance.rds
  id = "7a2931da-7968-46b2-9b86-88dc27ecb826"
}

import {
  to = module.preview.module.snapshot-database.cloudfoundry_service_instance.rds
  id = "cbb796d4-3c0d-4ebd-80b0-0e7c6183d681"
}

import {
  to = module.preview.module.s3-public.cloudfoundry_service_instance.bucket
  id = "fb529fd2-75cc-4c07-8a90-893f443a2a67"
}

import {
  to = module.preview.module.s3-private.cloudfoundry_service_instance.bucket
  id = "13f6f615-c772-4529-987a-5b76ab0eea6d"
}

import {
  to = module.preview-backups-bucket.cloudfoundry_service_instance.bucket
  id = "01abcf56-c8c6-4d61-965b-894cf375ab0d"
}
```

#### Dev
```
# Live RDS
terraform state show -state=terraform.tfstate.dev module.dev.module.database.cloudfoundry_service_instance.rds | grep -m 1 id
b036f306-5950-4078-9309-cfda6ed03482
terraform state rm -state=terraform.tfstate.dev module.dev.module.database.cloudfoundry_service_instance.rds

# Backup RDS
terraform state show -state=terraform.tfstate.dev module.dev.module.snapshot-database.cloudfoundry_service_instance.rds | grep -m 1 id
86a11021-7922-411b-b0ca-4341b7a0b911
terraform state rm -state=terraform.tfstate.dev module.dev.module.snapshot-database.cloudfoundry_service_instance.rds

# Public S3
terraform state show -state=terraform.tfstate.dev module.dev.module.s3-public.cloudfoundry_service_instance.bucket | grep -m 1 id
07cc1c42-1b73-44bd-a4f6-8f4392f657f3
terraform state rm -state=terraform.tfstate.dev module.dev.module.s3-public.cloudfoundry_service_instance.bucket

# Private S3
terraform state show -state=terraform.tfstate.dev module.dev.module.s3-private.cloudfoundry_service_instance.bucket | grep -m 1 id
d791aab9-8e4d-4fe2-8d0c-4977aea66719
terraform state rm -state=terraform.tfstate.dev module.dev.module.s3-private.cloudfoundry_service_instance.bucket

# Backups S3
terraform state show -state=terraform.tfstate.dev module.dev-backups-bucket.cloudfoundry_service_instance.bucket | grep -m 1 id
4bebb1dc-3951-420e-810e-34e461776679
terraform state rm -state=terraform.tfstate.dev module.dev-backups-bucket.cloudfoundry_service_instance.bucket

#Logshipper S3
terraform state show -state=terraform.tfstate.dev module.dev.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket | grep -m 1 id
d79b8e4c-c1f5-4711-8172-5da3f9298cc4
terraform state rm -state=terraform.tfstate.dev module.dev.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket

#Scanner S3
terraform state show -state=terraform.tfstate.dev module.dev.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket | grep -m 1 id
c435cb9c-32a7-4a31-828b-48c8c6f3bf37
terraform state rm -state=terraform.tfstate.dev module.dev.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket

terraform state rm -state=terraform.tfstate.dev module.dev.module.clamav.cloudfoundry_app.clamav_api
terraform state rm -state=terraform.tfstate.dev module.dev.module.file_scanner_clamav.cloudfoundry_app.clamav_api

```

#### Dev Imports
```
# terraform/dev/imports.tf
import {
  to = module.dev.module.database.cloudfoundry_service_instance.rds
  id = "b036f306-5950-4078-9309-cfda6ed03482"
}

import {
  to = module.dev.module.snapshot-database.cloudfoundry_service_instance.rds
  id = "86a11021-7922-411b-b0ca-4341b7a0b911"
}

import {
  to = module.dev.module.s3-public.cloudfoundry_service_instance.bucket
  id = "07cc1c42-1b73-44bd-a4f6-8f4392f657f3"
}

import {
  to = module.dev.module.s3-private.cloudfoundry_service_instance.bucket
  id = "d791aab9-8e4d-4fe2-8d0c-4977aea66719"
}

import {
  to = module.dev-backups-bucket.cloudfoundry_service_instance.bucket
  id = "4bebb1dc-3951-420e-810e-34e461776679"
}
```

#### Staging
```
# Live RDS
terraform state show -state=terraform.tfstate.staging module.staging.module.database.cloudfoundry_service_instance.rds | grep -m 1 id
ff264965-e93f-4b75-b358-49cdadaec30f
terraform state rm -state=terraform.tfstate.staging module.staging.module.database.cloudfoundry_service_instance.rds

# Backup RDS
terraform state show -state=terraform.tfstate.staging module.staging.module.snapshot-database.cloudfoundry_service_instance.rds | grep -m 1 id
2916eb7d-5222-4347-97d4-b43aa4130e56
terraform state show -state=terraform.tfstate.staging module.staging.module.snapshot-database.cloudfoundry_service_instance.rds | grep -m 1 id

# Public S3
terraform state show -state=terraform.tfstate.staging module.staging.module.s3-public.cloudfoundry_service_instance.bucket | grep -m 1 id
cc1dff78-87ee-4d2e-8774-681e397d9dd3
terraform state rm -state=terraform.tfstate.staging module.staging.module.s3-public.cloudfoundry_service_instance.bucket

# Private S3
terraform state show -state=terraform.tfstate.staging module.staging.module.s3-private.cloudfoundry_service_instance.bucket | grep -m 1 id
f43724f8-a94f-4ee9-9234-72aac309afad
terraform state rm -state=terraform.tfstate.staging module.staging.module.s3-private.cloudfoundry_service_instance.bucket

# Backups S3
terraform state show -state=terraform.tfstate.staging module.staging-backups-bucket.cloudfoundry_service_instance.bucket | grep -m 1 id
d6222847-cc59-4d3b-bcc3-7df080c70f1c
terraform state rm -state=terraform.tfstate.staging module.staging-backups-bucket.cloudfoundry_service_instance.bucket

#Logshipper S3
terraform state show -state=terraform.tfstate.staging module.staging.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket | grep -m 1 id
3db5447d-8403-45c6-8b47-63ea899fd1cd
terraform state rm -state=terraform.tfstate.staging module.staging.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket

#Scanner S3
terraform state show -state=terraform.tfstate.staging module.staging.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket | grep -m 1 id
b4cf43f9-7ada-4c21-9d16-b340672e50ae
terraform state rm -state=terraform.tfstate.staging module.staging.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket

terraform state rm -state=terraform.tfstate.staging module.staging.module.clamav.cloudfoundry_app.clamav_api
terraform state rm -state=terraform.tfstate.staging module.staging.module.file_scanner_clamav.cloudfoundry_app.clamav_api

```

#### Staging Imports
```
# terraform/staging/imports.tf
import {
  to = module.staging.module.database.cloudfoundry_service_instance.rds
  id = "ff264965-e93f-4b75-b358-49cdadaec30f"
}

import {
  to = module.staging.module.snapshot-database.cloudfoundry_service_instance.rds
  id = "2916eb7d-5222-4347-97d4-b43aa4130e56"
}

import {
  to = module.staging.module.s3-public.cloudfoundry_service_instance.bucket
  id = "cc1dff78-87ee-4d2e-8774-681e397d9dd3"
}

import {
  to = module.staging.module.s3-private.cloudfoundry_service_instance.bucket
  id = "f43724f8-a94f-4ee9-9234-72aac309afad"
}

import {
  to = module.staging-backups-bucket.cloudfoundry_service_instance.bucket
  id = "d6222847-cc59-4d3b-bcc3-7df080c70f1c"
}
```

#### Production
```
# Live RDS
terraform state show -state=terraform.tfstate.production module.production.module.database.cloudfoundry_service_instance.rds | grep -m 1 id
258ac781-7f34-465f-b24a-b04ec258f7db
terraform state rm -state=terraform.tfstate.production module.production.module.database.cloudfoundry_service_instance.rds

# Backup RDS
terraform state show -state=terraform.tfstate.production module.production.module.snapshot-database.cloudfoundry_service_instance.rds | grep -m 1 id
e026cae8-7564-4886-9317-f84dc4a5b339
terraform state show -state=terraform.tfstate.production module.production.module.snapshot-database.cloudfoundry_service_instance.rds | grep -m 1 id

# Public S3
terraform state show -state=terraform.tfstate.production module.production.module.s3-public.cloudfoundry_service_instance.bucket | grep -m 1 id
8e72011f-f010-4ab4-a1d6-7d3694f8fa78
terraform state rm -state=terraform.tfstate.production module.production.module.s3-public.cloudfoundry_service_instance.bucket

# Private S3
terraform state show -state=terraform.tfstate.production module.production.module.s3-private.cloudfoundry_service_instance.bucket | grep -m 1 id
ac8bf271-4c6d-4ee0-bd36-1415b839a93c
terraform state rm -state=terraform.tfstate.production module.production.module.s3-private.cloudfoundry_service_instance.bucket

#Logshipper S3
terraform state show -state=terraform.tfstate.production module.production.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket | grep -m 1 id
2f160a41-a7b7-417e-8856-f665e11b0d03
terraform state rm -state=terraform.tfstate.production module.production.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket

#Scanner S3
terraform state show -state=terraform.tfstate.production module.production.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket | grep -m 1 id
ca564d14-b89a-4944-a43f-033dca62ab30
terraform state rm -state=terraform.tfstate.production module.production.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket

terraform state rm -state=terraform.tfstate.production module.production.module.clamav.cloudfoundry_app.clamav_api
terraform state rm -state=terraform.tfstate.production module.production.module.file_scanner_clamav.cloudfoundry_app.clamav_api

```

#### Production Imports
```
# terraform/production/imports.tf
import {
  to = module.production.module.database.cloudfoundry_service_instance.rds
  id = "258ac781-7f34-465f-b24a-b04ec258f7db"
}

import {
  to = module.production.module.snapshot-database.cloudfoundry_service_instance.rds
  id = "e026cae8-7564-4886-9317-f84dc4a5b339"
}

import {
  to = module.production.module.s3-public.cloudfoundry_service_instance.bucket
  id = "8e72011f-f010-4ab4-a1d6-7d3694f8fa78"
}

import {
  to = module.production.module.s3-private.cloudfoundry_service_instance.bucket
  id = "ac8bf271-4c6d-4ee0-bd36-1415b839a93c"
}

import {
  to = module.domain.cloudfoundry_route.origin_route
  id = "d560bd38-f68e-4613-8c63-f404a252c3a3"
}
```


#### Outlier
```
terraform state show -state=terraform.tfstate.meta module.s3-backups.cloudfoundry_service_instance.bucket | grep -m 1 id
040c4133-1efe-4281-a485-005960b58405
terraform state rm -state=terraform.tfstate.meta module.s3-backups.cloudfoundry_service_instance.bucket
```

```
# terraform/meta/imports.tf
import {
  to = module.s3-backups.cloudfoundry_service_instance.bucket
  id = "040c4133-1efe-4281-a485-005960b58405"
}
```
