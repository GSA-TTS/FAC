from django.core.management.base import BaseCommand
from django.db.models.functions import Cast
from django.db.models import BigIntegerField

from dissemination.hist_models.census_2022 import CensusGen22, CensusCfda22
from audit.models import SingleAuditChecklist
from support.cog_over import compute_cog_over

class Command(BaseCommand):
    help = """
    Analyze cog/over for 20122 submissions
    """

    def handle(self, *args, **kwargs):
        gens = CensusGen22.objects.annotate(
            amt=Cast("totfedexpend", output_field=BigIntegerField())).all()
        print(f"Count of 2022 submissions: {len(gens)}")
        processed = mismatches = 0
        for gen in gens:
            sac = self.make_sac(gen)
            (cognizant_agency, oversight_agency) = compute_cog_over(sac)
            processed += 1
            if ( (cognizant_agency and cognizant_agency != sac.cognizant_agency) or
                (oversight_agency and oversight_agency != sac.oversight_agency)):
                self.show_mismatch(sac)
                mismatches += 1
            if processed % 1000 == 0:
                print(f'Processed {processed} rows. Found {mismatches} mismatches  so far ...')
        print(f'Completed {processed} rows. Found {mismatches} mismatches.')

    def show_mismatch(self, sac):
        print(
                    sac.ein,
                    sac.auditee_uei,
                    sac.cognizant_agency,
                    sac.oversight_agency,
                    sac.federal_awards["FederalAwards"]["total_amount_expended"]
                )
        for award in sac.federal_awards["FederalAwards"]["federal_awards"]:
            print(
                        'Award:',
                        award["award_reference"],
                        award["program"]['amount_expended'],
                        award["program"]['federal_agency_prefix'],
                        award["program"]['three_digit_extension'],
                        award['direct_or_indirect_award']['is_direct'],
                    )

    def make_sac(self, gen:CensusGen22):
        sac = SingleAuditChecklist()
        sac.general_information = {}
        sac.general_information["ein"] = gen.ein
        sac.general_information["auditee_uei"] = gen.uei
        sac.cognizant_agency = gen.cogagency
        sac.oversight_agency = gen.oversightagency
        sac.federal_awards = self.make_awards(gen)
        return sac

    def make_awards(self, gen:CensusGen22):
        awards =  {
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
    



    

