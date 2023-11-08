# Census Historical Migration

### How to run the historic data migrator:
```
docker compose run web python manage.py historic_data_migrator --email any_email_in_the_system@woo.gov \
  --year 22 \
  --dbkey 100010
```
- The email address currently must be a User in the system. As this has only been run locally so far, it would often be a test account in my local sandbox env.
- `year` and `dbkey` are optional. The script will use default values for these if they aren't provided.

### How to run the historic workbook generator:
```
docker compose run web python manage.py historic_workbook_generator
  --year 22 \
  --output <your_output_directory> \
  --dbkey 100010
```
- `year` is optional and defaults to `22`.
- The `output` directory will be created if it doesn't already exist.

### How to trigger historic data migrator from GitHub:
- Go to GitHub Actions and select `Historic data migrator` action
- Next, click on `Run workflow` on top right and 
- Provide the target `environment` along with optional parameters such as `dbkeys` and `years`
- Click `Run`
