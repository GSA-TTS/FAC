from config.settings import ENVIRONMENT
from django.test import TestCase
from psycopg2._psycopg import connection
from django.conf import settings

from datetime import datetime
import jwt
import os
import requests

class TestAdminAPI(TestCase):

    def get_connection(self):
        cloudgov = ["DEVELOPMENT", "PREVIEW", "STAGING", "PRODUCTION"]
        if settings.ENVIRONMENT not in cloudgov:
            conn_string = "dbname='postgres' user='postgres' port='5432' host='db'"
        else:
            conn_string = settings.CONNECTION_STRING
        conn = connection(conn_string)
        return conn

    # https://stackoverflow.com/questions/2511679/python-number-of-rows-affected-by-cursor-executeselect
    def test_users_exist_in_perms_table(self):
        if ENVIRONMENT in ["LOCAL"]:
            with self.get_connection().cursor() as cur:
                cur.execute("SELECT count(*) FROM public.support_administrative_key_uuids;")
                (number_of_rows,)=cur.fetchone()
                assert number_of_rows >= 1

    def setUp(self):
        self.api_url = settings.POSTGREST.get("URL")

    def create_payload(self, role="api_fac_gov"):
        payload = {
            # PostgREST only cares about the role.
            "role": role,
            "created": datetime.today().isoformat(),
        }
        return payload

    def test_postgrest_url_is_reachable(self):
        # We must pass a properly signed JWT to access the API
        encoded_jwt = jwt.encode(
            self.create_payload(), os.getenv("PGRST_JWT_SECRET"), algorithm="HS256"
        )
        response = requests.get(
            self.api_url, headers={"Authorization": f"Bearer {encoded_jwt}"}, timeout=10
        )
        self.assertEquals(response.status_code, 200)

    def test_api_fails_without_jwt(self):
        # We must pass a properly signed JWT to access the API
        response = requests.get(self.api_url, timeout=10)
        self.assertEquals(response.status_code, 400)

    def test_api_fails_with_bad_jwt(self):
        # We must pass a properly signed JWT to access the API
        encoded_jwt = jwt.encode(
            self.create_payload(),
            "thisisabadsecretitisveryverybadyeppers",
            algorithm="HS256",
        )
        response = requests.get(
            self.api_url, headers={"Authorization": f"Bearer {encoded_jwt}"}, timeout=10
        )
        self.assertEquals(response.status_code, 401)

    def test_api_fails_with_wrong_role(self):
        # We must pass a properly signed JWT to access the API
        encoded_jwt = jwt.encode(
            self.create_payload(role="thisisnotarole"),
            os.getenv("PGRST_JWT_SECRET"),
            algorithm="HS256",
        )
        response = requests.get(
            self.api_url, headers={"Authorization": f"Bearer {encoded_jwt}"}, timeout=10
        )
        self.assertEquals(response.status_code, 400)
