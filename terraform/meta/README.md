# Meta environment

The "meta" module applies configuration pertaining to spaces and users across
environments. In an initial bring-up or contingency recovery situation:
1. run `./bootstrap.sh`
1. run `./init.sh`

After that you should be able to run `terraform apply` whenever needed.

Among other things, this module...
- configures the spaces for dev, staging, and production
  - _See https://github.com/cloudfoundry-community/terraform-provider-cloudfoundry/issues/436_
- configures user access to those spaces
- configures application security groups (ASGs) for the spaces
  - _See https://github.com/cloudfoundry-community/terraform-provider-cloudfoundry/issues/405_
- ensures the production space does not have SSH enabled
- (future) sets up the deployer cred secrets in the corresponding GitHub environment
- (future) sets up egress spaces and proxy configuration
- (future) sets up log drains
- (future) sets up backup/restore of content across environments

NOTE: The deploying account must have the OrgManager role in the target
organization.


## TODO: 

* Make bootstrap.sh script
  * Checks that the user is logged into GitHub as repo admin and Cloud Foundry as OrgAdmin
  * Runs Terraform with the "bootstrap" sub-module that...
    * creates the "meta" space and backend S3 instance+key
    * populates S3 creds as repo secrets
    * if specified, populates shared/config/backend.tfvars
  * Try to make this idempotent!
  * Try to make this invokable via a GitHub workflow!
* Move the services currently in "management" into the "meta" space; we're not really using that space anyway
* Double-check that the "management" space can be blown away (first confirming that the *actual* Terraform state is in the S3 instance in the "production" space)
* Update/simplify ../terraform/README.md!
