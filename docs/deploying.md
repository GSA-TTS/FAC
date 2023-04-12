# Deploying

We use [cloud.gov](https://cloud.gov/) as our PaaS to provide application hosting as well as broker for Postgres and S3 instances from AWS.

We use [Terraform](https://github.com/GSA-TTS/FAC/tree/main/terraform) to configure the services and permissions for our cloud.gov environments.

We use [manifests](https://docs.cloudfoundry.org/devguide/deploy-apps/manifest.html) to configure and push our applications to cloud.gov

## Contents

- [Deploying](#deploying)
  - [Contents](#contents)
  - [Tools](#tools)
  - [Cloud.gov](#cloudgov)
  - [Initial Setup](#initial-setup)
  - [Deploying Manually](#deploying-manually)
  - [Deploying Automatically](#deploying-automatically)
  - [Troubleshooting](#troubleshooting)

## Tools

- [cf-cli](https://docs.cloudfoundry.org/cf-cli/) Cloudfoundry's CLI
  - Mac install of v8 needed for Cloud.gov: `brew install cloudfoundry/tap/cf-cli@8`
- [cloud.gov dashboard](https://www.cloud.gov)
- [cloud.gov deploy action](https://github.com/18F/cg-deploy-action)
- [application logs](https://logs.fr.cloud.gov/) with search and dashboard

## Cloud.gov

- Organization: `gsa-tts-oros-fac`
- Spaces: `dev`, `staging`, `production`

- Apps: gsa-fac
    - Manifests: [/backend/manifests](../backend/manifests)
    - route: [fac-dev.app.cloud.gov](https://fac-dev.app.cloud.gov)

## Initial Setup

To provision services in an otherwise empty space within cloud.gov, [add a new module for that space to the Terraform directory](https://github.com/GSA-TTS/FAC/tree/main/terraform#structure).

## Deploying Manually

This should not be necessary, and should only be done as part of troubleshooting or in case of issues with our GitHub deployment process.

After you've authenticated and targeted the desired org/space, push the application with

```shell
# Push the development app using `dev manifest
cf push -f manifests/manifest-dev.yml
```

## Deploying Automatically

* When code is pushed to `main`, it's deployed to the development space
* When code is pushed to `prod`, it's pushed to the staging space
* When code is [tagged with a tag starting with `v`](https://github.com/GSA-TTS/FAC/blob/main/docs/branching.md#steps), it's pushed to the production space

### Standard deployment process

#### Deploying to `dev`

1.  Create your branch; we often use `[name-or-initials]/[issue-number]-[description]` as the naming convention, for example `tadhg/docs-deployment-tweaks`.
2.  Create a pull request and add any notes a reviewer might need. Anyone on the development team can review, but you may wish to request review from specific team members.
3.  If any of the checks fail, resolve those problems.
3.  Make any requested changes/resolve any discussion.
4.  Either the reviewer or the submitter can merge the approved pull request.
    *   On merging **to `main` only**, we tend to use “squash and merge” to keep the history of `main` relatively clean.
5.  Verify that the deploy steps all passed.
6.  After deployment, the changes should be on https://fac-dev.app.cloud.gov/.

#### Deploying to `staging`

1.  Create a pull request using `main` targeting `prod`
    *   In the GitHub interface, this will mean setting **base** to `prod` and **compare** to `main`.
    *   The title of the pull request should start with `[YYYY-MM-DD]` and indicate that it’s a merge from `main` to `prod`, for example `2023-04-03 main -> prod`.
2.  Request reviewers.
3.  Wait for the checks to pass.
4.  If checks fail, or if reviewers request changes, something has gone awry. Investigation and/or starting over from a branch and making a PR against `main` may be required.
5.  A member of the [FAC admins team](https://github.com/orgs/GSA-TTS/teams/fac-admins) has to merge the pull request.
    *   Only use “merge pull request” here—_do not use “squash and merge” or “rebase and merge”_ as that will cause `main` and `prod` diverge in Git history terms.
5.  Verify that the deploy steps all passed.
6.  After deployment, the changes should be on https://fac-staging.app.cloud.gov/.

#### Deploying to `production`

1.  Create a [new release](https://github.com/GSA-TTS/FAC/releases/new).
    *   Create a new tag in the form `v1.[YYYYMMDD]` with the current date, such as `v1.20230329`, and use that as the tag for the release.
    *   **_Remember to set the target to `prod`_**.
    *   For the moment, check the “Set as a pre-release” checkbox. We may change this close to or after MVP.
3.  Wait for the checks to pass.
4.  If checks fail, or if reviewers request changes, something has gone awry. Investigation and/or starting over from a branch and making a PR against `main` may be required.
5.  Verify that the deploy steps all passed.
6.  After deployment, the changes should be on https://fac-prod.app.cloud.gov/.
7.  If anything was merged directly into the `prod` branch, such as a hotfix, merge `prod` back into `main`.

To see more about branching and the deployment steps, see the [Branching](branching.md) page.

## Running a Django admin command

You can SSH into a running instance of the app. Running Django apps is a little more complicated on Cloud Foundry than running locally.

Don't forget to change the organization or space you need first with `cf target -o your_org_name` or `cf target -s your_space_name`

```shell
cf ssh {APP NAME}
cd app
export LD_LIBRARY_PATH=~/deps/0/python/lib
~/deps/0/python/bin/python manage.py {COMMAND WITH ARGS}
```

## Troubleshooting

### Problem: A GitHub Action run says that Terraform cannot be applied because the plan differs from what was approved.
#### Solution: Click through from the error message to the referenced PR, click the `Checks` tab, and rerun the Terraform plan action. Then rerun the action that failed originally.
More info: When there are changes to the `terraform/` directory in a PR, [a GitHub Action](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/terraform-plan.yml) posts comments to the PR which include the "plan" indicating what will change in each environment when the PR is deployed there. ([example](https://github.com/GSA-TTS/FAC/pull/875)) Those comments help those reviewing and approving the PR to understand the implication of the change. 

However, we don't deploy immediately to the `staging` and `production` environments, and it's possible that other PRs will get merged, or that someone will make manual changes in those environments in the meantime. As a sanity check the plan is regenerated right before applying a change in those environments. If there's any difference from what was approved in the PR (captured in those comments), it's an indicator that the approved plan is **not** what is about to happen, and the action aborts so that humans can inspect and intervene if necessary. The simplest way to say "yeah, I want the new plan to happen, that's still OK" is to go regenerate the plans being compared against in the PR, using the steps indicated.

For more about how all this works, see [the `dflook/terraform-github-actions` documentation](https://github.com/dflook/terraform-github-actions), particularly [the `terraform-apply` action](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply).
