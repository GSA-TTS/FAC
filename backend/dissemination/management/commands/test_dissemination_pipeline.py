from django.core.management.base import BaseCommand
from dissemination import api_versions
from model_bakery import baker
import json
import os
import sys
from django.test import Client

from audit.test_views import (
    MockHttpResponse,
    _mock_login_and_scan
)

from audit.validators import _scan_file

from audit.fixtures.excel import (
    FINDINGS_TEXT_TEMPLATE,
    FINDINGS_TEXT_ENTRY_FIXTURES,
    FORM_SECTIONS,
)
from django.conf import settings
from openpyxl import load_workbook
from django.urls import reverse
import unittest

def test_workbook(filename, section, client):
    print(f'testing {filename}')
    tc = unittest.TestCase()

    xlsx_file = open(filename, 'rb')
    mock_scanfile = _scan_file(xlsx_file)    
    sac = _mock_login_and_scan(client, mock_scanfile)

    xlsx_file.seek(0)
    response = client.post(
        reverse(
            f"audit:{section}",
            kwargs={
                "report_id": sac.report_id,
                "form_section": section,
            },
        ),
        data={"FILES": xlsx_file},
    )
    print(response.content)
    tc.assertEqual(response.status_code, 302)
    return True

class Command(BaseCommand):
    help = """
    Creates workbooks for testing from Census data, and then runs it through the app.
    """

    def handle(self, *args, **kwargs):
        basepath = os.path.join(settings.DATA_FIXTURES, 'historic')
        for dbkey in os.listdir(basepath):
            print(f'Handling {dbkey}')
            client = Client()

            test_workbook(os.path.join(basepath, dbkey, f'federal-awards-{dbkey}.xlsx'), 
                          FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED, 
                          client)
