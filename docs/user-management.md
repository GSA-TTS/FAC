# User Management

We use Login.gov as our identity provider. In order to login to the app in local development and test environments, you will need to have a [Login.gov sandbox](https://idp.int.identitysandbox.gov/) account. FAC team members can request the shared team key.

The first time you login to the application, a user record in the FAC database will be created for you. We're using Django's provided [User model](https://docs.djangoproject.com/en/4.1/ref/contrib/auth/) and [admin interface](https://docs.djangoproject.com/en/4.1/ref/contrib/admin/) to manage accounts.

## Admin users

### Local development

To acquire admin access in the local environment, you can execute a management command directly.

```bash
# Run make_staff to promote a user to staff status
python manage.py make_staff user@example.com

# Run make_super to promote a user to superuser status
python manage.py make_super user@example.com
```

### Deployed instances

To add/remove/promote a user in the admin interface, you would modify the [staffusers.json](../backend/config/staffusers.json) list and submit a PR for this change.

Once the application starts up, it will adjust the user access to the admin site based on the updated list. If you are included in this list, you will be able to access the site via the `/admin` page.

**NOTE** - The email addresses included in this list MUST have a Login.gov account and have used it to log in to the application at least once. Otherwise, the application will ignore the email address on startup.

## Non-admin users

All other user accounts are managed via the Django admin. Admin users are able to create, update, deactivate, and remove accounts as needed.
