## PR Checklist: Submitter

-  Link to an issue if possible. If there’s no issue, describe what your branch does. Even if there is an issue, a brief description in the PR is still useful.
-  List any special steps reviewers have to follow to test the PR. For example, adding a local environment variable, creating a local test file, etc.
-  For extra credit, submit a screen recording like [this one](https://github.com/GSA-TTS/FAC/pull/1821).
-  Make sure you’ve merged `main` into your branch shortly before creating the PR. A PR check will alert you if your branch is out of date with main and will prevent you from merging it.
-  Make sure you’ve accounted for migrations if you've modified any Django models. Your PR should have only **one** new migration file for each of the component apps, except in rare circumstances; you may need to delete some and re-run `python manage.py makemigrations` to reduce the number to one. A PR check is in place that *should* alert you if a migration file is missing.
-  Make sure that whatever feature you’re adding has tests that cover the feature. This includes test coverage to make sure that the previous workflow still works, if applicable.
-  Make sure the full-submission.cy.js [Cypress test](https://github.com/GSA-TTS/FAC/blob/main/docs/testing.md#end-to-end-testing) passes, if applicable. This is automatically run in the PR checks. If an unexpected failure occurs, it's probably worthwhile to just rerun it first, as it can be flaky.
-  The unit tests should pass. This is also run by the PR checks, but you can run it yourself within `/backend` via `docker compose exec web /bin/bash -c "python manage.py test"`. They take a long time.
-  Do manual testing locally.
-  Verify that no Git surgery was necessary, or, if it was necessary at any point, repeat the testing after it’s finished.
-  On Github, you can head to Actions and run "Deploy to the Preview Environment" to allow anyone with the preview link (https://fac-preview.app.cloud.gov/) to test your changes.
-  Once a PR is merged, keep an eye on it until it’s deployed to dev, and do enough testing on dev to verify that it deployed successfully, the feature works as expected, and the happy path for the broad feature area (such as submission) still works.

## PR Checklist: Reviewer

-  Pull the branch to your local environment
-  Run the app. If it was already running locally, usually the hot reloading will be sufficient. If not, stop all containers and use these:
  - If you need to wipe all data: `make docker-clean`
  - If there are migrations involved: `make docker-first-run && docker compose up`
  - Otherwise, just `docker compose up`
-  Manually test out the changes locally.
-  Check that the PR has appropriate tests. Look out for changes in HTML/JS/JSON Schema logic that may need to be captured in Python tests even though the logic isn’t in Python.
-  Repeating testing is encouraged if the branch needs to be caught up with main before it can be merged.
