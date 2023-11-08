from fs.memoryfs import MemoryFS

from .sac_creation import (
    _post_upload_workbook,
    _make_excel_file,
    _create_sac,
)

from c2g.models import ELECAUDITHEADER as Gen
from audit.models import SingleAuditChecklist

from audit.fixtures.excel import FORM_SECTIONS


# from dissemination.workbooklib.notes_to_sefa import generate_notes_to_sefa
from .federal_awards import federal_awards_to_json
from .findings import generate_findings
from .findings_text import generate_findings_text

from .corrective_action_plan import generate_corrective_action_plan

# from dissemination.workbooklib.additional_ueis import generate_additional_ueis
# from dissemination.workbooklib.additional_eins import generate_additional_eins
# from dissemination.workbooklib.secondary_auditors import generate_secondary_auditors

# from model_bakery import baker
# from django.contrib.auth import get_user_model

import logging

sections = {
    # FORM_SECTIONS.ADDITIONAL_EINS: generate_additional_eins,
    # FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    # FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    # FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: generate_corrective_action_plan,
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: federal_awards_to_json,
    # FORM_SECTIONS.FINDINGS_TEXT: generate_findings_text,
    # FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: generate_findings,
    # FORM_SECTIONS.NOTES_TO_SEFA: generate_notes_to_sefa,
    # FORM_SECTIONS.SECONDARY_AUDITORS: generate_secondary_auditors,
}

json_field_names = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: "federal-awards-{}.xlsx",
}
filenames = {
    # FORM_SECTIONS.ADDITIONAL_EINS: "additional-eins-{}.xlsx",
    # FORM_SECTIONS.ADDITIONAL_UEIS: "additional-ueis-{}.xlsx",
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: "corrective-action-plan-{}.xlsx",
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: "federal-awards-{}.xlsx",
    FORM_SECTIONS.FINDINGS_TEXT: "audit-findings-text-{}.xlsx",
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: "audit-findings-{}.xlsx",
    # FORM_SECTIONS.NOTES_TO_SEFA: "notes-to-sefa-{}.xlsx",
    # FORM_SECTIONS.SECONDARY_AUDITORS: "secondary-auditors-{}.xlsx",
}

logger = logging.getLogger(__name__)


def setup_sac(user, gen: Gen):
    logger.info(f"Creating a SAC object for {user}, {gen.AUDITEENAME}")
    sac = _create_sac(user, gen)
    return sac


def workbook_loader(user, sac: SingleAuditChecklist, audit_year, dbkey):
    def _loader(workbook_generator, section):
        with MemoryFS() as mem_fs:
            filename = filenames[section].format(dbkey)
            outfile = mem_fs.openbin(filename, mode="w")
            (wb, json) = workbook_generator(sac, dbkey, audit_year, outfile)
            outfile.close()
            # outfile = mem_fs.openbin(filename, mode="r")
            # excel_file = _make_excel_file(filename, outfile)
            # if user:
            #     _post_upload_workbook(sac, user, section, excel_file)
            # outfile.close()
        return (wb, json, filename)

    return _loader
