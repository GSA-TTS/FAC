data "cloudfoundry_org" "org" {
  name = var.cf_org_name
}
data "cloudfoundry_space" "space" {
  name = var.cf_space_name
  org  = data.cloudfoundry_org.org.id
}

data "cloudfoundry_domain" "domain" {
  name = var.domain
}

locals {
  destinations = (length(var.app_ids) == 0 ? null : [
    for dest in var.app_ids : { app_id = dest }
  ])
}
resource "cloudfoundry_route" "app_route" {
  domain = data.cloudfoundry_domain.domain.id
  space  = data.cloudfoundry_space.space.id
  host   = var.hostname
  path   = var.path

  destinations = local.destinations
}
