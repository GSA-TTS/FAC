### Make sure to have CF CLI on WSL2 Ubuntu
```
# ...first add the Cloud Foundry Foundation public key and package repository to your system
wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -
echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list
# ...then, update your local package index, then finally install the cf CLI
sudo apt-get update
sudo apt-get install cf8-cli
```

### Create a deployer account
If a deployer account has not been created, then simply run the following:
```
cd terraform/sandbox
../../bin/ops/create_service_account.sh -o gsa-tts-oros-fac -s sandbox -u sandbox-deployer >> secrets.auto.tfvars
```
This will create a `secrets.auto.tfvars` in the directory for use with terraform.

In the event that a deployer account has already been created:
```
cd terraform/sandbox
../../bin/ops/get_service_account.sh -o gsa-tts-oros-fac -s sandbox -u sandbox-deployer >> secrets.auto.tfvars
```
This will update a `secrets.auto.tfvars` in the directory for use with terraform.

### Give the deployer account permissions in the ${ENV}-egress space
You must have a role of SpaceManager to assign the deployer service account. Ask Alex, Bret or Matt to do this for you (but the assumption is it will be done for you. The space will only have this service account and will not need to be done more than once, unless the account gets deleted from the sandbox space)
```
cf space-users gsa-tts-oros-fac sandbox
cf set-space-role <uaa_unique_id> gsa-tts-oros-fac sandbox-egress SpaceDeveloper
```

### ASGS
Since we do not rely on the github meta workflow (yet) to handle ASGS, we must explictly ensure they are there. This operation will only need to be done once, but documenting for documentation purposes.

Security Groups:
```
cf bind-security-group trusted_local_networks gsa-tts-oros-fac --lifecycle running --space sandbox
cf bind-security-group trusted_local_networks_egress gsa-tts-oros-fac --lifecycle running --space sandbox

cf bind-security-group public_networks_egress gsa-tts-oros-fac --lifecycle running --space sandbox-egress
```

### Pre-Configuration
Navigate to the following folders in cli:
`terraform/shared/modules/sandbox-proxy` & `terraform/shared/modules/stream-proxy`
Run the following commands to generate a local `proxy.zip` so the module is able to see the zip artifact to deploy the applications with
```
terraform init \
  --backend-config=../shared/config/sandbox.tfvars

terraform plan \
  --backend-config=../shared/config/sandbox.tfvars
```

### First Deployment
Navigate to `terraform/sandbox` and run the `./init.sh` script. This assumes you have a `sandbox.tfvars` in `terraform/shared/config/`. Below is an example of values that will need to have values inside the file:
```
branch_name             = "" # There is no default branch. This value should be the name of your branch. (ex <initials>/<feature> [as/terraform-work])
new_relic_license_key   = ""
pgrst_jwt_secret        = ""
sam_api_key             = ""
login_client_id         = ""
login_secret_key        = ""
django_secret_login_key = ""
```

Next, run `./plan.sh` script. You should see it creating ~20 resources.
Finally, run `./apply.sh` script and wait.
