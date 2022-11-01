# 12. Switch to a unified Django web application architecture

Date: 2022-10-28

## Status

Accepted

## Context

The original decision to split the submission side of the application into a statically-generated frontend site and a backend API rested on some assumptions:

*   The frontend would not need to track anything beyond very simple state:
    *   The user flow through the form would be almost entirely linear.
    *   The form logic would not contain many branching paths involving dependencies between different sections of the form.
    *   Form variation would be limited enough to allow static generation to reasonably cover all required permutations.
    *   Functionality specific to individual user roles would not introduce significant complexity.
*   An API for submissions was an overall priority.

These three key findings from the [auditee user research](https://docs.google.com/presentation/d/1NHdDjMgkirOteJoAG3ClgSs_V98c9svQ2MK25s5UU6Q/edit#slide=id.g16c6a44ada3_0_18) show a need for keeping track of state at the user level:

1.  Give users a clear overview of what the submission process entails, and show them how they are progressing through the process at every step.
2.  Make it clear who is responsible for each process step; guide users to the actions they need to complete and show them which actions need to be completed by someone else.
3.  Give users more feedback on whether they’re doing things right; confirm when a step is completed and tell them what to expect next.

These research findings are all difficult to support while keeping minimal frontend state, and every set of user needs prior to this also added more complexity to the state the application needed to keep track of.

In addition, the separation into distinct frontend and backend applications:

*   Made multi-tab support difficult/impossible due to how maintaining authenticated sessions worked.
*   Meant we had to use query parameters instead of nice URLs.
*   Meant the team was at times struggling to work as a single unit due to the separation.
*   Already required the addition of frontend libraries (`alpine.js` and `is-land`) to support the increased complexity.

It was apparent that we were pushing up against the limitations of the separated approach even before the user research indicated the need for more complex state handling.

Lastly, while ultimately supporting an API-centric path for the submission of single audits remains a goal, it cannot be considered a priority under the current circumstances. There is no current demand among submitters for this, and the deadline means that supporting the interactive submission path must be the priority.

## Decision

We will move the current frontend into Django, use Django to manage state, add whatever rich interaction we need to via as-yet-undetermined JavaScript frameworks, and continue to use USWDS styling and components. This also means we will move to a single repository, something that was already looking likely regardless of this decision.

## Considerations

*   We need to prioritize development speed, and therefore simplicity of development environment. When the frontend required less state management, the approach of having two separate environments, both relatively simple, was feasible. But once one or both of them hit a certain point, the difficulty of managing synchronization between the environments became an impediment.
*   Making the change sooner rather than later means less work to potentially re-do.
*   Making the change sooner rather than later means a better chance of having the new architecture settled enough for ease of vendor onboarding, which may be happening soon.

## Consequences

*   Better long-term outlook.
*   Redoing a lot of the frontend work to use Django templates and views.
*   Revisiting authentication flow / Login.gov integration (will move from PKCE flow to private_key_jwt).
*   Django learning for a lot of the team.
*   Feature work delayed as we make the move.

## Updated system diagram

![image](https://raw.githubusercontent.com/GSA-TTS/FAC/main/docs/architecture/diagrams/FAC_System_Context_unified.png)
