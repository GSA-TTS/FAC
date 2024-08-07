
## PR Checklist: Submitter

- [ ]   Link to an issue if possible. If there’s no issue, describe what your branch does. Even if there is an issue, a brief description in the PR is still useful.
- [ ]   List any special steps reviewers have to follow to test the PR. For example, adding a local environment variable, creating a local test file, etc.
- [ ]   For extra credit, submit a screen recording like [this one](https://github.com/GSA-TTS/FAC/pull/1821).
- [ ]   Make sure you’ve merged `main` into your branch shortly before creating the PR. (You should also be merging `main` into your branch regularly during development.)
- [ ]   Make sure you’ve accounted for any migrations. When you’re about to create the PR, bring up the application locally and then run `git status | grep migrations`. If there are any results, you probably need to add them to the branch for the PR. Your PR should have only **one** new migration file for each of the component apps, except in rare circumstances; you may need to delete some and re-run `python manage.py makemigrations` to reduce the number to one. (Also, unless in exceptional circumstances, your PR should not delete any migration files.)
- [ ]   Make sure that whatever feature you’re adding has tests that cover the feature. This includes test coverage to make sure that the previous workflow still works, if applicable.
- [ ]   Make sure the full-submission.cy.js [Cypress test](https://github.com/GSA-TTS/FAC/blob/main/docs/testing.md#end-to-end-testing) passes, if applicable.
- [ ]   Do manual testing locally. Our tests are not good enough yet to allow us to skip this step. If that’s not applicable for some reason, check this box.
- [ ]   Verify that no Git surgery was necessary, or, if it was necessary at any point, repeat the testing after it’s finished.
- [ ]   Once a PR is merged, keep an eye on it until it’s deployed to dev, and do enough testing on dev to verify that it deployed successfully, the feature works as expected, and the happy path for the broad feature area (such as submission) still works.
- [ ]   Ensure that prior to merging, the working branch is up to date with main and the terraform plan is what you expect.

## PR Checklist: Reviewer

- [ ]   Pull the branch to your local environment and run `make docker-clean; make docker-first-run && docker compose up`; then run `docker compose exec web /bin/bash -c "python manage.py test"`
- [ ]   Manually test out the changes locally, or check this box to verify that it wasn’t applicable in this case.
- [ ]   Check that the PR has appropriate tests. Look out for changes in HTML/JS/JSON Schema logic that may need to be captured in Python tests even though the logic isn’t in Python.
- [ ]   Verify that no Git surgery is necessary at any point (such as during a merge party), or, if it was, repeat the testing after it’s finished.

The larger the PR, the stricter we should be about these points.

## Pre Merge Checklist: Merger

- [ ]   Ensure that prior to approving, the terraform plan is what we expect it to be. `-/+ resource "null_resource" "cors_header" ` should be destroying and recreating its self and ` ~ resource "cloudfoundry_app" "clamav_api" ` might be updating its `sha256` for the `fac-file-scanner` and `fac-av-${ENV}` by default.
- [ ]   Ensure that the branch is up to date with `main`.
- [ ]   Ensure that a terraform plan has been recently generated for the pull request.
