#############################################################
# cog_over_assignment
#   Input - federal_awards_data - federal awards json object
#   Returns - cog_agency, over_agency - Agency prefix integer
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
#           cog_agency = agency with max tot_da_amt in tot_da_amount_agency
#       else
#           cog_agency = agency with max tot_amt in tot_amount_agency
# else, find over agency
#       if tot_da_amount_expended >= 25% tot_amount_expended
#           over_agency = agency with max tot_da_amt in tot_da_amount_agency
#       else
#           over_agency = agency with max tot_amt in tot_amount_agency
#############################################################

from collections import defaultdict
# 2019 cfda table - Fix names when 2019 data is available
from 2019models import cfda2019

def calc_amount_expended_limit():
    MILLION = 1_000_000
    amount_expended_limit = 50 * MILLION
    return amount_expended_limit


def load_2019_federal_award_data():
    pass


def auditee_2019_submission_exists():
    return False # for now


def calc_total_amounts(tot_amt_agency, tot_da_amt_agency, tot_da_amt_expended, fed_award_data):
    for award in fed_award_data["FederalAwards"]["federal_awards"]:
        agency = award["program"]["federal_agency_prefix"]
        tot_amt_agency[agency] += award["program"]["amount_expended"]
        if award["direct_or_indirect_award"]["is_direct"] == "Y":
            tot_da_amt_expended += award["program"]["amount_expended"]
            tot_da_amt_agency[agency] += award["program"]["amount_expended"]

    tot_amt_agency = list(
        sorted(tot_amt_agency.items(), reverse=True, key=lambda item: item[1])
    )
    #   print("tot_amt_agency = ", tot_amt_agency)

    tot_da_amt_agency = list(
        sorted(tot_da_amt_agency.items(), reverse=True, key=lambda item: item[1])
    )
    #   print("tot_da_amt_agency = ", tot_da_amt_agency)

    #   print("tot_da_amt_expended = ", tot_da_amt_expended)
    return tot_amt_agency, tot_da_amt_agency, tot_da_amt_expended


def cog_over_assignment(federal_awards_data):
    cog_agency = 0
    over_agency = 0
    tot_amount_agency = defaultdict(lambda: 0)
    tot_da_amount_agency = defaultdict(lambda: 0)
    tot_da_amount_expended = 0

    tot_amount_agency, tot_da_amount_agency, tot_da_amount_expended = \
        calc_total_amounts(tot_amount_agency, tot_da_amount_agency, tot_da_amount_expended, federal_awards_data)

    # for award in federal_awards_data["FederalAwards"]["federal_awards"]:
    #     agency = award["program"]["federal_agency_prefix"]
    #     tot_amount_agency[agency] += award["program"]["amount_expended"]
    #     if award["direct_or_indirect_award"]["is_direct"] == "Y":
    #         tot_da_amount_expended += award["program"]["amount_expended"]
    #         tot_da_amount_agency[agency] += award["program"]["amount_expended"]

    # tot_amount_agency = list(
    #     sorted(tot_amount_agency.items(), reverse=True, key=lambda item: item[1])
    # )
    # #   print("tot_amount_agency = ", tot_amount_agency)

    # tot_da_amount_agency = list(
    #     sorted(tot_da_amount_agency.items(), reverse=True, key=lambda item: item[1])
    # )
    # #   print("tot_da_amount_agency = ", tot_da_amount_agency)

    # #   print("tot_da_amount_expended = ", tot_da_amount_expended)

    if (
        federal_awards_data["FederalAwards"]["total_amount_expended"]
        > calc_amount_expended_limit()
    ):
        #############################################################
        #       Cognizant agency
        #       ######## TO DO NEXT
        #       ####### Use 2019 Base year submission data
        #############################################################
        if auditee_2019_submission_exists():
            tot_amount_agency_2019 = defaultdict(lambda: 0)
            tot_da_amount_agency_2019 = defaultdict(lambda: 0)
            tot_da_amount_expended_2019 = 0

            tot_amount_agency_2019, tot_da_amount_agency_2019, tot_da_amount_expended_2019 = \
                calc_total_amounts(tot_amount_agency_2019, tot_da_amount_agency_2019, tot_da_amount_expended_2019, federal_awards_data_2019)
            
            if (
                tot_da_amount_expended_2019
                >= 0.25 * federal_awards_data_2019["FederalAwards"]["total_amount_expended"]
            ):
                cog_agency, val = tot_da_amount_agency_2019[0]
            else:
                cog_agency, val = tot_amount_agency_2019[0]
        #           print("cognizant agency = ", cog_agency)
        else:
            if (
                tot_da_amount_expended
                >= 0.25 * federal_awards_data["FederalAwards"]["total_amount_expended"]
            ):
                cog_agency, val = tot_da_amount_agency[0]
            else:
                cog_agency, val = tot_amount_agency[0]
        #           print("cognizant agency = ", cog_agency)
    else:
        #       Oversight agency
        if (
            tot_da_amount_expended
            >= 0.25 * federal_awards_data["FederalAwards"]["total_amount_expended"]
        ):
            over_agency, val = tot_da_amount_agency[0]
        else:
            over_agency, val = tot_amount_agency[0]
        #       print("oversight agency = ", over_agency)

    return cog_agency, over_agency
