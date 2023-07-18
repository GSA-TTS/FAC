# Management environment

The "management" is a "meta" configuration, in that it specifies
configuration pertaining to spaces and users across environments. In an
initial bring-up/contingency recovery situation, this is the first environment
to apply.

Among other things, this module...
- ~~configures the spaces for dev, staging, and production~~ 
  - _See https://github.com/cloudfoundry-community/terraform-provider-cloudfoundry/issues/436_
- configures user access to those spaces
- ~~configures application security groups (ASGs) for the spaces~~
  - _See https://github.com/cloudfoundry-community/terraform-provider-cloudfoundry/issues/405_
- ensures the production space does not have SSH enabled
- (future) sets up egress spaces and proxy configuration
- (future) sets up log drains
- (future) sets up backup/restore of content across environments

NOTE: The deploying account must have the OrgManager role in the target
organization.

