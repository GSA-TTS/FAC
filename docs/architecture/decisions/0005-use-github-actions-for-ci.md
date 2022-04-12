# 5. Use Github Actions for CI

Date: 2022-04-12

## Status
Accepted

## Context
Our architecture calls for a CI/CD tool which can be used with this current repository to execute one or more test suites as well as deploy to cloud.gov, among other things.

**We will use [Github Actions](https://github.com/features/actions) for CI**

## Consequences

* We'll follow TTS and GSA guides and standards in implementing CI workflows.
* We'll implement testing as part of the CI pipeline and prevent merging until the suite passes.
* We'll block merging to main on passing tests and a successful build.
* We'll continue to build out CI as we add linting, security scanning, accessibility scanning, etc.
