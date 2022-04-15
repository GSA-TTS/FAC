# 4. EIN or UEI before recording audits?

Introduced: 20220411

## Status

For Discussion

## Context

We are moving the FAC during an identifier transition within the community. Specifically, the transition from the EIN->UEI. 

This raises a number of questions.

1. Do we record both numbers?
2. Do we try and link an old EIN number to a new UEI number?
3. Do we record only the UEI?
4. Do we require the UEI before entering audit data?
5. Do we require the UEI before recording audit data?
6. Do we require the UEI before submitting audit data?


Each has implications, and all of this is subject to discussion.

1. If we begin capturing the EIN now, we will effectively be expected to capture it/hold it for years to come. Why? Do we have a clear product vision for why this is *necessary* or *sufficient* for ongoing operation of the FAC? No case has yet been made.
2. If we record both numbers, we are building a (potentially ad-hoc) mapping between the old and new. This would best be done by sam.gov. However, we have no idea (currently) if an entity might have multiple EINs that must be mapped to UEIs, and so forth. Further, it will be user data, and therefore (for all intents and purposes) untrustworthy and unverifiable. This is the purpose/point of the EIN.
3. There is a clearer case for only recording the UEI, because it is the new identifier of record.
4. Do we make it a blocker to entering any audit data? This would be a serious interruption of user flow, and may have negative repurcussions. It would require a substantial media campaign to alert the community of its necessity.
5. If we block the temporary storage of audit data without a UEI we end up in a space that is effectively as bad as #4. 
6. The difference between *recording* and *submitting* data might be that an audit can be "in progress" as opposed to "certified." That is, we might prevent the final double-certification (by auditee/auditor COs) until a valid UEI is present. However, the entire package could be loaded into the system up to that point. This would likely have the least impact on the end-user workflow. 

Not discussed is whether we can commit/certify an audit without an identifier. This is a non-starter.

## Decision

Subject to discussion. There is discussion related that has been sent to `fac-steering` as well.

## Consequences

Are there legal or ethical implications for suggesting that Entity1 was, historically, Entity2?

There may be an inclination to link UEI to EIN. However, doing so *incorrectly* will introduce *false information* into the FAC. If we are going to do that linkage, we need to decide what our comfort with incorrect linkages is. We will have no way to validate the linkage. 

