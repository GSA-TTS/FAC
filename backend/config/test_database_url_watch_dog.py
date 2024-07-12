from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
import environs


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


class CheckVCAPServicesTestCase(TestCase):
    def setUp(self):
        self.env = environs.Env()
        environs.Env.read_env()

    def test_vcap_services_not_set(self):
        with self.assertRaises(ImproperlyConfigured) as context:
            check_vcap_services(None, self.env)
        self.assertEqual(
            str(context.exception), "VCAP_SERVICES environment variable is not set."
        )

    def test_database_url_not_found(self):
        vcap = {
            "aws-rds": [
                {
                    "name": "other-db",
                    "credentials": {
                        "uri": "postgres://other:password@localhost/otherdb"
                    },
                }
            ]
        }
        with self.assertRaises(ImproperlyConfigured) as context:
            check_vcap_services(vcap, self.env)
        self.assertEqual(
            str(context.exception),
            "Database URL is not properly configured. Expected 'fac-db' URL.",
        )

    def test_database_url_mismatch(self):
        vcap = {
            "aws-rds": [
                {
                    "name": "fac-db",
                    "credentials": {
                        "uri": "postgres://wrong:password@localhost/wrongdb"
                    },
                }
            ]
        }
        with self.assertRaises(ImproperlyConfigured) as context:
            check_vcap_services(vcap, self.env)
        self.assertEqual(
            str(context.exception),
            "Database URL is not properly configured. Expected 'fac-db' URL.",
        )


def test_database_url_correct(self):
    vcap = {
        "aws-rds": [
            {
                "name": "fac-db",
                "credentials": {
                    "uri": "postgres://user:password@localhost:5432/mydatabase"
                },
            }
        ]
    }
    with self.settings(
        ENV={"DATABASE_URL": "postgres://user:password@localhost:5432/mydatabase"}
    ):
        try:
            check_vcap_services(vcap, self.env)
        except ImproperlyConfigured:
            self.fail("check_vcap_services() raised ImproperlyConfigured unexpectedly!")
