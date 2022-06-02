# 6. Use the Static Site Generator Eleventy for the FAC Frontend

Date: 2022-04-26

## Status

Accepted

## Context

Our architecture calls for an API to be the interface for both our initial frontend as well as future FAC users. We will build the API using Django. How will we build the frontend that consumes the API?

## Decision

The TTS Engineering Practices Guide to [Choosing a Web App Architecture](https://engineering.18f.gov/web-architecture/) recommends using static sites for frontend applications whenever possible. Given the number of forms involved, the [FAC frontend](https://github.com/gsa-TTS/fac-frontend) may approach the outer edges of complexity for which the Guide recommends using a static site. However, we can still pick a static site generator that will allow us to keep the frontend as simple as possible while still adhering to the planned [API/Client architecture](https://github.com/GSA-TTS/FAC/blob/main/docs/architecture/decisions/0003-initial-architecture.md).

**We will use [Eleventy](https://www.11ty.dev/) (sometimes styled as 11ty) to build the frontend**

## Considerations:

* Eleventy is well-supported on Federalist/Cloud.gov Pages, with an [official new site template](https://github.com/cloud-gov/11ty-uswds-template/) in the works.
* Eleventy is highly configurable, but can support workflows that will be familiar to Jekyll users, of which there are many at GSA.

## Consequences

* Client-side interactions should be simple.
* The server will be responsible for managing application state.
