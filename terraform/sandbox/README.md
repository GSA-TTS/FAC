### WIP Readme
`cd terraform/sandbox/`
` ../../bin/ops/create_service_account.sh -o sandbox-gsa -s <firstname.lasname> -u <username>-workspace-deployer > secrets.auto.tfvars`
The script will output the `username` (as `cf_user`) and `password` (as `cf_password`) for your `<ACCOUNT_NAME>`. Read more in the [cloud.gov service account documentation](https://cloud.gov/docs/services/cloud-gov-service-account/).

`cf create-service s3 basic workspace-terraform-state`
`cf create-service-key <key-name> workspace-terraform-state`
`cf service-key workspace-terraform-state <key-name>`
Copy `access_key_id`, `secret_access_key`, `bucket`, `region` and `endpoint` values into `shared/condig/sandbox.tfvars`

Make sure to have CF CLI on WSL2 Ubuntu
```
# ...first add the Cloud Foundry Foundation public key and package repository to your system
wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -
echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list
# ...then, update your local package index, then finally install the cf CLI
sudo apt-get update
sudo apt-get install cf8-cli
```


Pre-Req for proxy:
1. You must navigate to /terraform/shared/modules/https-proxy, run `terraform init` and `terraform plan` in order to generate a `proxy.zip` for the module to have a reference on what it will use as source for the app when it attempts to deploy

Security Groups:
```
cf bind-security-group public_networks_egress <ORGNAME> --lifecycle running --space <SPACENAME>
cf bind-security-group trusted_local_networks_egress <ORGNAME> --lifecycle running --space <SPACENAME>
cf bind-security-group trusted_local_networks <ORGNAME> --lifecycle running --space <SPACENAME>
```

Getting it to run the first time:
```terraform
#### ClamAV ####
# terraform\shared\modules\sandbox\clamav.tf
#proxy_server   = module.https-proxy.domain
#proxy_port     = module.https-proxy.port
#proxy_username = module.https-proxy.username
#proxy_password = module.https-proxy.password
depends_on = [module.fac-app.app_id]

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
