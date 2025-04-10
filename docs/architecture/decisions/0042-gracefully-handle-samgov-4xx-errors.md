## Areas of impact

- [ ]   Compliance
- [ ]   Content
- [x]   CX
- [ ]   Design
- [x]   Engineering
- [x]   Policy
- [x]   Product
- [ ]   Process
- [ ]   UX

## Related documents/links

## Context

The FAC validates all of the data coming in. Part of that validation process comes at the very beginning: we make sure that the UEI presented is active in SAM.gov.

In order to make this check, we need a system-to-system credential from SAM.gov. It must be updated every 90 days. That process involves:

1. Being registered as a system owner in SAM.gov
2. Visiting SAM.gov, logging in, and obtaining the key
3. Entering it into our CI/CD secrets
4. Re-deploying the FAC

All of this is a manual process, from obtaining the key through to redeploy, and it cannot be automated. At most, three individuals are able to be registered to be allowed to obtain this key in SAM.gov.

If SAM.gov goes down for an extended period of time, or if there is no one available to perform these API key updates, then the FAC will no longer allow new audits to be created. This would block the submission of audits (as required under the Single Audit Act and 2CFR200), and also block oversight at dozens of agencies.

For this reason, we are going to add a graceful degradation pathway to the FAC.


## Decision


1. If the API key works, we will uphold our UEI validations.
2. If the API key fails, we use our UEI waiver process (internally and automatically), which will serve as a log/audit trail for the process by which we excepted the creation of the new audit.


## Consequences

Although this *could* lead to an incorrect UEI being used, it would at least leave a trail that could be revisited. And, this is only a path that will be followed if the FAC ends up in a space where we are unable (for technical or other reasons) unable to update the API key or otherwise communicate in a robust manner with SAM.gov.

The possibility that the UEI would be incorrect is non-zero, but it all other validations would continue to operate. As a result, data quality would remain high for the submission, and any inconsistencies would be handled by an oversight official at the cog/over agencies involved with the audit.