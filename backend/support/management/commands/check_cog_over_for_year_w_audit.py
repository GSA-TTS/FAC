from django.core.management.base import BaseCommand
from django.db.models import Q

from audit.models.constants import STATUS
from support.cog_over_w_audit import compute_cog_over
from django.apps import apps

from config.settings import ENVIRONMENT


class Command(BaseCommand):
    help = """
    Analyze cog/over for 2022 / 2023 / 2024 / 2025 submissions in LOCAL environment only.
    Uses 20000 existing rows in Audit
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            help="Year(2022 or 2023 or 2024 or 2025)",
            type=str,
            default="2022",
        )

    def is_year_invalid(self, year):
        valid_years = ["2022", "2023", "2024", "2025"]
        return year not in valid_years

    def handle(self, *args, **options):
        if ENVIRONMENT != "LOCAL":
            print(f"Environment is not LOCAL, ENVIRONMENT={ENVIRONMENT}")
            return

        year = options.get("year")
        if self.is_year_invalid(year):
            print(f"Invalid year {year}.  Expecting 2022 / 2023 / 2024 / 2025")
            return

        audit_model = apps.get_model("audit.Audit")
        audits = audit_model.objects.filter(
            Q(audit_year=year)
            & (
                Q(submission_status=STATUS.SUBMITTED)
                | Q(submission_status=STATUS.DISSEMINATED)
            )
        )[:20000]
        print(f"Count of {year} submissions: {len(audits)}")
        processed = cog_mismatches = over_mismatches = 0

        for audit in audits:
            print(
                f"audit.report_id = {audit.report_id} \n",
            )
            cognizant_agency, oversight_agency = compute_cog_over(
                audit.audit["federal_awards"],
                audit.submission_status,
                audit.auditee_ein,
                audit.auditee_uei,
                audit.audit_year,
            )

            processed += 1
            if audit.cognizant_agency == "":
                audit.cognizant_agency = None
            if audit.oversight_agency == "":
                audit.oversight_agency = None
            if cognizant_agency != audit.cognizant_agency:
                cog_mismatches += 1
                print(
                    f"Cog mismatch. Calculated {cognizant_agency} Expected {audit.cognizant_agency}"
                )
                self.show_mismatch(audit)
            if oversight_agency != audit.oversight_agency:
                self.show_mismatch(audit)
                over_mismatches += 1
                print(
                    f"Oversight mismatch. Calculated {oversight_agency} Expected {audit.oversight_agency}"
                )
                self.show_mismatch(audit)
            if processed % 1000 == 0:
                print(
                    f"""
                    Processed {processed} rows so far.
                    Found {cog_mismatches} cog and {over_mismatches} over mismatches.
                    ..."""
                )
        print(
            f"""
                Processed all {processed} rows.
                Found {cog_mismatches} cog and {over_mismatches} over mismatches.
                """
        )

    def show_mismatch(self, audit):
        print(
            audit.auditee_ein,
            audit.auditee_uei,
            audit.cognizant_agency,
            audit.oversight_agency,
            audit.audit["federal_awards"]["total_amount_expended"],
        )
        for award in audit.audit["federal_awards"]["awards"]:
            print(
                "Award:",
                award["award_reference"],
                award["program"]["amount_expended"],
                award["program"]["federal_agency_prefix"],
                award["program"]["three_digit_extension"],
                award["direct_or_indirect_award"]["is_direct"],
            )
