import argparse
import openpyxl as pyxl
import sys

from django.core.management.base import BaseCommand
from django.conf import settings
from users.models import User
from audit.fixtures.excel import FORM_SECTIONS
from django.apps import apps

import logging
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser()

from audit.fixtures.single_audit_checklist import (
    _post_upload_workbook,
    _create_sac,
    _make_excel_file
)

from fs.memoryfs import MemoryFS
from audit.management.commands.workbooks.notes_to_sefa import generate_notes_to_sefa

def setup_sac(user, test_name):
    logger.info(f"Creating a SAC object for {user}, {test_name}")
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
    sac = SingleAuditChecklist.objects.filter(
        submitted_by=user, general_information__auditee_name=test_name
    ).first()
    logger.info(sac)
    if sac is None:
        sac = _create_sac(user, test_name)
    return sac

class Command(BaseCommand):
   
    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument('workbook', type=str)
        parser.add_argument('dbkey', type=str)

    def handle(self, *args, **options):
        if 'email' not in options:
            print("Pass an email address, workbook name, and dbkey.")
            sys.exit()

        try:
            user = User.objects.get(email=options['email'])
        except User.DoesNotExist:
            logger.info("No user found for %s, have you logged in once?", options['email'])
            return
        
        if options['workbook'] == "notes_to_sefa":
            with MemoryFS() as mem_fs:
                outfile = mem_fs.openbin('notes.xlsx', mode='w')
                (wb, json) = generate_notes_to_sefa(options['dbkey'], outfile)
                sac = setup_sac(user, "Testing Notes to SEFA")
                outfile.close()
                outfile = mem_fs.openbin('notes.xlsx', mode='r')
                excel_file = _make_excel_file("notes.xlsx", outfile)
                _post_upload_workbook(sac, user, FORM_SECTIONS.NOTES_TO_SEFA, excel_file)
