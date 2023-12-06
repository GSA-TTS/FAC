from django.test import TestCase

from dissemination.export import export_to_workbook
from dissemination.models import General

from model_bakery import baker


class ExportTests(TestCase):
    def test(self):
        general = baker.make(General, _quantity=100)

        f = export_to_workbook([g.report_id for g in general])
        