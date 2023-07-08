from django.test import TestCase
from django.db import connection

import requests
from model_bakery import baker

from config import settings
from .models import General


class APIViewTests(TestCase):
    def setUp(self):
        self.api_url = settings.POSTGREST.get("URL")

    def test_postgrest_url_is_reachable(self):
        response = requests.get(self.api_url, timeout=10)
        self.assertAlmostEquals(response.status_code, 200)

    def test_general_returns_data(self):
        uei = "UCL2KRV93"

        general = baker.make(General, auditee_uei=uei, is_public=True)
        general.save()
        with connection.cursor() as cursor:
            # TODO: Need a better way. Creating the views here as the data is in a temporary test databasse
            for file in [
                "init_api_db.sql",
                "db_views.sql",
            ]:
                filename = f"dissemination/api/{file}"
                sql = open(filename, "r").read()
                cursor.execute(sql)

            cursor.execute("SELECT auditee_uei FROM api.vw_general")
            data = cursor.fetchall()
            print("response vw_general:", data[0][0])
            self.assertEquals(data[0][0], uei)
