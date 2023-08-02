from django.core.management.base import BaseCommand
from dissemination import api_versions

from model_bakery import baker
import json
import os
import sys
from django.test import Client
import re

from audit.test_views import (
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
    # Rewind the file, because _scan_file unwound it.
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

mapping = {
    FORM_SECTIONS.ADDITIONAL_UEIS : 'additional-ueis-{0}.xlsx',
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN : 'captext-{0}.xlsx',
    # MCJ FIXME the validation or mapping for secondary auditors is broken.
    # FORM_SECTIONS.SECONDARY_AUDITORS : 'cpas-{0}.xlsx',
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED : 'federal-awards-{0}.xlsx',
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE : 'findings-{0}.xlsx',
    FORM_SECTIONS.FINDINGS_TEXT : 'findings-text-{0}.xlsx',
    # The form needs to have single cells formatted LtoR, and 
    # it appears that there is data not coming through to the XLSX file.
    # FORM_SECTIONS.NOTES_TO_SEFA : 'notes-{0}.xlsx'
}

def big(s):
    print("##########################################################")
    print(f"# {s}")
    print("##########################################################")
    

class Command(BaseCommand):
    help = """
    Creates workbooks for testing from Census data, and then runs it through the app.
    """

    def handle(self, *args, **kwargs):
        basepath = os.path.join(settings.DATA_FIXTURES, 'historic')
        for dbkey in os.listdir(basepath):
            # Only handle directories that look like DBKEYs, or 
            # a sack of numbers.
            if re.search('^[0-9]+$', dbkey):
                big(f'Handling {dbkey}')
                client = Client()
                for section, file in mapping.items():
                    big(file.format(dbkey))
                    test_workbook(os.path.join(basepath, dbkey, file.format(dbkey)), 
                                section, 
                                client)
                # Set the certification flags
                # Invoke cross-validation
                # Trigger dissemination/ETL
                # Check against the JSON source of truth
