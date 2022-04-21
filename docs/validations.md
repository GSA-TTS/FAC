# Validations

An essential function of this application is to validate inbound SF-SAC and SingleAudit data. This document serves as a repository of:

* Each specific validation, including the fields/attributes examined, the logic applied, and a plain-language summary
* Where and how each validation is defined
* Where and how each validation is tested
* Notes on how these validations can be modified

##

| Form Step | Validation | Fields | Implementation | Test coverage
| --- | --- | --- | --- | --- |
| Eligibility | Org type must be one of `audit.models.SingleAuditChecklist.USER_PROVIDED_ORGANIZATION_TYPES` | `USER_PROVIDED_ORGANIZATION_TYPE` | `api.serializers.EligibilitySerializer` |  `api.test_serializers.EligibilityStepTests`
| Eligibility | Must be USA based | `IS_USA_BASED`| `api.serializers.EligibilitySerializer` | `api.test_serializers.EligibilityStepTests`
| Eligibility | Must meet spending threshold| `MET_SPENDING_THRESHOLD`| `api.serializers.EligibilitySerializer` | `api.test_serializers.EligibilityStepTests`
