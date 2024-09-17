### WIP Readme


**Make sure to have CF CLI on WSL2 Ubuntu**
```
# ...first add the Cloud Foundry Foundation public key and package repository to your system
wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -
echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list
# ...then, update your local package index, then finally install the cf CLI
sudo apt-get update
sudo apt-get install cf8-cli
```

**For use within the sandbox-gsa**
`cd terraform/sandbox/`
` ../../bin/ops/create_service_account.sh -o sandbox-gsa -s <firstname.lasname> -u <username>-workspace-deployer > secrets.auto.tfvars`
The script will output the `username` (as `cf_user`) and `password` (as `cf_password`) for your `<ACCOUNT_NAME>`. Read more in the [cloud.gov service account documentation](https://cloud.gov/docs/services/cloud-gov-service-account/).

`cf create-service s3 basic workspace-terraform-state`
`cf create-service-key <key-name> workspace-terraform-state`
`cf service-key workspace-terraform-state <key-name>`
Copy `access_key_id`, `secret_access_key`, `bucket`, `region` and `endpoint` values into `shared/config/sandbox.tfvars`

**For use within the cf space sandbox**
`cd terraform/sandbox/`
The keys will be managed by the meta module, so all you have to do is `cf service-key ${SERVICE_ACCOUNT} ${SERVICE_ACCOUNT}-key`, and then copy the `username` (as `cf_user`) and `password` (as `cf_password`) into `secrets.auto.tfvars` in the `/sandbox/` folder.



**Pre-Req for proxy:**
1. You must navigate to /terraform/shared/modules/https-proxy, run `terraform init` and `terraform plan` in order to generate a `proxy.zip` for the module to have a reference on what it will use as source for the app when it attempts to deploy

Security Groups:
```
cf bind-security-group public_networks_egress <ORGNAME> --lifecycle running --space <SPACENAME>
cf bind-security-group trusted_local_networks_egress <ORGNAME> --lifecycle running --space <SPACENAME>
cf bind-security-group trusted_local_networks <ORGNAME> --lifecycle running --space <SPACENAME>
```

**Getting it to run the first time:**
```terraform
#### ClamAV ####
# terraform\shared\modules\sandbox\clamav.tf
depends_on = [module.https-proxy.https_proxy]

#### Proxy ####
# terraform\shared\modules\sandbox\https-proxy.tf
depends_on = [module.fac-app.app_id, module.clamav.app_id]

#### App ####
# terraform\shared\modules\app\app.tf
environment = {
  # PROXYROUTE = var.https_proxy
  ENV        = "SANDBOX"
}

# terraform\shared\modules\app\variables.tf
# Can't be created before the app exists
# variable "https_proxy" {
#   type        = string
#   description = "the full string of the https proxy for use with the logshipper app"
# }
```

**Once things have been built successfully for the first time (- the app):**
```terraform
# In shared/modules/app/app.tf
# Uncomment this
service_binding {
    service_instance = cloudfoundry_user_provided_service.clam.id
}

# In shared/modules/app/variables.tf
# uncommment this
variable "https_proxy" {
  type        = string
  description = "the full string of the https proxy for use with the logshipper app"
}

# In shared/modules/sandbox/app.tf
# uncomment this
https_proxy   = module.https-proxy.https_proxy

# In shared/modules/sandbox/clamav.tf
# comment this out
# depends_on     = [module.https-proxy.https_proxy]

# In shared/modules/sandbox/clamav.tf
# comment this out
# depends_on = [module.fac-app.app_id]
```

If all done correctly, the plan should look something like:
```terraform
  # module.sandbox.module.fac-app.cloudfoundry_app.fac_app will be updated in-place
  ~ resource "cloudfoundry_app" "fac_app" {
      ~ environment                     = (sensitive value)
        id                              = "3c62d5ad-14a6-44aa-9745-6f22efcf88f6"
      ~ id_bg                           = "3c62d5ad-14a6-44aa-9745-6f22efcf88f6" -> (known after apply)
        name                            = "gsa-fac"
        # (19 unchanged attributes hidden)

      ~ service_binding {
          ~ service_instance = "d87d8062-6be5-4546-aebe-4ea085c66298" -> "88091522-2e09-40bb-84df-925438bfb7f7"
            # (2 unchanged attributes hidden)
        }
      ~ service_binding {
          ~ service_instance = "0dfc5f01-bccf-4bd2-9376-b0fe20213a38" -> "d87d8062-6be5-4546-aebe-4ea085c66298"
            # (2 unchanged attributes hidden)
        }
      ~ service_binding {
          ~ service_instance = "ba5b3080-b968-442b-821f-54b1b16a627c" -> "0dfc5f01-bccf-4bd2-9376-b0fe20213a38"
            # (2 unchanged attributes hidden)
        }
      + service_binding {
          + service_instance = "ba5b3080-b968-442b-821f-54b1b16a627c"
        }

        # (1 unchanged block hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.
```


### Lessons Learned:
- If you are attempting to do a deployment and terraform fails because of inflight prior failed deploys, run `cf cancel-deployment gsa-fac` to get it back to a stable state to ensure it can attempt to deploy a new revision
- Because we are wrapped around newrelic, and subsequently gunicorn is, we need to use the current `Procfile` to wrap the gunicorn threads in newrelic.
