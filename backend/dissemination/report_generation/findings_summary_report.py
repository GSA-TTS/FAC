from datetime import datetime, timedelta, time, timezone
from dissemination.models import General, Finding, FederalAward
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import io


class FindingsReport:
    pass


# Return a dict that can
# be turned into a sheet.
# auditee_name
# auditee_uei
# award_reference
# reference_number
# aln
# cog_over
# federal_program_name
# amount_expended
# is_direct
# is_major
# is_passthrough_award
# passthrough_amount
# is_modified_opinion
# is_other_matters
# is_material_weakness
# is_significant_deficiency
# is_other_findings
# is_questioned_costs
# is_repeat_finding
# prior_finding_ref_numbers
def _get_findings_for_agency_number(report_ids):
    def _get_findings(agency_number):
        # Start with the objects with the right report IDs
        gobjs = General.objects.filter(report_id__in=report_ids)
        uniq = set()
        results = []
        for gobj in gobjs:
            # Now, we have to find the awards for the given agency number.
            # awardobjs = FederalAward.objects.filter(
            #     report_id=gobj.report_id, federal_agency_prefix=agency_number
            # )
            # But, there is also a question of
            # First, see if we have any findings for this report.
            # If not, we won't be building any results.
            fobjs = Finding.objects.filter(report_id=gobj.report_id)
            for fobj in fobjs:
                d = None
                # Now, get the award object associated with this finding.
                try:
                    awardobj = FederalAward.objects.get(
                        report_id=gobj.report_id,
                        award_reference=fobj.award_reference,
                        federal_agency_prefix=agency_number,
                    )
                    if (
                        gobj.report_id,
                        fobj.reference_number,
                        awardobj.award_reference,
                    ) not in uniq:
                        uniq.add(
                            (
                                gobj.report_id,
                                fobj.reference_number,
                                awardobj.award_reference,
                            )
                        )
                        d = {}
                        d["report_id"] = gobj.report_id
                        d["auditee_name"] = gobj.auditee_name
                        d["auditee_uei"] = gobj.auditee_uei
                        d["award_reference"] = fobj.award_reference
                        d["reference_number"] = fobj.reference_number
                        d["aln"] = (
                            f"{awardobj.federal_agency_prefix}.{awardobj.federal_award_extension}"
                        )
                        d["cog_over"] = (
                            f"COG-{gobj.cognizant_agency}"
                            if gobj.cognizant_agency
                            else f"OVER-{gobj.oversight_agency}"
                        )
                        d["federal_program_name"] = awardobj.federal_program_name
                        d["amount_expended"] = awardobj.amount_expended
                        d["is_direct"] = awardobj.is_direct
                        d["is_major"] = awardobj.is_major
                        d["is_passthrough_award"] = awardobj.is_passthrough_award
                        d["passthrough_amount"] = awardobj.passthrough_amount
                        d["is_modified_opinion"] = fobj.is_modified_opinion
                        d["is_other_matters"] = fobj.is_other_matters
                        d["is_material_weakness"] = fobj.is_material_weakness
                        d["is_significant_deficiency"] = fobj.is_significant_deficiency
                        d["is_other_findings"] = fobj.is_other_findings
                        d["is_questioned_costs"] = fobj.is_questioned_costs
                        d["is_repeat_finding"] = fobj.is_repeat_finding
                        d["prior_finding_ref_numbers"] = fobj.prior_finding_ref_numbers
                except:
                    pass
                if d:
                    results.append(d)
        return results

    return _get_findings


# Takes a list of report IDs and returns a set of agency numbers
def get_unique_agency_numbers(report_ids):
    alns = set()
    # We want the unique agency numbers from the awards that have findings
    fobjs = Finding.objects.filter(report_id__in=report_ids)
    for fobj in fobjs:
        awards = FederalAward.objects.filter(
            report_id=fobj.report_id, award_reference=fobj.award_reference
        )
        for award in awards:
            alns.add(award.federal_agency_prefix)
    return sorted(alns)


def get_unique_cog_overs(report_ids):
    cogovers = set()
    # We want the unique agency numbers from the awards that have findings
    gobjs = General.objects.filter(report_id__in=report_ids)
    for gobj in gobjs:
        if gobj.cognizant_agency:
            cogovers.add(gobj.cognizant_agency)
        else:
            cogovers.add(gobj.oversight_agency)
    return sorted(cogovers)


def adjust_columns(ws):
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:  # Necessary to avoid error on empty cells
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column].width = adjusted_width
    return ws


def _add_sheets(wb, iter, query):
    # iter_value will likely be an integer
    for iter_value in iter:
        ws = wb.create_sheet(f"{iter_value}")
        # Put headers on the sheets
        for d in query(iter_value):
            ws.append(list(d.keys()))
            break
        # Now the values.
        for d in query(iter_value):
            ws.append(list(d.values()))
        adjust_columns(ws)


def convert_bools(res):
    for k in res.keys():
        if res[k] in ["Y", "TRUE", "T", "YES"]:
            res[k] = True
        elif res[k] in ["N", "NO", "FALSE", "F"]:
            res[k] = False
    return res


yes_fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")


def _cleanup_sheet(ws):
    boolean_columns = ["J", "K", "L", "M", "O", "P", "Q", "R", "S", "T"]
    # Trys to go through a sheet and
    # 1. Hyperlink all the report ids,
    # 2. Cleanup all the booleans.
    # The columns are hard-coded to the order
    # they appear from the dump into the sheet.
    try:
        report_ids = []
        for cell in ws["A"]:
            if ("GSAFAC" in cell.value) or ("CENSUS" in cell.value):
                report_ids.append(cell.value)
                cell.hyperlink = (
                    f"https://app.fac.gov/dissemination/report/pdf/{cell.value}"
                )
            else:
                pass
        for ndx, cell in enumerate(ws["B"][1:]):
            cell.hyperlink = (
                f"https://app.fac.gov/dissemination/summary/{report_ids[ndx]}"
            )
        for bool_column in boolean_columns:
            for cell in ws[bool_column]:
                if cell.value in [1, "Y"]:
                    cell.value = "YES"
                elif cell.value in [0, "N"]:
                    cell.value = "NO"
                else:
                    pass
        for bool_column in boolean_columns:
            for cell in ws[bool_column]:
                if cell.value == "YES":
                    cell.fill = yes_fill
    except:
        pass


def _remove_default_sheet(wb):
    # Try removing the default sheet.
    try:
        del wb["Sheet"]
    except:
        pass


def _gather_report_data(report_ids=None, start_date=None, end_date=None):
    # We start by getting the report ids in this range.
    if report_ids == None:
        report_ids = General.objects.filter(
            fac_accepted_date__gte=start_date, fac_accepted_date__lt=end_date
        ).values_list("report_id")
    # Now, lets start building our workbook. It's an iterative
    # set of queries.
    wb = Workbook()
    _add_sheets(
        wb,
        get_unique_agency_numbers(report_ids),
        _get_findings_for_agency_number(report_ids),
    )
    # Hyperlink the report IDs
    for sheet in wb.worksheets:
        _cleanup_sheet(sheet)

    _remove_default_sheet(wb)

    return wb


def _prepare_workbook_for_download(workbook, start_date, end_date):

    now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    workbook_filename = f"findings-summary-{start_date.strftime('%Y-%m-%d')}-to-{end_date.strftime('%Y-%m-%d')}-{now}.xlsx"

    # Save the workbook directly to a BytesIO object
    workbook_bytes = io.BytesIO()
    workbook.save(workbook_bytes)
    workbook_bytes.seek(0)

    return workbook_filename, workbook_bytes


# This generates reports of the form that we generated
# while advanced search was offline.
#
# These reports *only* contain public data, and therefore
# do not have access control concerns.
def generate_findings_summary_report(report_ids=None, start_date=None, end_date=None):
    # We're going to either use the given dates, or
    # we're going to assume now until two weeks ago.
    if start_date == None or end_date == None:
        # Monday is 0, Sunday is 6
        # I want to get a two-week window from Sat->Sun->Sat->Sun
        # where I'll go back in time to the most recent Sunday
        day_ndx = datetime.today().weekday()
        # First, subtract some
        today = datetime.now()
        get_to_sunday = timedelta(days=(day_ndx + 1))
        sunday = today - get_to_sunday
        two_weeks_ago = timedelta(days=14)
        # Get midnight on the first Sunday, and almost midnight on the last Saturday
        start_date = sunday - two_weeks_ago
        start_date = datetime.combine(start_date, time.min)
        end_date = sunday - timedelta(days=1)
        end_date = datetime.combine(end_date, time.max)
        print(f"Date range: {start_date}, {end_date}")
    elif isinstance(start_date, str) and isinstance(end_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = datetime.combine(start_date, time.min)
        end_date = datetime.combine(end_date, time.max)
    else:
        start_date = datetime.combine(start_date, time.min)
        end_date = datetime.combine(end_date, time.max)

    wb = _gather_report_data(report_ids, start_date, end_date)
    # workbook_filename = f"{start_date.strftime('%Y-%m-%d')}-to-{end_date.strftime('%Y-%m-%d')}-findings.xlsx"
    # wb.save(workbook_filename)
    (filename, workbook_bytes) = _prepare_workbook_for_download(
        wb, start_date, end_date
    )
    return filename, workbook_bytes
