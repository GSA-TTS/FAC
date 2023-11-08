# 29. Use GitHub issues to start ADR process

Date: 2023-11-06

## Status

Accepted

## Areas of impact

*   Process

## Related documents/links

*   Our original decisions to use ADRs (and later, Product Decision Records).
*   [Jadud’s ADR issue template](https://github.com/jadudm/issue-template-exploration/issues/1)
*   [Initial issue for this ADR](https://github.com/GSA-TTS/FAC/issues/2729)

## Context

We stopped using ADRs (and PDRs) over time, without really meaning to. The current process for creating them is getting in the way, and the distinction between Product and Architecture decisions is more confusing than useful. We want it to be easier for more people to suggest them, for the team to discuss them, and in general to focus on recording more decisions in smaller chunks.

Our current process is based upon creating a document and then a pull request to bring that document into our project tree. This is an attempt at making an easier process.

It's also relevant that our existing ADR process resulted in ADRs hanging out in the tree without actually being accepted, which is unhelpful.

## Decision

1.  Use a specific issue template, probably something like [this one](https://github.com/jadudm/issue-template-exploration/issues/1), to write the first draft of an ADR.
2.  Engage in discussion with the team or a subset around the ADR issues.
3.  If accepted, a person who’s comfortable with Git and the pull request review process will help the author get it into the pull request queue. The finalized ADR will be in the tree with other documentation. This will be co-working, not the author handing it off to someone else.
4.  Establish some regular check-in time for ADR discussion. This includes checking on the ADR pull request queue.

Additional details:

*   If an ADR is contentious, assign a second person to it at the ADR check-in; the author and that person are now responsible for getting it accepted, getting it rejected, or redoing it by the following ADR check-in.
*   The pull request review should be quick since the discussion happened in the issue, but while comments or objections here should be rare, they’re allowed.
*   We’ll use ADRs for everything at this point; no more PDRs, no additional categories.
*   We might move all the existing accepted PDRs into the ADR directory and tweak the numbers just so the records are in order. [PR for this is here]().
*   ADRs are GitHub-flavored Markdown, have ``.md`` extensions, and have filenames that start with a four-digit number followed by lowercase characters and digits, using hyphens instead of spaces and no other punctuation.
*   Diagrams in ADRs should be PlantUML or Mermaid.js.
*   The date for the ADR is the date the file for the tree is created, not the date the issue is created.
*   ADR issues will use the [adr label](https://github.com/GSA-TTS/FAC/issues?q=is%3Aissue+is%3Aopen+label%3Aadr).
*   We will put templates for ADR issues and for the file version of ADRs (they will be very similar) into the repository.
*   The ADR in the pull request should have its status set to “Accepted”—that is the status it will have in the tree once the pull request is accepted.
*   The possible ADR statuses are:
    *   Accepted
    *   Deprecated
    *   Superseded (with reference to whatever the superseding decision is)
    *   (We don’t used “proposed” because our ADR issues are essentially ADRs in that phase, so that status never makes it into the tree.)

## Consequences

The barrier for creating ADRs will be lower.

It should be easier to keep knowledge and context around decisions in relatively bounded spaces (first, the ADR issue, then the ADR file once discussion is complete).

Decisions will be more visible to the team (and everyone else).
