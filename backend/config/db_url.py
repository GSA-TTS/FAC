from django.core.exceptions import ImproperlyConfigured


def get_db_url_from_vcap_services(vcap, db_instance_name="fac-db"):
    database_url = None
    for db_service in vcap.get("aws-rds", []):
        if db_service.get("instance_name") == db_instance_name:
            database_url = db_service["credentials"]["uri"]
            break

    if not database_url:
        raise ImproperlyConfigured(
            "Database URL is not properly configured. Expected 'fac-db' URL."
        )
    return database_url
