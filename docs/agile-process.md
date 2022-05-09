Agile Process
===================

# Overview

There is a [high-level roadmap](https://app.mural.co/t/gsa6/m/gsa6/1646336450605/6a77a27a287989f91e1c0dfbcf9be4dec6e49393?sender=ua4d37dfba3f1e69e09078790) that the product and design team distills down to actionable tasks at the beginning of each sprint. Design, engineering and product work is tracked on the [FAC Task Tracking board](https://github.com/GSA-TTS/FAC/projects/1) in Github. "Story" issues can be created to define a high-level piece of functionality, but linked subtasks should be created for discrete pieces of work across disciplines, each not exceeding one day in anticipated time. There is no estimation process for tickets, but they should be refined to be in approximately comparable sizes. The team works in two-week sprints starting on Tuesdays.

### Board workflow

- **Backlog** - Not currently selected for the current sprint

- **Available** - Selected for the current sprint and is currently available to be picked up.

- **In progress** - Someone is actively working on this

- **Blocked** - If you put an issue here, please explain why it is stuck.

- **In review** - There is code review or QA happening on this feature

- **Done (Sprint X)** - The path to "Done" varies by issue type:

    - **User Story** - Acceptance criteria for a task is verified by PM or QA lead on the development instance, then moved to done. 

    - **Engineering task** - Acceptance criteria is verified by an engineer on the development instance, then moved to done. 

    - **Design task** - PM verifies the process for next steps / implementation is documented in another ticket, then moved to done. 

    - **Product task** - PM asks relevant parties (design, engineering, etc) to review and move to done.  

Note: Sprint-specific "done" columns are used to track exactly what was completed in a current sprint for velocity / reporting purposes.

### How we'll stay on track

Time-based estimations are prone to inaccuracy and preconceived notions of "how long something should take" that often doesn't consider code review, qa, deployment and bug fixes. We'll keep it real about what we can deliver by tracking a velocity metric and considering that as we plan new sprints. That said, there are very real deadlines for this project! Here is how we can work together in an agile fashion to deliver on time:

-   **Definition** - Make sure the issues we slate for a sprint are sufficiently detailed (have everything you need to start) and are sufficiently broken up (about the same size, not more than a day).

-   **Execution** - We should all test what we create to the best extent possible to avoid churn in QA and code review.

-   **Velocity** - Our team should rally around the one thing we can control - the velocity of our output as defined by the number of tickets "done" in a given sprint. This will be acknowledged in our retros and compared to previous sprints.

# Supporting Meetings and processes

### Sprint planning (Backlog->Available)

At the start of each sprint, we review the stories refined for implementation and ensure they . We aim to take on work that can be completed within one sprint. If a story seems like it'll need to span more than one sprint, that may be a sign that it needs to be broken into a smaller chunk of work.

### Code Review (In Progress->Ready For Review->Done)

Pull requests are reviewed on a per-ticket basis for merge into test. Better to push to test more rather than less; we assume test will break.

Stories are reviewed against acceptance criteria (AC) with test coverage.

Once stories are reviewed, stories are pushed to staging.

One reviewer required for any pull request (both test and staging).

Anyone can review; ad-hoc. Prefer velocity. Signal to the team in slack if you've waited more than two hours for a review.

### Backlog refinement

At the middle of each sprint we refine the backlog. Risks and dependencies are evaluated, context provided, and stories are added/removed from the backlog based on learning from the previous sprint.

Participants: PO/PM, Design Lead, and Engineering Lead

The UX team elaborates backlog stories that have been flagged for move from "backlog" to "to do."

Elaboration includes:

-   A two-sentence narrative.

-   Context

-   In/out of scope

-   Acceptance criteria

-   Latest mocks