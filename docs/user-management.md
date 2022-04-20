# User Management

During initial development, we're using Django's provided User model, authentication, and admin interface to manage accounts locally and in test environments.


## Admin users

To create a new superuser account, we'll use a Django management command. If you're running locally, the management command can be executed directly. To run it against a deployed instance, we'll SSH into the app, [configure our session](https://cloud.gov/docs/management/using-ssh/#application-debugging-tips), and then run the command.

```bash
# SSH to cloud.gov instance
cf ssh gsa-fac-dev

# Configure session per cloud.gov docs
/tmp/lifecycle/shell

# Run createsuperuser
python manage.py createsuperuser
```

One you've followed the prompts and received a `Superuser created successfully.` response, you'll be able to access the admin via `/admin`.

## Non-admin users

All other user accounts are managed via the Django admin. Admin users are able to create, update, deactivate, and remove accounts as needed.
