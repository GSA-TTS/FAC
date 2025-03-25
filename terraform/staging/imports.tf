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

import {
  to = module.staging.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket
  id = "3db5447d-8403-45c6-8b47-63ea899fd1cd"
}

import {
  to = module.staging.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket
  id = "b4cf43f9-7ada-4c21-9d16-b340672e50ae"
}
