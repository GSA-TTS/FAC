
module "egress-proxy" {
  source = "../egress-proxy"

  name          = "egress"
  cf_org_name   = var.cf_org_name               # gsa-tts-oros-fac
  cf_space_name = "${var.cf_space_name}-egress" # eg prod-egress
  client_space  = var.cf_space_name             # eg prod

  # head of the "main" branch as of this commit
  gitref = "7487f882903b9e834a5133a883a88b16fb8b16c9"

  allowlist = {
    gsa-fac = ["api.sam.gov:443"],
  }
  denylist = {}
}

