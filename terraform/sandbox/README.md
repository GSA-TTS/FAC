### WIP Readme
`cd terraform/sandbox/`
` ../../bin/ops/create_service_account.sh -o sandbox-gsa -s <firstname.lasname> -u <username>-workspace-deployer > secrets.auto.tfvars`
The script will output the `username` (as `cf_user`) and `password` (as `cf_password`) for your `<ACCOUNT_NAME>`. Read more in the [cloud.gov service account documentation](https://cloud.gov/docs/services/cloud-gov-service-account/).

`cf create-service s3 basic workspace-terraform-state`
`cf create-service-key <key-name> workspace-terraform-state`
