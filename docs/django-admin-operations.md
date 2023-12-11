# Django admin operations

This is a how-to guide for common FAC Django admin operations.

The Django admin interface path is `/admin/`; the production instance is at [https://app.fac.gov/admin/](https://app.fac.gov/admin/). 

To use it, you must have logged into the application and have an account that has been granted access.

If you need to grant someone read-only access to the Django admin, see [Granting `staff` access](#granting-staff-access).

If you need to investigate why a user cannot see or access a submission, see [Looking up access information by `report_id` or email address](#looking-up-access-information-by-report_id-or-email-address).

If you need to investigate problems with a submission unrelated to access issues, see [Looking up submission information by `report_id` or UEI](#looking-up-submission-information-by-report_id-or-uei).

## Granting `staff` access

You must have `superuser` access to do this.

1.  Get the email address of the account to grant `staff` access to.
2.  Go to [https://app.fac.gov/admin/users/staffuser/add](https://app.fac.gov/admin/users/staffuser/add), enter the email address, and click on the **SAVE** button.
3.  Verify that the email address is in the list of users at [https://app.fac.gov/admin/users/staffuser/]([https://app.fac.gov/admin/users/staffuser/).
4.  Confirm with the user in question that they can log into the Django admin site.

## Looking up access information by `report_id` or email address

You must have `staff` or `superuser` access to do this.

1.  Get the `report_id` of the submission or the email address in question.
2.  Go to [https://fac-dev.app.cloud.gov/admin/audit/access/](https://fac-dev.app.cloud.gov/admin/audit/access/).
3.  Enter the `report_id` or email address into the search field at the top of the page and hit enter.
4.  You should now see only the list of `Access` entries associated with that `report_id` or email address.
5.  The roles and email addresses are displayed here and are usually all that’s required.
6.  If necessary, click on any of the entries in the **SAC** column in order to find more information about that `Access`.

## Looking up submission information by `report_id` or UEI

You must have `staff` or `superuser` access to do this.

1.  Get the `report_id` or UEI in question.
2.  Go to [https://fac-dev.app.cloud.gov/admin/audit/singleauditchecklist/](https://fac-dev.app.cloud.gov/admin/audit/singleauditchecklist/).
3.  Enter the `report_id` or UEI into the search field at the top of the page and hit enter.
4.  You should now see only the list of `SingleAuditChecklist` entries associated with that `report_id` or UEI.
5.  To see more information about a particular `SingleAuditChecklist`, click the number in the **ID** column.
