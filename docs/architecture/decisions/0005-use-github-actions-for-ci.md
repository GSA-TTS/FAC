# 5. Use Github Actions for CI

Date: 2022-04-12

## Status
Accepted

## Context
"A Continuous Deployment service allows a development team to receive rapid feedback on new features or bug fixes. CD also helps ensure deployment and infrastructure issues are identified earlier in a release process, and are scoped to a smaller number of changes." —[TTS Engineering Practices Guide](https://engineering.18f.gov/project-setup/#continuous-integrationcontinuous-deployment)

Our architecture calls for a CI/CD service with Github integration which can be used with this current repository to execute one or more test suites as well as deploy to cloud.gov, among other things.

## Decision
There are two main options as recommended by the [TTS Engineering Practices Guide](https://engineering.18f.gov/project-setup/#continuous-integrationcontinuous-deployment):
* [CircleCI](https://circleci.com/) [default]
* [Github Actions](https://github.com/features/actions) [suggestion]

Both options provide adequate coverage, the ability to integrate with cloud.gov for deployment, and have been used successfully in other TTS projects.

Finding no issues with either option and opting to stick with Github-native workflows:

**We will use [Github Actions](https://github.com/features/actions) for CI**

## Consequences

* We'll follow TTS and GSA guides and standards in implementing CI/CD workflows.
* We'll implement testing as part of the CI pipeline and prevent merging until the test suite passes.
* We'll block merging to main on passing tests and a successful build.
* We'll automatically deploy the latest passing build to cloud.gov
* We'll continue to build out CI as we add linting, security scanning, accessibility scanning, etc.
