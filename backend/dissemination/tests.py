from django.test import TestCase
from dissemination import api_versions

import os
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from math import floor


import jwt
import requests

from config import settings
from .models import FederalAward, Finding, FindingText, General

api_schemas = ["api_v1_0_0_beta"]


class APIViewTests(TestCase):
    def setUp(self):
        self.api_url = settings.POSTGREST.get("URL")

    def create_payload(self, role="api_fac_gov", expires=6):
        six_months = datetime.today() + relativedelta(months=+expires)
        payload = {
            # PostgREST only cares about the role.
            "role": role,
            "created": datetime.today().isoformat(),
            "expires": six_months.isoformat(),
            "exp": floor(six_months.timestamp()),
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
