# TODO - This file should be removed eventually after more testing is done. - Please check with Sudha K.
#############################################################
# cog_over_assignment
#   Input - federal_awards_data - federal awards json object
#   Returns - cog_agency_prefix, over_agency_prefix - Agency prefix integer
#
# Algorithm:
# Use all "federal_awards" to do calculations required to
#   determine cognizant / oversight agency assignment

# Calculate total amount_expended (tot_amount_expended)
# Calculate total amount_expended by agency
#   tot_amount_agency = {agency, tot_amt}
# Calculate total direct award amount_expended by agency
#   tot_da_amount_agency = {agency, tot_da_amt}
# Calculate total direct award amount_expended (tot_da_amount_expended)
#
# If tot_amount_expended > $ 50,000,000, find cog agency
#   Pull 2019 data from DB
#       If 2019 data exists, use this for all calculations
#           data_to_use = 2019 data
#           Do all the above calculations with data_to_use
#       else use current data
#           data_to_use = current data
#       if tot_da_amount_expended >= 25% tot_amount_expended
#           cog_agency_prefix = agency with max tot_da_amt in tot_da_amount_agency
#       else
#           cog_agency_prefix = agency with max tot_amt in tot_amount_agency
# else, find over agency
#       if tot_da_amount_expended >= 25% tot_amount_expended
#           over_agency_prefix = agency with max tot_da_amt in tot_da_amount_agency
#       else
#           over_agency_prefix = agency with max tot_amt in tot_amount_agency
#############################################################

from collections import defaultdict


def calc_amount_expended_limit():
    MILLION = 1_000_000
    amount_expended_limit = 50 * MILLION
    return amount_expended_limit


def load_2019_federal_award_data(auditee_ein):
    # Load 2019 ["FederalAwards"] where
    # 2019 Cfda.auditee_ein = auditee_ein
    # return Cfda19.objects.filter(ein=auditee_ein)
    pass


def auditee_2019_submission_exists(auditee_ein, general_2019_data):
    # Check if auditee_ein exists in 2019 data
    # return Gen19.objects.filter(ein=auditee_ein)
    return auditee_ein == general_2019_data["General"]["ein"]


def calc_total_amounts_agency(fed_award_data, year=2023):
    tot_amount_agency = defaultdict(lambda: 0)
    tot_da_amount_agency = defaultdict(lambda: 0)
    tot_da_amount_expended = 0
    for award in fed_award_data["FederalAwards"]["federal_awards"]:
        if year == 2019:
            agency_prefix = int(str(award["cfda"])[:2])
            tot_amount_agency[agency_prefix] += award["amount"]
            if award["direct"] == "Y":
                tot_da_amount_expended += award["amount"]
                tot_da_amount_agency[agency_prefix] += award["amount"]
        else:  # 2023
            agency_prefix = award["program"]["federal_agency_prefix"]
            tot_amount_agency[agency_prefix] += award["program"]["amount_expended"]
            if award["direct_or_indirect_award"]["is_direct"] == "Y":
                tot_da_amount_expended += award["program"]["amount_expended"]
                tot_da_amount_agency[agency_prefix] += award["program"][
                    "amount_expended"
                ]
    tot_amount_agency = list(
        sorted(tot_amount_agency.items(), reverse=True, key=lambda item: item[1])
    )
    tot_da_amount_agency = list(
        sorted(tot_da_amount_agency.items(), reverse=True, key=lambda item: item[1])
    )
    # print("tot_amount_agency = ", tot_amount_agency)
    # print("tot_da_amount_agency = ", tot_da_amount_agency)
    # print("tot_da_amount_expended = ", tot_da_amount_expended)

    return tot_da_amount_expended, tot_da_amount_agency[0], tot_amount_agency[0]


def select_agency(
    tot_da_amount_expended, tot_da_amount_agency, tot_amount_agency, tot_amount_expended
):
    if tot_da_amount_expended >= 0.25 * tot_amount_expended:
        selected_agency_prefix, val = tot_da_amount_agency
    else:
        selected_agency_prefix, val = tot_amount_agency
    # print("selected agency prefix = ", selected_agency_prefix)
    return selected_agency_prefix


def calc_tot_amt_expended(federal_awards_data, auditee_ein, general_2019_data):
    if auditee_2019_submission_exists(auditee_ein, general_2019_data):
        # Calculate from 2019 data
        # gen = Gen19.objects.filter(EIN=auditee_ein)
        return general_2019_data["General"]["totfedexpend"]
    else:
        return federal_awards_data["FederalAwards"]["total_amount_expended"]


def cog_over_assignment(
    federal_awards_data, auditee_ein, federal_awards_data_2019_data, general_2019_data
):
    cog_agency_prefix = 0
    over_agency_prefix = 0

    # #print(CensusCfda19.objects.filter(index__lt = 10))
    # #print("Cfda first row = ", Cfda.objects.first())
    # print("Cfda first row = ", Cfda19.objects.filter(index__lt=10))
    # #cfda = Cfda.objects.filter(EIN = 731084819)
    # print("Gen first row = ", Gen19.objects.filter(index__lt=10))

    if (
        calc_tot_amt_expended(federal_awards_data, auditee_ein, general_2019_data)
        > calc_amount_expended_limit()
    ):
        #       Cognizant agency
        if auditee_2019_submission_exists(auditee_ein, general_2019_data):
            # federal_awards_data_2019 = load_2019_federal_award_data(auditee_ein)
            (
                tot_da_amount_expended,
                tot_da_amount_agency,
                tot_amount_agency,
            ) = calc_total_amounts_agency(federal_awards_data_2019_data, 2019)
            cog_agency_prefix = select_agency(
                tot_da_amount_expended,
                tot_da_amount_agency,
                tot_amount_agency,
                general_2019_data["General"]["totfedexpend"],
            )
        else:
            print("No 2019 submission")
            (
                tot_da_amount_expended,
                tot_da_amount_agency,
                tot_amount_agency,
            ) = calc_total_amounts_agency(federal_awards_data)
            cog_agency_prefix = select_agency(
                tot_da_amount_expended,
                tot_da_amount_agency,
                tot_amount_agency,
                federal_awards_data["FederalAwards"]["total_amount_expended"],
            )
    else:
        #       Oversight agency
        (
            tot_da_amount_expended,
            tot_da_amount_agency,
            tot_amount_agency,
        ) = calc_total_amounts_agency(federal_awards_data)
        over_agency_prefix = select_agency(
            tot_da_amount_expended,
            tot_da_amount_agency,
            tot_amount_agency,
            federal_awards_data["FederalAwards"]["total_amount_expended"],
        )

    print("cog_agency_prefix = ", cog_agency_prefix)
    print("over_agency_prefix = ", over_agency_prefix)
    return cog_agency_prefix, over_agency_prefix
