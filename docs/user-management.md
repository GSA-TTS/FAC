# User Management

We use Login.gov as our identity provider. In order to login to the app in local development and test environments, you will need to have a [Login.gov sandbox](https://idp.int.identitysandbox.gov/) account. FAC team members can request the shared team key.

The first time you login to the application, a user record in the FAC database will be created for you. We're using Django's provided [User model](https://docs.djangoproject.com/en/4.1/ref/contrib/auth/) and [admin interface](https://docs.djangoproject.com/en/4.1/ref/contrib/admin/) to manage accounts.

## Admin users

To promote a user to either staff or superuser status, we'll use a Django management command. If you're running locally, the management command can be executed directly.

```bash
# Run make_staff to promote a user to staff status
python manage.py make_staff user@example.com

# Run make_super to promote a user to superuser status
python manage.py make_super user@example.com
```

To run it against a deployed instance, we'll SSH into the app, [configure our session](https://cloud.gov/docs/management/using-ssh/#application-debugging-tips), and then run the command.

```bash
# SSH to cloud.gov **instance**
cf ssh gsa-fac-dev

# Configure session per cloud.gov docs
/tmp/lifecycle/shell

# Run make_staff to promote a user to staff status
python manage.py make_staff user@example.com

# Run make_super to promote a user to superuser status
python manage.py make_super user@example.com
```

Once your user is promoted, you'll be able to access the admin site via the `/admin` page.

## Non-admin users

All other user accounts are managed via the Django admin. Admin users are able to create, update, deactivate, and remove accounts as needed.
