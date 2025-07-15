import fac as f
import os

from django.test import TestCase


class FacTest(TestCase):
    def test_create_client(self):
        client = f.FAC()
        self.assertEqual(client.base, f.FAC_PRODUCTION)

    def test_create_query(self):
        client = f.FAC()
        # Params should be alpha sorted by the key.
        client.query("report_id", "eq", "2023-09-GSA-1234")
        client.query("audit_year", "eq", 2023)
        self.assertEqual(
            client.get_url(),
            "https://api.fac.gov/general?audit_year=eq.2023&report_id=eq.2023-09-GSA-1234",
        )

    def test_chaining(self):
        client = f.FAC()
        client.query("a", "b", "c").header("a", "b").header("d", "e")
        self.assertEqual(client.get_url(), "https://api.fac.gov/general?a=b.c")
        hs = f.headers_to_dict(client.headers)
        self.assertEqual(sorted(list(hs.keys())), ["a", "d"])
        self.assertEqual(sorted(list(hs.values())), ["b", "e"])

    def test_fetch_fail(self):
        client = f.FAC()
        client.param("a", "b")
        client.fetch()
        status = client.error_status()
        self.assertEqual(status["code"], "API_KEY_MISSING")

    def test_fetch(self):
        client = f.FAC()
        client.query("audit_year", "eq", 2023)
        client.api_key(os.getenv("FAC_API_KEY"))
        client.fetch()
        self.assertGreater(len(client.results()) > 30_000)
