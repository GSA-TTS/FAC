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
  to = module.domain.cloudfoundry_service_instance.external_domain_instance
  id = "c36480a2-ec78-4e75-b175-d6b53abf2400"
}

import {
  to = module.production.module.cg-logshipper.module.s3-logshipper-storage.cloudfoundry_service_instance.bucket
  id = "2f160a41-a7b7-417e-8856-f665e11b0d03"
}

import {
  to = module.production.module.fac-file-scanner.module.quarantine.cloudfoundry_service_instance.bucket
  id = "ca564d14-b89a-4944-a43f-033dca62ab30"
}
