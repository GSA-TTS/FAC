---
name: Story issue template
about: Starting point for new stories
title: 'clear, concise summary'
labels: ''
assignees: ''
---

# At a glance

[comment]: # "Begin with a short summary so intent can be understood at a glance."

[comment]: # "In order to: some objective or value to be achieved"
[comment]: # "as a: stakeholder"
[comment]: # "I want: some new feature"

**In order to** 
**as a**
**I want**

# Acceptance Criteria

We use [DRY](https://docs.behat.org/en/latest/user_guide/writing_scenarios.html#backgrounds) [behavior-driven development](https://en.wikipedia.org/wiki/Behavior-driven_development#Behavioral_specifications) wherever possible.

[comment]: # "ACs should be clearly demoable/verifiable whenever possible."
[comment]: # "Given: the initial context at the beginning of the scenario"
[comment]: # "when: the event that triggers the scenario"
[comment]: # "then: the expected outcome(s)"
[comment]: # "Repeat scenarios as needed, or repeat behaviors and lists within a scenario as needed."

[comment]: # "The scenario should be a short, plain language description."
[comment]: # "Feeling repetative? Apply the DRY (Don't Repeat Yourself) principle!"

### Scenario: 

**Given**   
**when**  
...

[comment]: # "Each task should be a verifiable outcome"
```[tasklist]
### then... 
- [ ] 
```

### Shepherd

[comment]: # "@ mention shepherds as we move across the board."

* Design shepherd: 
* Engineering shepherd: 

# Background

[comment]: # "Any helpful contextual notes or links to artifacts/evidence, if needed"

# Security Considerations

Required per [CM-4](https://nvd.nist.gov/800-53/Rev4/control/CM-4).

[comment]: # "Our SSP says 'The team ensures security implications are considered as part of the agile requirements refinement process by including a section in the issue template used as a basis for new work.'"
[comment]: # "Please do not remove this section without care."
[comment]: # "Note any security concerns that might be implicated in the change. 'None' is OK, but we must be explicit here."

# Sketch

We're thinking we'll try implementing A and then changing B.

```[tasklist]
# Tasks
- [ ] 
```

---

<details>
  <summary>Process checklist</summary>
  
# Sketch

[comment]: # "Notes or a checklist reflecting our understanding of the selected approach"

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
- [ ] A design shepherd has been identified

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
- [ ] An engineering shepherd has been identified

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

</details>
