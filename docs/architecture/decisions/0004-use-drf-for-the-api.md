# 4. Use Django Rest Framework for the API

Date: 2022-03-30

## Status

Accepted

## Context

Our architecture calls for an API to be the interface for both our initial frontend as well as future FAC users. How will we build that API?

**We will use [Django REST framework](https://www.django-rest-framework.org/) to implement the API**

**We will use OpenAPI to document our API**

Considerations:
* DRF is 18F's `default` choice for python APIs: https://engineering.18f.gov/python/
* There is existing art across TTS projects which are successfully using DRF today
  * Including existing patterns for handling authentication


## Consequences

* We'll follow TTS and GSA guides and standards in implementing our API https://tech.gsa.gov/guides/API_standards/
* We'll strive to leverage shared services like [https://api.data.gov]().
* We'll implement all listing, view, update, and creation API actions in Django Rest Framework
* We'll need to ensure our CI pipeline includes building of API documentation and that our test-suite covers accessibility scanning of our API documentation
