from django.core.management.base import BaseCommand
from django.db.models.functions import Cast
from django.db.models import BigIntegerField


from dissemination.hist_models.census_2022 import CensusGen22, CensusCfda22
from audit.models import SingleAuditChecklist, User
from support.models import CognizantAssignment


class Command(BaseCommand):
    help = """
    Analyze cog/over for 20122 submissions
    Beware! Deletes any existing rows in SingleAuditChecklist
    """

    def handle(self, *args, **kwargs):
        initialize_db()
        gens = CensusGen22.objects.annotate(
            amt=Cast("totfedexpend", output_field=BigIntegerField())
        ).all()
        print(f"Count of 2022 submissions: {len(gens)}")
        processed = cog_mismatches = over_mismatches = 0

        for gen in gens:
            sac = self.make_sac(gen)
            sac.submission_status = sac.STATUS.SUBMITTED
            sac.save()
            processed += 1
            if gen.cogagency != sac.cognizant_agency:
                cog_mismatches += 1
                print(f"Cog mismatch. Expected {gen.cogagency}")
                self.show_mismatch(sac)
            if gen.oversightagency != sac.oversight_agency:
                over_mismatches += 1
                print(f"Oversight mismatch. Expected {gen.oversightagency}")
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
        for award in sac.federal_awards["FederalAwards"]["federal_awards"]:
            print(
                "Award:",
                award["award_reference"],
                award["program"]["amount_expended"],
                award["program"]["federal_agency_prefix"],
                award["program"]["three_digit_extension"],
                award["direct_or_indirect_award"]["is_direct"],
            )

    def make_sac(self, gen: CensusGen22):
        general_information = {
            "auditee_fiscal_period_start": "2022-11-01",
            "auditee_fiscal_period_end": "2023-11-01",
            "met_spending_threshold": True,
            "is_usa_based": True,
        }
        general_information["ein"] = gen.ein
        general_information["auditee_uei"] = gen.uei
        federal_awards = self.make_awards(gen)
        sac = SingleAuditChecklist.objects.create(
            submitted_by=User.objects.first(),
            submission_status="in_progress",
            general_information=general_information,
            federal_awards=federal_awards,
        )
        return sac

    def make_awards(self, gen: CensusGen22):
        awards = {
            "FederalAwards": {
                "auditee_uei": gen.uei,
                "federal_awards": [],
                "total_amount_expended": gen.amt,
            }
        }
        cfdas = CensusCfda22.objects.annotate(
            amt=Cast("amount", output_field=BigIntegerField())
        ).filter(ein=gen.ein, dbkey=gen.dbkey)
        for cfda in cfdas:
            awards["FederalAwards"]["federal_awards"].append(
                {
                    "award_reference": cfda.index,
                    "program": {
                        "program_name": cfda.cfdaprogramname,
                        "amount_expended": cfda.amt,
                        "federal_agency_prefix": cfda.cfda[:2],
                        "three_digit_extension": cfda.cfda[2:],
                    },
                    "direct_or_indirect_award": {"is_direct": cfda.direct},
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
