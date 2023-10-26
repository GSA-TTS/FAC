from django.test import TestCase

from model_bakery import baker

from .wb_generator import generate_workbooks
from .models import ELECAUDITHEADER, ELECAUDITS


class WbGegeratorTestCase(TestCase):
    def test_submission_with_gen_and_awards(self):
        audit_year = "2021"
        dbkey = "10001"
        baker.make(ELECAUDITHEADER, AUDITYEAR=audit_year, DBKEY=dbkey).save()
        baker.make(ELECAUDITS, AUDITYEAR=audit_year, DBKEY=dbkey).save()
        baker.make(ELECAUDITS, AUDITYEAR=audit_year, DBKEY=dbkey).save()
        result = generate_workbooks(audit_year, dbkey)
        wb_ref = result.get("Workbook")
        self.assertIsNotNone(wb_ref)
