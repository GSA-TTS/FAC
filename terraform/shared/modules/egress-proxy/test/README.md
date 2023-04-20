# Test the egress-proxy module
1. Authenticate with cloud.gov (`cf login -a api.fr.cloud.gov --sso`)
2. Copy `terraform.tfvars-template` to `terraform.tfvars` and edit to taste
3. Run `terraform apply` to deploy a test fixture app and the proxy
4. Verify success
5. Run `terraform destroy` to tear everything down