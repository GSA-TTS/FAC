locals {

  # Make a clean list of the client apps for iteration purposes
  clients = toset(keys(merge(var.allowlist, var.denylist)))

  # Generate Caddy-compatible allow and deny ACLs, one target per line.
  #
  # For now, there's just one consolidated allowlist and denylist, no matter
  # what apps they were specified for. Future improvments could improve this,
  # but it would mean also changing the proxy to be both more complex (in terms
  # of how the Caddyfile is constructed) and more discriminating (in terms of
  # recognizing client apps based on GUIDs supplied by Envoy in request headers,
  # as well as the destination ports). However, adding these improvements won't
  # require modifying the module's interface, since we're already collecting
  # that refined information.
  allowacl = templatefile("${path.module}/acl.tftpl", { list = var.allowlist })
  denyacl  = templatefile("${path.module}/acl.tftpl", { list = var.denylist })
}

###
### Set up the authenticated egress application in the target space on apps.internal
###

data "cloudfoundry_domain" "internal" {
  name = "apps.internal"
}

resource "cloudfoundry_route" "egress_route" {
  space    = data.cloudfoundry_space.egress_space.id
  domain   = data.cloudfoundry_domain.internal.id
  hostname = "${var.cf_org_name}-${replace(var.cf_space_name, ".", "-")}-${var.name}"
  # Yields something like: orgname-spacename-name.apps.internal
}

resource "random_uuid" "username" {}
resource "random_password" "password" {
  length  = 16
  special = false
}

data "cloudfoundry_space" "egress_space" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

# This zips up just the depoyable files from the specified gitref in the
# cg-egress-proxy repository
data "external" "proxyzip" {
  program     = ["/bin/sh", "prepare-proxy.sh"]
  working_dir = path.module
  query = {
    gitref = var.gitref
  }
}

resource "cloudfoundry_app" "egress_app" {
  name             = var.name
  space            = data.cloudfoundry_space.egress_space.id
  path             = "${path.module}/${data.external.proxyzip.result.path}"
  source_code_hash = filesha256("${path.module}/${data.external.proxyzip.result.path}")
  buildpack        = "binary_buildpack"
  command          = "./caddy run --config Caddyfile"
  memory           = var.egress_memory
  instances        = var.instances
  strategy         = "rolling"

  routes {
    route = cloudfoundry_route.egress_route.id
  }
  environment = {
    PROXY_ALLOW : local.allowacl
    PROXY_DENY : local.denyacl
    PROXY_USERNAME : random_uuid.username.result
    PROXY_PASSWORD : random_password.password.result
  }
}

###
### Set up network policies so that the clients can reach the proxy
###

data "cloudfoundry_space" "client_space" {
  org_name = var.cf_org_name
  name     = var.client_space
}

data "cloudfoundry_app" "clients" {
  for_each   = local.clients
  name_or_id = each.key
  space      = data.cloudfoundry_space.client_space.id
}

resource "cloudfoundry_network_policy" "client_routing" {
  for_each = local.clients
  policy {
    source_app      = data.cloudfoundry_app.clients[each.key].id
    destination_app = cloudfoundry_app.egress_app.id
    port            = "61443"
  }
}

###
### Create a credential service for bound clients to use when make requests of the proxy
###
locals {
  https_proxy = "https://${random_uuid.username.result}:${random_password.password.result}@${cloudfoundry_route.egress_route.endpoint}:61443"
  domain      = cloudfoundry_route.egress_route.endpoint
  username    = random_uuid.username.result
  password    = random_password.password.result
  protocol    = "https"
  port        = 61443
}

resource "cloudfoundry_user_provided_service" "credentials" {
  name  = "${var.name}-creds"
  space = data.cloudfoundry_space.client_space.id
  credentials = {
    "uri"      = local.https_proxy
    "domain"   = local.domain
    "username" = local.username
    "password" = local.password
    "protocol" = local.protocol
    "port"     = local.port
  }
}
