from django.test import TestCase
from psycopg2._psycopg import connection
from django.conf import settings

from datetime import datetime
import jwt
import os
import requests


class TestAdminAPI(TestCase):
    # We can force a UUID locally that would not work when using api.data.gov,
    # because api.data.gov sets/overwrites this.
    api_user_uuid = "61ba59b2-f545-4c2f-9b24-9655c706a06c"
    admin_api_version = "admin_api_v1_1_0"

    def get_connection(self):
        cloudgov = ["DEVELOPMENT", "PREVIEW", "STAGING", "PRODUCTION"]
        if settings.ENVIRONMENT not in cloudgov:
            conn_string = "dbname='postgres' user='postgres' port='5432' host='db'"
        else:
            conn_string = settings.CONNECTION_STRING
        conn = connection(conn_string)
        return conn

    def admin_api_events_exist(self):
        # If we did the above, there should be non-zero events in the
        # admin API event log.

        query_url = self.api_url + "/admin_api_events"
        response = requests.get(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "accept-profile": TestAdminAPI.admin_api_version,
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
        )
        objects = response.json()
        self.assertGreater(len(objects), 0)

        # And, we should have at least added and removed things.
        added = False
        removed = False
        for o in objects:
            if "added" in o["event"]:
                added = True
            if "removed" in o["event"]:
                removed = True
        self.assertEquals(added and removed, True)

    # https://stackoverflow.com/questions/2511679/python-number-of-rows-affected-by-cursor-executeselect
    def test_users_exist_in_perms_table(self):
        with self.get_connection().cursor() as cur:
            cur.execute("SELECT count(*) FROM public.support_administrative_key_uuids;")
            (number_of_rows,) = cur.fetchone()
            self.assertGreaterEqual(number_of_rows, 1)

    def setUp(self):
        self.api_url = settings.POSTGREST.get("URL")
        self.encoded_jwt = jwt.encode(
            self.create_payload(role="api_fac_gov"),
            os.getenv("PGRST_JWT_SECRET"),
            algorithm="HS256",
        )

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

    def test_assert_fails_with_bad_user_id(self):
        # We must pass a properly signed JWT to access the API

        # Insert a user via API
        query_url = self.api_url + "/rpc/add_tribal_access_email"
        response = requests.post(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "content-profile": TestAdminAPI.admin_api_version,
                "content-type": "application/json",
                "prefer": "params=single-object",
                # We can force a UUID locally that would not work when using api.data.gov,
                # because api.data.gov sets/overwrites this.
                "x-api-user-id": "not-a-user-id",
            },
            timeout=10,
            json={"email": "not.a.test.user@fac.gsa.gov"},
        )
        print("response", response.text)
        self.assertEquals(response.text, "false")
        self.assertEquals(response.status_code, 200)

    def test_cannot_find_without_access(self):
        # We must pass a properly signed JWT to access the API

        # Insert a user via API
        query_url = self.api_url + "/rpc/add_tribal_access_email"
        response = requests.post(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "content-profile": TestAdminAPI.admin_api_version,
                "content-type": "application/json",
                "prefer": "params=single-object",
                # We can force a UUID locally that would not work when using api.data.gov,
                # because api.data.gov sets/overwrites this.
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
            json={"email": "test.user@fac.gsa.gov"},
        )
        self.assertEquals(response.text, "true")
        self.assertEquals(response.status_code, 200)

        # With the right permissions, I can check if things are present
        # via the associated view.
        query_url = self.api_url + "/tribal_access"
        response = requests.get(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "accept-profile": TestAdminAPI.admin_api_version,
                "x-api-user-id": "not-a-user-id",
            },
            timeout=10,
        )
        found = False
        objects = response.json()
        for o in objects:
            if "test.user@fac.gsa.gov" in o["email"]:
                found = True
        self.assertEquals(objects, [])
        self.assertEquals(found, False)

        # Now, remove the user, and find them absent.
        query_url = self.api_url + "/rpc/remove_tribal_access_email"
        response = requests.post(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "content-profile": TestAdminAPI.admin_api_version,
                "content-type": "application/json",
                "prefer": "params=single-object",
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
            json={"email": "test.user@fac.gsa.gov"},
        )
        self.assertEquals(response.text, "true")
        self.assertEquals(response.status_code, 200)

    def test_find_gsa_users_in_table(self):
        # We must pass a properly signed JWT to access the API

        # Insert a user via API
        query_url = self.api_url + "/rpc/add_tribal_access_email"
        response = requests.post(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "content-profile": TestAdminAPI.admin_api_version,
                "content-type": "application/json",
                "prefer": "params=single-object",
                # We can force a UUID locally that would not work when using api.data.gov,
                # because api.data.gov sets/overwrites this.
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
            json={"email": "test.user@fac.gsa.gov"},
        )
        self.assertEquals(response.text, "true")
        self.assertEquals(response.status_code, 200)

        # With the right permissions, I can check if things are present
        # via the associated view.
        query_url = self.api_url + "/tribal_access"
        response = requests.get(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "accept-profile": TestAdminAPI.admin_api_version,
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
        )
        found = False
        for o in response.json():
            if "test.user@fac.gsa.gov" in o["email"]:
                found = True
        self.assertEquals(found, True)

        # Now, remove the user, and find them absent.
        query_url = self.api_url + "/rpc/remove_tribal_access_email"
        response = requests.post(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "content-profile": TestAdminAPI.admin_api_version,
                "content-type": "application/json",
                "prefer": "params=single-object",
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
            json={"email": "test.user@fac.gsa.gov"},
        )
        self.assertEquals(response.status_code, 200)

        query_url = self.api_url + "/tribal_access"
        response = requests.get(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "accept-profile": TestAdminAPI.admin_api_version,
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
        )
        found = False
        for o in response.json():
            if "test.user@fac.gsa.gov" in o["email"]:
                found = True
        self.assertEquals(found, False)

    def test_find_many_gsa_users_in_table(self):
        all_emails = [
            "test.user@fac.gsa.gov",
            "alice@fac.gsa.gov",
            "bob@fac.gsa.gov",
        ]

        # Insert a user via API
        query_url = self.api_url + "/rpc/add_tribal_access_emails"
        response = requests.post(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "content-profile": TestAdminAPI.admin_api_version,
                "content-type": "application/json",
                "prefer": "params=single-object",
                # We can force a UUID locally that would not work when using api.data.gov,
                # because api.data.gov sets/overwrites this.
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
            json={"emails": all_emails},
        )
        self.assertEquals(response.text, "true")
        self.assertEquals(response.status_code, 200)

        # With the right permissions, I can check if things are present
        # via the associated view.
        query_url = self.api_url + "/tribal_access"
        response = requests.get(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "accept-profile": TestAdminAPI.admin_api_version,
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
        )

        found = 0
        for email in all_emails:
            for o in response.json():
                if email in o["email"]:
                    found += 1
        self.assertEquals(found, len(all_emails))

        # Now, remove the user, and find them absent.
        query_url = self.api_url + "/rpc/remove_tribal_access_emails"
        response = requests.post(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "content-profile": TestAdminAPI.admin_api_version,
                "content-type": "application/json",
                "prefer": "params=single-object",
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
            json={"emails": all_emails},
        )
        self.assertEquals(response.status_code, 200)

        query_url = self.api_url + "/tribal_access"
        response = requests.get(
            query_url,
            headers={
                "authorization": f"Bearer {self.encoded_jwt}",
                "accept-profile": TestAdminAPI.admin_api_version,
                "x-api-user-id": TestAdminAPI.api_user_uuid,
            },
            timeout=10,
        )

        found = 0
        for email in all_emails:
            for o in response.json():
                if email in o["email"]:
                    found += 1
        self.assertEquals(found, 0)

        self.admin_api_events_exist()
