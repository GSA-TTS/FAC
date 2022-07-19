Agile Process
===================

### Overview

There is a [high-level roadmap](https://github.com/GSA-TTS/FAC/blob/main/docs/product/roadmap.md) containing Milestones that the product and design team distills down to actionable tasks at the beginning of each sprint. Design, engineering and product work is tracked on the [FAC Task Tracking board](https://github.com/GSA-TTS/FAC/projects/1) in Github with corrosponding roadmap Milestones. 

### Creating issues
 
**Story** - Issues of this type define high-level pieces of functionality that may require multiple team members to implement (design, front-end, back-end engineering, etc). These currently use the "Story template". The "story" label is added to this. Often sub tasks will be created and linked from stories. The person assigned the story is considered the "shepherd" of the issue who is tasked with tying it all together.
 
**Task** - Issues of this type represents a discrete piece of functionality that should not require more than one day of work. It should use the "Basic task tracking" template that links back to the main story and has specific acceptance criteria. Tasks are given a "design" or "engineering" label.
 
**Ceremonies** - The goal is for new work from the backlog to enter the sprint at the start of the sprint and have agreement from the team that it's realistic to get the body of work done by the end of the sprint. In practice, items are sometimes removed and added to the sprint while it's ongoing. When this happens, team members are expected to communicate the up-scope or down-scope of the sprint to the rest of the team. Items that the team agrees to take on from the outset are currently given a sprint milestone, which communicates what the team anticipated was possible.
 
**Labeling issues** - In addition to the "story", "design" and "engineering" labels, the "needs refinement" label is a very important label to denote whether an issue needs to be better clarified. There are a bunch of other labels that are rarely used and could probably be deleted. These two carry special significance since we try not to actively work on an issue until these labels have been removed: 

* “Needs refinement” - need a design, engineering or product decision to move forward
* “Needs scoping” - needs people to pair up and review, then break down an issue into individual tasks.

 
**Estimation / Velocity** - There is no estimation process for tickets, but they should be refined to be in approximately comparable sizes. The team works in two-week sprints starting on Tuesdays. As of right now, our two velocity metrics are number of tasks completed and number of stories completed in a sprint tracked

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

### Quality assurance

As of the time of this writing, the product manager does the following QA on each story before moving to done: 

- [ ] Meets acceptance criteria
- [ ] Screen reader - Listen to the experience with a screen reader extension, ensure the information presented in order
- [ ] Keyboard navigation - Run through acceptance criteria with keyboard tabs, ensure it works. 
- [ ] Text scaling - Adjust viewport to 1280 pixels wide and zoom to 200%, ensure everything renders as expected. Document 400% zoom issues with USWDS if appropriate. 

### How we'll stay on track

Time-based estimations are prone to inaccuracy and preconceived notions of "how long something should take" that often doesn't consider code review, qa, deployment and bug fixes. We'll keep it real about what we can deliver by tracking a velocity metric and considering that as we plan new sprints. That said, there are very real deadlines for this project! Here is how we can work together in an agile fashion to deliver on time:

-   **Definition** - Make sure the issues we slate for a sprint are sufficiently detailed (have everything you need to start) and are sufficiently broken up (about the same size, not more than a day).

-   **Execution** - We should all test what we create to the best extent possible to avoid churn in QA and code review.

-   **Velocity** - Our team should rally around the one thing we can control - the velocity of our output as defined by the number of tickets "done" in a given sprint. This will be acknowledged in our retros and compared to previous sprints.

# Supporting Meetings and processes

### Standup
We do standups on video chat, but everyone has the option to do it in Slack instead. 

### Sprint planning (Backlog->Available)

At the start of each sprint, we review the stories refined for implementation and ensure they are of sufficient definition and priority. We aim to take on work that can be completed within one sprint. If a story seems like it'll need to span more than one sprint, that may be a sign that it needs to be broken into a smaller chunk of work. 

All teams members to provide update in github issues in progress on Monday/early-Tues before sprint planning and backlog refinement. 

### Code Review (In Progress->Ready For Review->Done)

Pull requests are reviewed on a per-ticket basis for merge into test. Better to push to test more rather than less; we assume test will break.

Stories are reviewed against acceptance criteria (AC) with test coverage.

Once stories are reviewed, stories are pushed to staging.

One reviewer required for any pull request (both test and staging).

Anyone can review; ad-hoc. Prefer velocity. Signal to the team in slack if you've waited more than two hours for a review.

### Backlog refinement

At the middle of each sprint we refine the backlog. Risks and dependencies are evaluated, context provided, and stories are added/removed from the backlog based on learning from the previous sprint.

Participants: Smaller meeting at least containing Product Manager, Design Lead, and Engineering Lead

The UX team elaborates backlog stories that have been flagged for move from "backlog" to "to do."

Elaboration includes:

-   A two-sentence narrative.

-   Context

-   In/out of scope

-   Acceptance criteria

-   Latest mocks