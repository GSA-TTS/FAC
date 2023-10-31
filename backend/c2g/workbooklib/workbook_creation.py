from fs.memoryfs import MemoryFS

from c2g.workbooklib.sac_creation import (
    _post_upload_workbook,
    _make_excel_file,
    _create_test_sac,
)
from audit.fixtures.excel import FORM_SECTIONS
from django.apps import apps


from c2g.workbooklib.notes_to_sefa import generate_notes_to_sefa
from c2g.workbooklib.federal_awards import generate_federal_awards
from c2g.workbooklib.findings import generate_findings
from c2g.workbooklib.findings_text import generate_findings_text
from c2g.workbooklib.corrective_action_plan import (
    generate_corrective_action_plan,
)
from c2g.workbooklib.additional_ueis import generate_additional_ueis
from c2g.workbooklib.additional_eins import generate_additional_eins
from c2g.workbooklib.secondary_auditors import generate_secondary_auditors

from model_bakery import baker
from django.contrib.auth import get_user_model

import logging

sections = {
    FORM_SECTIONS.ADDITIONAL_EINS: generate_additional_eins,
    FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: generate_corrective_action_plan,
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: generate_federal_awards,
    FORM_SECTIONS.FINDINGS_TEXT: generate_findings_text,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: generate_findings,
    FORM_SECTIONS.NOTES_TO_SEFA: generate_notes_to_sefa,
    FORM_SECTIONS.SECONDARY_AUDITORS: generate_secondary_auditors,
}

filenames = {
    FORM_SECTIONS.ADDITIONAL_EINS: "additional-eins-{}.xlsx",
    FORM_SECTIONS.ADDITIONAL_UEIS: "additional-ueis-{}.xlsx",
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: "corrective-action-plan-{}.xlsx",
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: "federal-awards-{}.xlsx",
    FORM_SECTIONS.FINDINGS_TEXT: "audit-findings-text-{}.xlsx",
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: "audit-findings-{}.xlsx",
    FORM_SECTIONS.NOTES_TO_SEFA: "notes-to-sefa-{}.xlsx",
    FORM_SECTIONS.SECONDARY_AUDITORS: "secondary-auditors-{}.xlsx",
}

logger = logging.getLogger(__name__)


def setup_sac(user, test_name, dbkey):
    logger.info(f"Creating a SAC object for {user}, {test_name}")
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
    if user:
        sac = SingleAuditChecklist.objects.filter(
            submitted_by=user, general_information__auditee_name=test_name
        ).first()
    else:
        sac = SingleAuditChecklist()
        User = get_user_model()
        user = baker.make(User)
        sac.submitted_by = user
        sac.general_information = {}
        sac.general_information["auditee_name"] = test_name

    logger.info(sac)
    if sac is None:
        sac = _create_test_sac(user, test_name, dbkey)
    return sac


def workbook_loader(user, sac, dbkey, year, entity_id):
    def _loader(workbook_generator, section):
        with MemoryFS() as mem_fs:
            filename = filenames[section].format(dbkey)
            outfile = mem_fs.openbin(filename, mode="w")
            (wb, json) = workbook_generator(dbkey, year, outfile)
            outfile.close()
            outfile = mem_fs.openbin(filename, mode="r")
            excel_file = _make_excel_file(filename, outfile)
            if user:
                _post_upload_workbook(sac, user, section, excel_file)
            outfile.close()
        return (wb, json, filename)

    return _loader
