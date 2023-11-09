from collections import namedtuple
from fs.memoryfs import MemoryFS

from audit.fixtures.excel import FORM_SECTIONS
from .sac_creation import _make_excel_file, _post_upload_workbook
from c2g.models import ELECAUDITHEADER as Gen


import logging

from .federal_awards import generate_federal_awards

SectionInfo = namedtuple("SectionInfo", ["func", "filename"])

sections = {
    # FORM_SECTIONS.ADDITIONAL_EINS: generate_additional_eins,
    # FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    # FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    # FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: generate_corrective_action_plan,
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: SectionInfo(
        generate_federal_awards, "federal-awards-{}.xlsx"
    ),
    # FORM_SECTIONS.FINDINGS_TEXT: generate_findings_text,
    # FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: generate_findings,
    # FORM_SECTIONS.NOTES_TO_SEFA: generate_notes_to_sefa,
    # FORM_SECTIONS.SECONDARY_AUDITORS: generate_secondary_auditors,
}

# filenames = {
#     FORM_SECTIONS.ADDITIONAL_EINS: "additional-eins-{}.xlsx",
#     FORM_SECTIONS.ADDITIONAL_UEIS: "additional-ueis-{}.xlsx",
#     FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: "corrective-action-plan-{}.xlsx",
#     FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: "federal-awards-{}.xlsx",
#     FORM_SECTIONS.FINDINGS_TEXT: "audit-findings-text-{}.xlsx",
#     FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: "audit-findings-{}.xlsx",
#     FORM_SECTIONS.NOTES_TO_SEFA: "notes-to-sefa-{}.xlsx",
#     FORM_SECTIONS.SECONDARY_AUDITORS: "secondary-auditors-{}.xlsx",
# }

logger = logging.getLogger(__name__)


def make_loader(gen: Gen):
    def _loader(workbook_generator, file_name, sac, section):
        dbkey = gen.DBKEY
        with MemoryFS() as mem_fs:
            file_name = file_name.format(dbkey)
            outfile = mem_fs.openbin(file_name, mode="w")
            (wb, json) = workbook_generator(gen, outfile)
            outfile.close()
            outfile = mem_fs.openbin(file_name, mode="r")
            excel_file = _make_excel_file(file_name, outfile)
            _post_upload_workbook(sac, section, excel_file)
            outfile.close()
        return (wb, json, file_name)

    return _loader
