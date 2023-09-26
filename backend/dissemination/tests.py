from django.test import TestCase

import os
from datetime import datetime


import jwt
import requests

from config import settings

api_schemas = ["api_v1_0_0"]


class APIViewTests(TestCase):
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
