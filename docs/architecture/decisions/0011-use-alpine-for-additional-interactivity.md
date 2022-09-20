# 11. Use the Static Site Generator Eleventy for the FAC Frontend

Date: 2022-09-06

## Status

Pending

## Context

The FAC frontend needs to support some complicated interactions as well as binding DOM elements to data. It would be helpful to add a lightweight JavaScript library to make implementing these features easier without having to write this code ourselves from scratch.


## Decision

We will use a combination of Eleventy's [is-land plugin](https://is-land.11ty.dev/) with [Alpine JS](https://alpinejs.dev/).

## Considerations:

* As a first-party plugin, `is-land` is well-supported by the Eleventy team, and makes it simple to add small pieces of interactivity/reactivity to isolated parts of a page according to the [Islands Architecture](https://www.patterns.dev/posts/islands-architecture/) pattern.
* Alpine is a small library that:
  * Works out of the box with `is-land`
  * Includes a lightweight frontend state-management solution the FAC can leverage without bringing in the complexity of a tool like Redux.
  * Integrates easily into our existing templates and doesn't require creating separate JS-based components. This will let us keep content in YAML/markdown where it currently lives.

## Consequences

* Future components will be able to leverage Alpine, requiring less custom JS.
* Adding `is-land` will allow the team to add other libraries on a page-by-page basis if needed.
