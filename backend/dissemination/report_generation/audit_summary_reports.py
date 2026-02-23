import datetime
import io
import logging
import time

from audit.models import Audit
from audit.models.constants import ORGANIZATION_TYPE
from dissemination.report_generation.excel.coversheets import (
    insert_dissemination_coversheet,
)
from dissemination.report_generation.excel.utils import REPORT_FORMAT, create_workbook
from dissemination.summary_reports import insert_precert_coversheet

logger = logging.getLogger(__name__)

restricted_model_names = ("captext", "findingtext", "note")


def generate_audit_summary_report(
    report_ids, include_private=False, pre_submission=False
):
    t0 = time.time()
    data, tgad = _gather_audit_data(report_ids, include_private)
    workbook, tcw = create_workbook(data)

    tht = 0
    if pre_submission:
        insert_precert_coversheet(workbook)
    else:
        has_tribal, tht = _contains_private_tribal(report_ids)
        insert_dissemination_coversheet(workbook, has_tribal, include_private)

    filename, workbook_bytes, tpw = _prepare_workbook_for_download(workbook)
    t1 = time.time()
    logger.info(
        f"SUMMARY_REPORTS generate_summary_report\n\ttotal: {t1 - t0} has_tribal: {tht} audit_data: {tgad} create_workbook: {tcw} prepare_workbook: {tpw}"
    )
    return filename, workbook_bytes


def _prepare_workbook_for_download(workbook):

    t0 = time.time()
    now = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S")
    filename = f"audit-fac-summary-report-{now}.xlsx"

    # Save the workbook directly to a BytesIO object
    workbook_bytes = io.BytesIO()
    workbook.save(workbook_bytes)
    workbook_bytes.seek(0)

    t1 = time.time()
    return filename, workbook_bytes, t1 - t0


def _gather_audit_data(report_ids, include_private):
    """
    Given a set of report IDs, fetch the disseminated data for each and assemble into a dictionary with the following shape:

    {
        general: {
            field_names: [],
            entries: [],
        },
        federal_award: {
            field_names: [],
            entries: [],
        },
        ...
    }
    """
    t0 = time.time()
    report_ids = set(report_ids)
    data = _initialize_data()

    audits = Audit.objects.filter(report_id__in=report_ids)
    for audit in audits:
        _add_entries_from_audit(audit, data, include_private)

    return data, time.time() - t0


def _initialize_data():
    data = {}
    for mapping in REPORT_FORMAT:
        data[mapping.sheet_name] = {
            "field_names": mapping.column_names,
            "entries": [],
        }
    return data


def _add_entries_from_audit(audit, data, include_private):
    for mapping in REPORT_FORMAT:
        if not include_private and mapping.sheet_name in restricted_model_names:
            continue

        entries = mapping.parse_audit_to_entries(audit)
        if entries:
            data[mapping.sheet_name]["entries"].extend(entries)


def _contains_private_tribal(report_ids):
    t0 = time.time()
    has_tribal = (
        Audit.objects.filter(
            report_id__in=report_ids,
            organization_type=ORGANIZATION_TYPE.TRIBAL,
            is_public=False,
        ).count()
        > 0
    )
    t1 = time.time()
    return has_tribal, t1 - t0
