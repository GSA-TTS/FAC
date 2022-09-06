# 6. Proposed UEI handling change

Introduced: 2022-09-02

## Status

Proposed.

## Context

As part of a government-wide move, the FAC is switching from EIN to UEI for the purpose of identifying submitting organizations. We would like to verify submitted UEIs with the SAM.gov API as part of the FAC submission process.

UEI is relatively new and many individuals involved in submissions may not know, or know how to get, their organization's UEI. In addition, there are potential delays involved with organizations acquiring UEIs and/or with our being able to validate them.

Our [initial decision](https://github.com/GSA-TTS/FAC/blob/main/docs/product/decisions/0002-P-uei.md) was to capture UEI instead of DUNS, and that is not changing. This decision concerns cases where submitters are unable to provide a fully-validated UEI recognized by SAM.gov.

## Decision: two datasets

Currently we see no way to avoid potentially storing two sets of data relating to UEI:

*   Name and address data supplied by SAM.gov in the case that the user submits a UEI that SAM.gov verifies.
*   Name and address data supplied by the user in the case that no info from SAM.gov is supplied.

These are the relevant fields in the data model:

*   `auditee_uei`
*   `auditee_uei_is_sam_validated`
*   `auditee_sam_organization_name`
-   `auditee_sam_address_line_1`
-   `auditee_sam_city`
-   `auditee_sam_state`
-   `auditee_sam_zip`
*   `auditee_unverified_organization_name`
-   `auditee_unverified_name`
-   `auditee_unverified_address_line_1`
-   `auditee_unverified_city`
-   `auditee_unverified_state`
-   `auditee_unverified_zip`

The above name and address fields will replace these existing fields:

*   `auditee_name`
-   `auditee_address_line_1`
-   `auditee_city`
-   `auditee_state`
-   `auditee_zip`

### If the submitter has, knows, and enters the correct UEI, and we get a response from SAM.gov that the user approves

In this case the user sees the canonical SAM.gov name for their organization after they enter the UEI and this is the name used for the rest of their submission. We would also pull address data from SAM.gov. Neither name or address data would be editable by the user.

Changing the UEI would be possible but would require going through the original process again.

We would store the following:

<dl>
<dt><code>auditee_uei</code></dt>
<dd>Any entries here would have to conform to the UEI specification but would not have to be verified by SAM.gov.</dd>
<dt><code>auditee_uei_is_sam_validated</code></dt>
<dd>A boolean value that is only set to true if we have received confirmation from SAM.gov that the UEI submitted is verified.</dd>
<dt><code>auditee_sam_organization_name</code></dt>
<dd>The name of the organization as supplied by SAM.gov.</dd>
<dt><code>auditee_sam_address_line_1</code>, <code>auditee_sam_city</code>, <code>auditee_sam_state</code>, <code>auditee_sam_zip</code></dt>
<dd>The address information for the organization as supplied by SAM.gov.</dd>
</dl>

These fields would not be displayed as form fields but as text values. Some UI allowing the user to kick off the UEI submission process would be necessary in order for users to change their UEI.

### If the submitter is unable to supply a correct UEI and/or we do not get a response from SAM.gov

In this case the user would be prompted to enter their own organization name (and possibly address), which would potentially later be written over if a user enters a valid UEI through the above process.

<dl>
<dt><code>auditee_uei</code></dt>
<dd>If the user entered something that SAM.gov did not verify, that value would be stored here.</dd>
<dt><code>auditee_uei_is_sam_validated</code></dt>
<dd>This would be false in this case.</dd>
<dt><code>auditee_unverified_organization_name</code></dt>
<dd>The name of the organization as supplied by the user.</dd>
<dt><code>auditee_unverified_address_line_1</code>, <code>auditee_unverified_city</code>, <code>auditee_unverified_state</code>, <code>auditee_unverified_zip</code></dt>
<dd>The address information for the organization as supplied by the user.</dd>
</dl>

The UI for kicking off the UEI submission process would be available here also, but otherwise all of these fields would be presented as user-editable.

We probably need to flag this in some way that makes it clear that UEI is the standard and that submitting without one may require jumping through further hoops.

### Proceeding to a finalized submission

We will not support both sets of fields on the dissemination side. Pending future technical decisions, either the data model for post-submission audits will be distinct from that for in-progress audits, or we will add a third set of fields that can be searched for organization name and address.

Any case in which SAM.gov has verified the UEI and provided information to us will result in that provided information populating the post-submission fields; only if the SAM.gov-provided information is absent would user-entered information be used.

If a verified UEI is present, finalization will require the user to attest that this UEI is the correct one and that the name (and address, potentially) associated with it in SAM.gov is valid. (At this attestation step all of this data would be presented to the user.)

If a verified UEI is not present, finalization will require the user to attest that they have exhausted their attempts to acquire one, and that the name and address they are submitting are correct. (At this attestation step all of this data would be presented to the user.)

### Policy question: can submissions without UEIs be rejected?

Organizations are required to submit these reports, and it's not currently clear that the FAC would be within its rights to refuse to let a submission proceed without a UEI—especially if the submission lacks a UEI because the organization has for some reason been unable to acquire one.

In order to determine product and technical direction on how to handle this case, we first need policy direction.
