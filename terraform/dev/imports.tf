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

import {
  to = module.dev.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket
  id = "d79b8e4c-c1f5-4711-8172-5da3f9298cc4"
}

import {
  to = module.dev.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket
  id = "c435cb9c-32a7-4a31-828b-48c8c6f3bf37"
}
