# 44. Data representation migration testing

Date: 2025-04-30

## Status

Accepted

## Areas of impact

- Engineering

## Related documents/links

* Source of truth parent ticket: https://github.com/GSA-TTS/FAC/issues/4740

## Context

The internal representation of data in the FAC is undergoing a complex redesign.

The original data design for the FAC involved an internal representation, centered around a table called `singleauditchecklist`, which we will refer to as the SAC. This table is where audits were *submitted*. While they were undergoing submission, the row containing audit data would experience multiple `UPDATE` operations. Once submitted, the data was *copied* from the SAC table to a set of "dissemination" tables. We call them the "dissemination" tables because... the data is distributed, or disseminated, from these. Once copied, neither the SAC nor the dissemination tables are updated. The audit is "frozen" in its submitted state.

This design makes resubmission more difficult than we would like. Specifically, a resubmission must now work with an internal representation (the SAC) as well as update/remove/modify an external representation (dissemination). This is almost guaranteed to lead to situations where the two representations are out of step with each-other.

A new data design, which we refer to as the "source of truth" (SOT), collapses these two views into a single table. During submission, the SOT is updated. Once submitted, we no longer edit the table, but we do serve data directly from the SOT. This way, there is no delay in dissemination, and we do not risk synchronization issues in future iterations of the FAC---specifically, in the case of resubmissions. 

Because this transition requires us to copy all of the data from the SAC to the SOT, and because it is an *internal* data migration, we need to assure ourselves (and our Federal partners and the public) that we have executed diligence in the migration. Therefore, we have two ways that we are validating the correctness of our migration of data from the SAC to the SOT:

1. **Internal**. We have a set of tests that allow us to migrate data internally between the tables and then compare data in the SAC and SOT.
2. **External**. We have a set of tests that allow us to use the API to compare the data in the dissemination tables and the SOT. 

The first check is internal, and validates the data migration. The second check simulates the experience that federal partners and the public experience when using the API for data extraction. By assuring that the data is 100% complete and identical via both means, we believe we are enacting a process that will faithfully reproduce all of the data in the existing data model in our new model without error.

## Decision

We will have both internal and external tests of data correctness/completeness.

### Internal

Our [internal data comparison strategy](https://github.com/GSA-TTS/FAC/blob/d14723b4f548775d1439caf518e599e2616ef424/backend/audit/models/utils.py#L208) validates that all data in SingleAuditChecklist exists in Audit, ignores structure and searches for keys/values. All values in SAC must exist in Audit. Because the SAC and SOT tables both contain large JSON objects (with sometimes different structure), we have decided to *ignore* that structure, and focus on the idea that the key/value relationships are what matter. If all of the keys are present in both models, and all of the values are identical for all keys, then we consider the two representations to be equivalent.

This validation will be performed whenever an audit is [saved in the app](https://github.com/GSA-TTS/FAC/blob/61deeb009d26e9655cb8744c3207e269295e10b1/backend/audit/models/audit.py#L296). It can also be done offline via [Django command](https://github.com/GSA-TTS/FAC/blob/real-time-checking/backend/dissemination/management/commands/source_of_truth.py) by providing either a `report_id` or a `fac_accept_date` date range.

### External

Our [external data comparison strategy](https://github.com/GSA-TTS/FAC/blob/d1caf9f715cd2c0ef3cb6d59e327e47b72b26d72/backend/dissemination/api/compare_api_results.py) validates that all data presented by [api_v1_1_0](https://github.com/GSA-TTS/FAC/tree/hdms/source-of-truth/api/backend/dissemination/api/api_v1_1_0) is present in [api_v1_2_0](https://github.com/GSA-TTS/FAC/tree/hdms/source-of-truth/api/backend/dissemination/api/api_v1_2_0). In this case, v110 is the API that points at the dissemination tables---the old data model---and the v120 API points at the SOT table.

However, unlike the internal data strategy, we need to be concerned with the structure of the API. We have users who are driving their oversight systems off the API, and therefore they expect:

* A given set of endpoints, which each contain
* A given set of keys, and
* Expect the data mapped to those keys to remain unchanged.

Therefore, this comparison expects the data to come back from the two APIs both in an identical order (in some cases) as well as with the exact same values.

### Operation

As part of this work, we have [created a consistent set of data to test against](https://github.com/GSA-TTS/FAC/blob/jr/source-of-truth/main/backend/util/load_public_dissem_data/README.md). It is based on a dump of production data from March 2025. In preparing the data, we removed all Tribal data, and then modified 500 audits/year to "look like" Tribal/suppressed audits. In this way, we have an authentic dataset that contains data that is 100% public.

We will run complete migrations of all data in this set, using the internal tools to validate the migration. We will then run the API test against all data as well. Once we go to production, we will carry out similar tests in our "lower" environment (staging) before running the migration in production. We will do a final validation of all data, using both methods, in our production environment, assuring that 1) all data is present, and 2) all data migrated successfully.

When we are assured that the SOT model is operating fully, we will disable and, ultimately, archive the SAC/dissemination models.

## Consequences

Data migrations are always fraught. We believe that our approach provides the maximum assurance that no changes in data will result because of our work. 

1. The internal tests assure us that all data is accounted for at time of migration. 
2. The external tests assure us that the user experience will remain uninterrupted.

We have other unit tests and E2E tests that will continue to operate throughout this process. We are using these in addition to these new migration-centric tests to make sure that nothing changes in the FAC experience. 

We believe, once complete, the consequences will be that we have:

1. A model prepared to support audit resubmission
2. A more performant API
3. A more performant/real-time search experience

