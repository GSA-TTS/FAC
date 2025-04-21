module "smtp-proxy" {
  source        = "../stream-proxy"
  name          = "smtp-proxy"
  cf_org_name   = var.cf_org_name
  cf_space_name = "${var.cf_space.name}-egress"
  client_space  = var.cf_space.name
  instances     = var.smtp_proxy_instances

  upstream = "smtp-relay.gmail.com:587"
  clients  = ["gsa-fac"]
}
