---
name: Story issue template
about: Starting point for new stories
title: '[distinguishable summary]'
labels: ''
assignees: ''
---
# User Story

In order to [goal], [stakeholder] wants [change].

# Acceptance Criteria

[ACs should be clearly demoable/verifiable whenever possible. Try specifying them using [BDD](https://en.wikipedia.org/wiki/Behavior-driven_development#Behavioral_specifications).]

- [ ] GIVEN [a contextual precondition] \
  [AND optionally another precondition] \
  WHEN [a triggering event] happens \
  THEN [a verifiable outcome] \
  [AND optionally another verifiable outcome]

# Background

[Any helpful contextual notes or links to artifacts/evidence, if needed]

---

# Security Considerations ([required](https://nvd.nist.gov/800-53/Rev4/control/CM-4))

[comment]: # "Our SSP says 'The Data.gov team ensures security implications are considered as part of the agile requirements refinement process by including a section in the issue template used as a basis for new work.' so please don't remove this section without care."
[Any security concerns that might be implicated in the change. "None" is OK, just be explicit here!]

# Sketch

[Notes or a checklist reflecting our understanding of the selected approach]

- [ ] Design designs all the things
- [ ] Engineering engineers all the things

# Definition of Done

## Triage

### If not likely to be important in the next quarter...
- [ ] Archived from the board

### Otherwise...

- [ ] Has a clear story statement
- [ ] Design or Engineering accepts that it belongs in their respective backlog

## Design Backlog

- [ ] Has clearly stated/testable acceptance criteria
- [ ] Meets the design Definition of Ready [citation needed]

## Design In Progress

- [ ] Meets the design Definition of Done [citation needed]

## Design Review Needed

- [ ] Necessary outside review/sign-off was provided

## Design Done

- [ ] Presented in a sprint review
- [ ] Includes screenshots or references to artifacts

### If no engineering is necessary
- [ ] Tagged with the sprint where it was finished
- [ ] Archived

## Engineering Backlog

- [ ] Has clearly stated/testable acceptance criteria
- [ ] Has a sketch or list of tasks
- [ ] Can reasonably be done in a few days (otherwise, split this up!)

## Engineering Available

- [ ] There's capacity in the `In Progress` column

## Engineering In Progress

- [ ] Meets acceptance criteria
- [ ] Meets [QASP conditions](https://derisking-guide.18f.gov/qasp/)

### If there's UI...
- [ ] Screen reader - Listen to the experience with a screen reader extension, ensure the information presented in order
- [ ] Keyboard navigation - Run through acceptance criteria with keyboard tabs, ensure it works. 
- [ ] Text scaling - Adjust viewport to 1280 pixels wide and zoom to 200%, ensure everything renders as expected. Document 400% zoom issues with USWDS if appropriate.

## Engineering Blocked

- [ ] Blocker removed/resolved

## Engineering Review Needed

- [ ] Outside review/sign-off was provided

## Engineering Done

- [ ] Presented in a sprint review
- [ ] Includes screenshots or references to artifacts
- [ ] Tagged with the sprint where it was finished
- [ ] Archived

