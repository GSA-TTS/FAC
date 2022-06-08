# 7. Use the SAM.gov API for UEI validation

Date: 2022-05-10

## Status

Accepted

## Context

Our model includes a Unique Entity Identifier (UEI) to distinctly recognize entities. How will we validate UEIs?

## Decision

UEIs are [specifically structured](https://www.gsa.gov/about-us/organization/federal-acquisition-service/office-of-systems-management/integrated-award-environment-iae/iae-systems-information-kit/uei-technical-specifications-and-api-information) and maintained by SAM.gov. Sam.gov offers an Entity API here: https://open.gsa.gov/api/entity-api/.

**We will initially validate UEIs locally**

**We will use [SAM.gov's Entity API](https://open.gsa.gov/api/entity-api/) to fully validate UEIs and retrieve entity data**

## Considerations:

* Fully offline verification of UEIs isn't possible
* A verified System Account is required for SAM.gov
* SAM.gov's API is limited to 10,000 requests a day
* The SAM.gov API could go down for service or maintenance which may have an impact

## Consequences

* Local validation of UEIs should be done before making an API call to SAM.gov
* A System Account will be created and managed for SAM.gov
* SAM.gov requests should be limited
* SAM.gov downtime should be addressed
* SAM.gov entity data may be private and should be limited in what it returns
