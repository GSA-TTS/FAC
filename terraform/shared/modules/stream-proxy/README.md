# stream egress proxy Terraform module

## Usage

This example proxies connections to an upstream SMTP relay

```
module "smtp-proxy" {
  source = "<path to module>"

  name          = "smtp-proxy"
  cf_org_name   = local.cf_org_name
  cf_space_name = local.cf_space_name
  client_space  = local.cf_space_name

  upstream = "smtp-relay.gmail.com:587"
  clients = [ "app1" ]
}
```

Credentials and route for the proxy are stored in the `${name}-creds` user-provided service instance in the client space.

> **Note**
> 
> It's up to you to bind the `${name}-creds` service to the clients, read the credentials from `VCAP_SERVICES`, and configure your app appropriately to use the proxy!

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
            System(stream_proxy, "stream proxy", "proxy for TCP connections")
          }
      }
      
      Boundary(external_boundary, "external boundary") {
        System_Ext(external_relay, "external relay", "TCP service that the application relies on")
      }

      Rel(credentials, client1, "delivers credentials", "VCAP_SERVICES")
      Rel(client1, stream_proxy, "makes connection", "TCP")
      Rel(stream_proxy, external_relay, "proxies connection", "TCP")
```

1. Creates an egress proxy in the designated space
2. Adds network-policies so that clients can reach the proxy
3. Creates a user-provided service instance in the client space with credentials

## TODO

* Once it's possible, [create the UPSI in the egress space and share it to the client space](https://github.com/cloudfoundry-community/terraform-provider-cloudfoundry/issues/481)
* Require use of a username/password (currently network policies prevent unwanted access)
