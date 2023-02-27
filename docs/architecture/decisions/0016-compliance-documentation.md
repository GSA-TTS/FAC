# 16. How to document compliance work

Date: 2023-02-27

## Status

Accepted

## Context

Compliance documentation is an essential component of working in the open while providing clear and obvious evidence of security considerations, concerns, and mitigations.

The [prior decision](https://github.com/GSA-TTS/FAC/blob/main/docs/architecture/decisions/0009-compliance-documentation.md) to use [OSCAL](https://pages.nist.gov/OSCAL/) with [Trestle](https://github.com/IBM/compliance-trestle) isn’t practical given personnel considerations.

## Decision

We will use spreadsheets and other documentation to track the compliance work.

We will continue to [generate diagrams with PlantUML](https://github.com/GSA-TTS/FAC/blob/main/docs/architecture/decisions/0002-c4-plantuml-diagrams.md).

## Considerations:

*   Lack of familiarity of team personnel with OSCAL/Trestle.
*   Reduction of technical maintenance—existing code in `compliance` was generating `dependabot` issues.
*   Concerns that OSCAL/Trestle does not fully match GSA’s ATO processes.

## Consequences

*   ATO documentation will need to be tracked using documents/spreadsheets, requiring manual coordination.
*   We will remove the `/compliance` directory from `main`.
