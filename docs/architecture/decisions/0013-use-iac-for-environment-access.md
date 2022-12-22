# 13. Use Infrastructure-as-Code (IaC) for environment access

Date: 2022-12-09

## Status

Accepted

## Context

We need to have well-defined, well-documented processes for controlling access to the  FAC spaces in cloud.gov. 

## Decision

We are using Terraform HCL code to manage the set of cloud.gov spaces and who has which permissions in them. [This code is tracked and versioned as part of the FAC GitHub repository.](https://github.com/GSA-TTS/FAC/tree/main/terraform/management/config.tf) Changes are made effective whenever this file changes on the `main` branch.

Changes to the file are required to be reviewed by a member of [the GitHub @GSA-TTS/FAC-admins team](https://github.com/orgs/GSA-TTS/teams/fac-admins/members) before they land on `main`. This requirement is implemented by [requiring pull requests to be reviewed by code owners](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches#require-pull-request-reviews-before-merging), using branch protection rules on `main` and `prod`. The [`CODEOWNERS` file](https://github.com/GSA-TTS/FAC/tree/main/.github/CODEOWNERS) includes a line specifying that the code in the `terraform/management` directory is owned by the `@GSA-TTS/FAC-admins` team.

Who administers the administrators? Another line in the files enforces that changes to the `CODEOWNERS` file itself are also required to be reviewed by the current membership of that team.

## Considerations

The process needs to be structured, well-documented, and auditable for compliance purposes, particularly for the [NIST AC control family](https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search#/controls/?version=latest&family=AC).

## Consequences

* Clear, self-service onboarding process.
* Clear offboarding process.
* Audit trail available.
* People can come and go without the process changing.
* Single-sources environment access approvals with repository access approvals.

