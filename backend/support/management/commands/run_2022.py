from django.core.management.base import BaseCommand
from django.db.models.functions import Cast
from django.db.models import BigIntegerField, Q


from dissemination.models import General, FederalAward
from audit.models import SingleAuditChecklist, User
from support.models import CognizantAssignment

from config.settings import ENVIRONMENT


class Command(BaseCommand):
    help = """
    Analyze cog/over for 20122 submissions
    Beware! Deletes any existing rows in SingleAuditChecklist
    """

    def handle(self, *args, **kwargs):
        if ENVIRONMENT != "LOCAL":
            print(f"Environment is not LOCAL, ENVIRONMENT={ENVIRONMENT}")
            return

        initialize_db()
        gens = General.objects.annotate(
            amt=Cast("total_amount_expended", output_field=BigIntegerField())
        ).filter(Q(audit_year='2022'))
        print(f"Count of 2022 submissions: {len(gens)}")
        processed = cog_mismatches = over_mismatches = 0

        for gen in gens:
            sac = self.make_sac(gen)
            sac.submission_status = sac.STATUS.SUBMITTED
            sac.save()
            if not sac.cognizant_agency and not sac.oversight_agency:
                sac.assign_cog_over()
            processed += 1
            if gen.cognizant_agency != sac.cognizant_agency:
                cog_mismatches += 1
                print(f"Cog mismatch. Expected {gen.cognizant_agency}")
                self.show_mismatch(sac)
            if gen.oversight_agency != sac.oversight_agency:
                over_mismatches += 1
                print(f"Oversight mismatch. Expected {gen.oversight_agency}")
                self.show_mismatch(sac)
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

    def show_mismatch(self, sac):
        print(
            sac.ein,
            sac.auditee_uei,
            sac.cognizant_agency,
            sac.oversight_agency,
            sac.federal_awards["FederalAwards"]["total_amount_expended"],
        )
        # for award in sac.federal_awards["FederalAwards"]["federal_awards"]:
        #     print(
        #         "Award:",
        #         award["award_reference"],
        #         award["program"]["amount_expended"],
        #         award["program"]["federal_agency_prefix"],
        #         award["program"]["three_digit_extension"],
        #         award["direct_or_indirect_award"]["is_direct"],
        #     )

    def make_sac(self, gen: General):
        general_information = {
            "auditee_fiscal_period_start": "2022-11-01",
            "auditee_fiscal_period_end": "2023-11-01",
            "met_spending_threshold": True,
            "is_usa_based": True,
        }
        general_information["ein"] = gen.auditee_ein
        general_information["auditee_uei"] = gen.auditee_uei
        federal_awards = self.make_awards(gen)
        sac = SingleAuditChecklist.objects.create(
            submitted_by=User.objects.first(),
            submission_status="in_progress",
            general_information=general_information,
            federal_awards=federal_awards,
        )
        return sac

    def make_awards(self, gen: General):
        awards = {
            "FederalAwards": {
                "auditee_uei": gen.auditee_uei,
                "federal_awards": [],
                "total_amount_expended": gen.amt,
            }
        }
        cfdas = FederalAward.objects.annotate(
            amt=Cast("amount_expended", output_field=BigIntegerField())
        ).filter(report_id=gen.report_id)
        for cfda in cfdas:
            awards["FederalAwards"]["federal_awards"].append(
                {
                    "award_reference": cfda.award_reference,
                    "program": {
                        "program_name": cfda.federal_program_name,
                        "amount_expended": cfda.amt,
                        "federal_agency_prefix": cfda.federal_agency_prefix,
                        "three_digit_extension": cfda.federal_award_extension,
                    },
                    "direct_or_indirect_award": {"is_direct": cfda.is_direct},
                },
            )
        return awards


def initialize_db():
    """
    This will delete existing data, and should only be run in a dev env
    """
    SingleAuditChecklist.objects.all().delete()
    CognizantAssignment.objects.all().delete()
    User.objects.get_or_create(
        username="foo",
        email="g22.foobar.com",
    )
