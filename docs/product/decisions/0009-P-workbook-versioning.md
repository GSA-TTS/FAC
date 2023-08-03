# Versioning submission workbooks

Introduced: 2023-08-02

## Status

Accepted.

## Context

The majority of an SF-SAC submission is in the form of spreadsheet documents. We provide these as `.xlsx` files. Auditors and auditees fill these spreadsheets in, upload them to `fac.gov`, we validate the contents, and then store the data.

We are concerned about *versioning* because of scenarios like the following:

1. A user downloads a workbook.
2. We discover a bug that requires a change to the workbook. This change results in material changes to the data validation and how we store/process the data.
3. Changes are made, and we publish the new workbook. 
4. The user attempts to upload the "old" workbook. It fails to validate, and they cannot complete their submission.

Our versioning process provdies a way we can 1) document and 2) clearly communicate about changes that may need to be made to the XLSX workbooks in service to collecting the SF-SAC.

## Decision: Workbook versioning is required

In short:

* Every workbook will carry a version number. This will be on a "coversheet." 
* Workbook validation will include the version number. This means that we will be validating that a submission is coming in on the correct version of the workbook.
* All workbooks will version together. When we make a change to one workbook, all workbook versions will change. E.g. if a workbook goes from version 1.0.0 to 1.0.1, then *all* workbooks go to version 1.0.1.
* We will use the website and other messaging channels, as appropriate, to announce version changes. Where possible, we will provide advance notice. For errors that impact data integrity (e.g. bugs), advance notice may not be possible.

## Details regarding versioning

In support of our decision, what follows are details regarding how we will version our workbooks, and the likely scenarios we forsee.

### Versioning conventions

* We use MAJOR, MINOR, and PATCH conventions from [SemVer](https://semver.org/) to clearly signal what we’re doing.

#### Examples

* `1.0.0` - First frozen version
* `1.0.1` - Fixes a bug
* `1.1.0` - Adds a new component, but is compatible with prior validations
* `2.0.0` - Breaks compatibility with older workbooks and validations

### Offering multiple workbook versions in parallel

Some workbook changes are minor. For example:

1. We discover a typo in a header in the 1.0.0 workbook.
2. We fix it, and update the version number to 1.0.1

This did not change anything of substance from a data collection perspective. Therefore, our validation process would want to accept *both* version 1.0.0 and 1.0.1 workbooks.

In this scenario, in-flight or in-process submissions are not impacted at all.

## Significant changes: adding features

Some workbook changes are more significant. These should generally be *optional* features or additions that do not strictly break the data collection, but potentially are useful for administrative or other reasons. They should be announced with a timeline for transition.

For example:

1. We discover that a version number is not enough. We also need a `version_name`.
2. We add this to the workbooks. We bump the version from 1.0.0 to 1.1.0, because it is a new component or feature.
3. We decide that recording this is 1) administrative, but also 2) not essential. We therefore make the validation *optional*.
6. We make version 1.1.0 workbooks the default for download from fac.gov
4. We accept both versions 1.0.0 and 1.1.0 in parallel.
5. We message that we intend to make 1.1.0 the only valid submission version *in 12 weeks*, or 3 months. We message this through the website and other channels.
6. In three months, we remove version 1.0.0 from the list of workbooks that we accept.

Generally, we will aspire to **3 month** feature windows. That is, we will:

1. Announce a new feature in the workbooks, and make that new version the default download.
2. Both the prior and new version will be able to be uploaded during that 3 month window.
3. We will remind people 1 month (4 weeks) before the close of the window to use the newest workbooks.
4. At the end of the transition window, we will remove the old version from the acceptable workbook version list.

In this scenario, in-flight or in-process submissions are not impacted at all.

## Significant changes: fixing bugs

Some changes are urgent, and impact the integrity of the data collection.

1. We discover that a field is allowing inappropriate or incorrect data to be entered.
2. We make changes to the workbooks, changing the version number from 1.1.0 to 2.0.0, as we found a change that breaks the prior workbooks.
3. We publish the new workbooks.
4. We immediately *only* accept workbooks that pass the 2.0.0 validations.
5. We announce this through the website and other channels.

In this scenario, submissions that are in-flight are impacted. Assuming all the workbooks were already uploaded, they would then fail to pass final validation. Auditors and auditees would have to download the new workbook version, copy data from the old to the new, and re-upload their workbooks.

We never want to do this, but it might happen. It is bad for users, but we must maintain the integrity of the data collection. Therefore, this kind of breaking change to workbooks might happen, and this is the process we would follow.

