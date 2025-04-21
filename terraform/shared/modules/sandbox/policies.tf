# The following use the community provider as these have not been moved to the official provider.
# In the event that these resources do not get moved, the following will likely break
# and need to be rebuilt in a different method. In the event the v2 api gets an extended depreciation,
# these may continue to be used until the provider adds this functionality, in which case, should be
# upgraded as soon as possible.
resource "cloudfoundry_network_policy" "app-network-policy" {
  provider = cloudfoundry-community

  policy {
    source_app      = module.fac-app.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
  policy {
    source_app      = module.fac-app.app_id
    destination_app = module.clamav.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}

resource "cloudfoundry_network_policy" "clamav-network-policy" {
  provider = cloudfoundry-community
  policy {
    source_app      = module.clamav.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }

  policy {
    source_app      = module.file_scanner_clamav.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}

resource "cloudfoundry_network_policy" "logshipper-network-policy" {
  provider = cloudfoundry-community
  policy {
    source_app      = module.logshipper.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}

resource "cloudfoundry_network_policy" "scanner-network-policy" {
  provider = cloudfoundry-community
  policy {
    source_app      = module.fac-file-scanner.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
  policy {
    source_app      = module.fac-file-scanner.app_id
    destination_app = module.file_scanner_clamav.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}
