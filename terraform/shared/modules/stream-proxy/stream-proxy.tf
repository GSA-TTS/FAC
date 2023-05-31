locals {
  domain   = split(":", var.upstream)[0]
  port     = split(":", var.upstream)[1]
  endpoint = "${cloudfoundry_route.egress_route.endpoint}:8080"
}

###
### Set up the proxy application in the target space on apps.internal
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

data "cloudfoundry_space" "egress_space" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

# This zips up just the depoyable files
data "external" "proxyzip" {
  program     = ["/bin/sh", "prepare-proxy.sh"]
  working_dir = path.module
}

resource "cloudfoundry_app" "egress_app" {
  name             = var.name
  space            = data.cloudfoundry_space.egress_space.id
  path             = "${path.module}/${data.external.proxyzip.result.path}"
  source_code_hash = filesha256("${path.module}/${data.external.proxyzip.result.path}")
  buildpack        = "nginx_buildpack"
  memory           = var.memory
  instances        = var.instances
  strategy         = "rolling"

  routes {
    route = cloudfoundry_route.egress_route.id
  }
  environment = {
    # Note that the value here has to be resolvable during staging or NGINX
    # will reject the config file as invalid!
    STREAM_DOMAIN : local.domain
    STREAM_PORT : local.port
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
  for_each   = var.clients
  name_or_id = each.value
  space      = data.cloudfoundry_space.client_space.id
}

resource "cloudfoundry_network_policy" "client_routing" {
  for_each = var.clients
  policy {
    source_app      = data.cloudfoundry_app.clients[each.value].id
    destination_app = cloudfoundry_app.egress_app.id_bg
    port            = "8080"
  }
}

### 
### Create a credential service for bound clients to use when make requests of the proxy
###

resource "cloudfoundry_user_provided_service" "credentials" {
  name  = "${var.name}-creds"
  space = data.cloudfoundry_space.client_space.id
  credentials = {
    "domain" = cloudfoundry_route.egress_route.endpoint
    "port"   = 8080
  }
}
