from django.core.exceptions import ImproperlyConfigured


def check_vcap_services(vcap, env):
    if not vcap:
        raise ImproperlyConfigured("VCAP_SERVICES environment variable is not set.")

    database_url = None

    for db_service in vcap.get("aws-rds", []):
        if db_service.get("name") == "fac-db":
            database_url = db_service["credentials"]["uri"]
            break

    # Retrieve the app URL
    app_url = env("DATABASE_URL")

    if not database_url or database_url != app_url:
        raise ImproperlyConfigured(
            "Database URL is not properly configured. Expected 'fac-db' URL."
        )
