import os
from django.core.exceptions import ImproperlyConfigured


def get_db_url_from_vcap_services(
    vcap,
):
    database_url = None
    for db_service in vcap.get("aws-rds", []):
        if db_service.get("instance_name") == "fac-db":
            database_url = db_service["credentials"]["uri"]
            break

    if not database_url:
        raise ImproperlyConfigured(
            "Database URL is not properly configured. Expected 'fac-db' URL."
        )
    return database_url


def delete_env_var(env_var_name):
    if env_var_name in os.environ:
        del os.environ[env_var_name]
