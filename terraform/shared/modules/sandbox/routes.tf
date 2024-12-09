locals {
  # Make a clean list of the client apps for iteration purposes
  clients      = toset(keys(merge(var.allowlist, var.denylist)))
  client_space = var.cf_space_name
}

data "cloudfoundry_space" "client_space" {
  provider = cloudfoundry-community

  org_name = var.cf_org_name
  name     = local.client_space
}

data "cloudfoundry_app" "clients" {
  provider = cloudfoundry-community

  for_each   = local.clients
  name_or_id = each.key
  space      = data.cloudfoundry_space.client_space.id
  depends_on = [module.fac-app, module.clamav, cloudfoundry_app.postgrest, module.https-proxy]
}

resource "cloudfoundry_network_policy" "client_routing" {
  provider = cloudfoundry-community

  for_each = local.clients
  policy {
    source_app      = data.cloudfoundry_app.clients[each.key].id
    destination_app = module.https-proxy.https_proxy
    port            = "61443"
  }
  depends_on = [module.fac-app, module.clamav, cloudfoundry_app.postgrest, module.https-proxy]
}
