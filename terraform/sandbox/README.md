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

In order to get the app to even attempt to startup, we have to disable collectstatic on the droplet.
1. In **terminal 1**, generate your plan with `./plan.sh`
2. In **terminal 1** type `./apply.sh` **but do not run**
3. In **terminal 2** paste `cf set-env gsa-fac DISABLE_COLLECTSTATIC 1`
4. In **terminal 1** press enter and run the apply
5. Wait until terminal **1** says `module.sandbox.module.fac-app.cloudfoundry_app.fac_app: Creating...` in the output, and then press enter in **terminal 2**
