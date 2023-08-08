import argparse

from django.core.management.base import BaseCommand
from users.models import User
from audit.fixtures.excel import FORM_SECTIONS
from django.apps import apps

import datetime
import logging

logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser()

from audit.management.commands.workbooks.sac_creation import (
    _post_upload_workbook,
    _create_test_sac,
    _make_excel_file,
)

from fs.memoryfs import MemoryFS
from audit.management.commands.workbooks.notes_to_sefa import generate_notes_to_sefa
from audit.management.commands.workbooks.federal_awards import generate_federal_awards
from audit.management.commands.workbooks.findings import generate_findings
from audit.management.commands.workbooks.findings_text import generate_findings_text
from audit.management.commands.workbooks.corrective_action_plan import generate_corrective_action_plan


def setup_sac(user, test_name, dbkey):
    logger.info(f"Creating a SAC object for {user}, {test_name}")
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
    sac = SingleAuditChecklist.objects.filter(
        submitted_by=user, general_information__auditee_name=test_name
    ).first()
    logger.info(sac)
    if sac is None:
        sac = _create_test_sac(user, test_name, dbkey)
    return sac


def workbook_loader(user, sac, dbkey, entity_id):
    def _loader(workbook_generator, section):
        json = None
        with MemoryFS() as mem_fs:
            filename = "workbook.xlsx"
            outfile = mem_fs.openbin(filename, mode="w")
            (_, json) = workbook_generator(dbkey, outfile)
            outfile.close()
            outfile = mem_fs.openbin(filename, mode="r")
            excel_file = _make_excel_file(filename, outfile)
            _post_upload_workbook(sac, user, section, excel_file)
            outfile.close()
        return json

    return _loader


sections = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: generate_federal_awards,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: generate_findings,
    FORM_SECTIONS.FINDINGS_TEXT: generate_findings_text,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: generate_corrective_action_plan,
    FORM_SECTIONS.NOTES_TO_SEFA: generate_notes_to_sefa,
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, required=True)
        parser.add_argument("--dbkey", type=str, required=True)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(email=options["email"])
        except User.DoesNotExist:
            logger.info(
                "No user found for %s, have you logged in once?", options["email"]
            )
            return
        entity_id = "DBKEY {dbkey} {date:%Y_%m_%d_%H_%M_%S}".format(
            dbkey=options["dbkey"], date=datetime.datetime.now()
        )
        sac = setup_sac(user, entity_id, options["dbkey"])
        loader = workbook_loader(user, sac, options["dbkey"], entity_id)
        json_test_tables = []
        for section, fun in sections.items():
            json_test_tables.append(loader(fun, section))
