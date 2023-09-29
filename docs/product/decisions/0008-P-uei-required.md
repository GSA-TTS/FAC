# UEI required for submission 

Introduced: 2023-05-31

## Status

Accepted.

## Context

This supersedes all prior ADRs and PDRs regarding UEI.

Uniform Guidance for 2022 required the UEI for FAC submission. No new guidance is being issued regarding the UEI: it is required in order to submit the SF-SAC.

It was the case (in 2022) that there was a substantial backlog for UEI requests. As of May 2023, the average time needed by SAM.gov to manually review UEI requests is 4 days.

## Decision: UEI is required

The UEI is required for submission, and we must be able to validate it against SAM.gov in order for a submission to proceed.

### A UEI is required

Submitters must have a valid UEI in hand at the time they go to submit their Single Audit. It will not be possible to proceed through the submission process without a UEI.

### The UEI must validate against SAM.gov

The UEI is requested early in the submission process. We will follow this process:

1. User enters their UEI.
2. We attempt to validate their UEI against SAM.gov using the SAM.gov API
3. If the UEI validates, skip to step 6.
4. If SAM.gov is available, and the UEI does not validate, we will:
    1. Present an error to the user, suggesting they double-check their UEI and return to step 1.
5. If SAM.gov is not available, we will:
   1. Present a message to the user, and suggest they try submitting again later, returning to step 1.
6. The user may proceed with their submission.

Put simply: it will not be possible to submit the SF-SAC without a valid UEI. A UEI is, for purposes of this PDR, considered "valid" when all of the following is true:

1. The UEI passes validation tests in keeping with the [UEI technical specifications](https://www.gsa.gov/about-us/organization/federal-acquisition-service/technology-transformation-services/integrated-award-environment-iae/iae-systems-information-kit/uei-technical-specifications-and-api-information)
2. SAM.gov is online and available.
3. The SAM.gov API indicates that the UEI presented is valid and in the SAM.gov database

