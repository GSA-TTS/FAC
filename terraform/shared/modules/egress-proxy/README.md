# Egress proxy Terraform module

## Usage

```
module "egress-proxy" {
  source = "<path to module>"

  name          = "egress"
  cf_org_name   = local.cf_org_name
  cf_space_name = local.cf_space_name
  client_space  = local.cf_space_name

  allowlist = {
    client1 = ["*.sam.gov:443", "*.login.gov:443"],
    client2 = ["gsa.gov:443"],
  }
  denylist = {
    client1 = ["bad.sam.gov:443", "verybad.login.gov:443"],
    client2 = ["sobad.gsa.gov:443"]
  }
}
```

Credentials and route for the proxy are stored in the `egress-creds` service in the client space.

> **Note**
> 
> It's up to you to bind the `egress-creds` service to the clients, read the credentials from `VCAP_SERVICES`, and configure your app appropriately to use the proxy!

## Deployment architecture

```mermaid
    C4Context
      title blue items are managed by the module
      Boundary(system, "system boundary") {
          Boundary(trusted_local_egress, "egress-controlled space", "trusted-local-egress ASG") {
            System(credentials, "Proxy Credentials", "UPSI")
            System_Ext(client1, "Client1", "a client")
          }

          Boundary(public_egress, "egress-permitted space", "public-egress ASG") {
            System(https_proxy, "web egress proxy", "proxy for HTTP/S connections")
          }
      }
      
      Boundary(external_boundary, "external boundary") {
        System_Ext(external_service, "external service", "service that the application relies on")
      }

      Rel(credentials, client1, "delivers credentials", "VCAP_SERVICES")
      Rel(client1, https_proxy, "makes request", "HTTP/S")
      Rel(https_proxy, external_service, "proxies request", "HTTP/S")
```


1. Creates an egress proxy in the designated space
2. Adds network-policies so that clients can reach the proxy
3. Creates a user-provided service instance in the client space with credentials

## TODO

* Once it's possible, [create the UPSI in the egress space and share it to the client space](https://github.com/cloudfoundry-community/terraform-provider-cloudfoundry/issues/481)
* Support multiple client spaces (maybe a map of allowlist and denylist entries per space?)
* Pay attention to the port number; right now it's ignored (the proxy has a fixed set of ports in the config file)
* Pay attention to the client ID; right now allow/deny are a union across all client apps
