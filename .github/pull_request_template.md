
## PR checklist: submitters

- [ ]   Link to an issue if possible. If there’s no issue, describe what your branch does. Even if there is an issue, a brief description in the PR is still useful.
- [ ]   List any special steps reviewers have to follow to test the PR. For example, adding a local environment variable, creating a local test file, etc.
- [ ]   For extra credit, submit a screen recording like [this one](https://github.com/GSA-TTS/FAC/pull/1821).
- [ ]   Make sure you’ve merged `main` into your branch shortly before creating the PR. (You should also be merging `main` into your branch regularly during development.)
- [ ]   Make sure that whatever feature you’re adding has tests that cover the feature. This includes test coverage to make sure that the previous workflow still works, if applicable.
- [ ]   Do manual testing locally. Our tests are not good enough yet to allow us to skip this step.
- [ ]   Verify that no Git surgery was necessary, or, if it was necessary at any point, repeat the testing after it’s finished.
- [ ]   Once a PR is merged, keep an eye on it until it’s deployed to dev, and do enough testing on dev to verify that it deployed successfully, the feature works as expected, and the happy path for the broad feature area (such as submission) still works.

## PR checklist: reviewers

- [ ]   Pull the branch to your local environment and run `make docker clean; make docker-first-run && docker compose up`; then run `docker compose exec web /bin/bash -c "python manage.py test"`
- [ ]   Manually test out the changes locally.
- [ ]   Check that the PR has appropriate tests. Look out for changes in HTML/JS/JSON Schema logic that may need to be captured in Python tests even though the logic isn’t in Python.
- [ ]   Verify that no Git surgery is necessary at any point (such as during a merge party), or, if it was, repeat the testing after it’s finished.
        
The larger the PR, the stricter we should be about these points.
