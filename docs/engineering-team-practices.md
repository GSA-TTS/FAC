# Engineering Team Practices

This is a place to jot down our decisions around engineering team workflow. It's a living document subject to change as the codebase and team grows.

### Contents
- [Principles](#principles)
- [Pull Requests and Code Reviews](#pull-requests-and-code-reviews)

## Principles

* We'll follow the methods and recommendations outlined in the [TTS Engineering Practices Guide](https://engineering.18f.gov/). Where we deviate from `Requirements`, `Standards`, or `Defaults`, we'll document our decisions, surrounding context, and reasoning.

* Simple is better than complex.

## Pull Requests and Code Reviews

- We strive to keep pull requests as small as possible, but realize this can be hard with greenfield projects. Small pull requests are easier to review and lead to more frequent merges.

- When reviewing a PR, be explicit about whether a comment is blocking or non-blocking, an issue or a suggestion, etc, in the vein of [conventional comments syntax](https://conventionalcomments.org/).

## Django conventions

* We strive for idiomatic Django implementations leveraging existing work where ever possible. In practice this means:
  * If there is an existing pattern in the Django documentation we use it.
  * Where there is not, we look to existing and tested patterns within TTS and the broader Django community.

* We rename our migrations to be descriptive and reflect the actions within.
