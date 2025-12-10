# Meta environment

The meta module is responsible for all environments configuration and common files. Any file with `-managed.tf` is a file managed by this module, and should not be changed manually. All changes should be done by changing the template, creating a backup of the `terraform.tfstate.meta`, running `terraform init`, `terraform plan`, and `terraform apply` to generate the local files, create a `pull request`, and merge into `main` before any other `pull requests` can merge, as doing so will cause issues with the terraform state, since the merge that does not have the new files will overwrite the updated `terraform.tfstate.meta`.

In the use case of updating a provider version, we want to go into `meta/bootstrap-env/templates/providers.tf-template` and make the change there, and when we run a `terraform plan` on meta locally, doing so will use the `meta/bootstrap-env/modulefiles.tf` to update those files locally for all environments.

NOTE: The deploying account must have the OrgManager role in the target organization.

## Updating shared files
In order to update the providers.tf across all environments, we do not want to update them manually in each. Inside `terraform/meta/bootstrap-env/templates/` we have a list of files that serve as the common templates. Update those according to your changes, and then navigate to `terraform/meta/` and run `python update-managed-files.py`. This will update the shared files across all environments like so:
```
$ python update-managed-files.py
Updated sandbox/providers-managed.tf
Updated sandbox/variables-managed.tf
Updated preview/providers-managed.tf
Updated preview/variables-managed.tf
Updated dev/providers-managed.tf
Updated dev/variables-managed.tf
Updated staging/providers-managed.tf
Updated staging/variables-managed.tf
Updated production/providers-managed.tf
Updated production/variables-managed.tf
```
We include an `excluded_templates = ["main.tf-template", "init.sh-template"]` list, as these two files are not updated regularly. If they need to be updated, they can be removed from the excluded templates.
