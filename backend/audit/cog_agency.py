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


def cog_over_assignment(federal_awards_data):
    cog_agency = 0
    over_agency = 0
    tot_amount_expended = 0
    tot_amount_agency = {}
    tot_da_amount_agency = {}
    tot_da_amount_expended = 0
    for i in federal_awards_data['FederalAwards']['federal_awards']:
        tot_amount_expended += i['program']['amount_expended']
        agency = i['program']['federal_agency_prefix']
        if agency in tot_amount_agency.keys():
            tot_amount_agency[agency] += i['program']['amount_expended']
        else:
            tot_amount_agency[agency] = i['program']['amount_expended']
        if i['direct_or_indirect_award']['is_direct'] == 'Y':
            tot_da_amount_expended += i['program']['amount_expended']
            if agency in tot_da_amount_agency.keys():
                tot_da_amount_agency[agency] += i['program']['amount_expended']
            else:
                tot_da_amount_agency[agency] = i['program']['amount_expended']
#   print("tot_amount_expended = ", tot_amount_expended)

    tot_amount_agency = list(sorted(tot_amount_agency.items(), reverse=True, key=lambda item: item[1]))
#   print("tot_amount_agency = ", tot_amount_agency)

    tot_da_amount_agency = list(sorted(tot_da_amount_agency.items(), reverse=True, key=lambda item: item[1]))
#   print("tot_da_amount_agency = ", tot_da_amount_agency)

#   print("tot_da_amount_expended = ", tot_da_amount_expended)

    if tot_amount_expended > 50000000:
        #############################################################
        #       Cognizant agency
        #       ######## TO DO NEXT
        #       ####### Use 2019 Base year submission data
        #############################################################
        data_2019 = False  # For now
        if data_2019:
            pass
        else:
            if tot_da_amount_expended >= 0.25 * tot_amount_expended:
                cog_agency, val = tot_da_amount_agency[0]
            else:
                cog_agency, val = tot_amount_agency[0]
        #           print("cognizant agency = ", cog_agency)
    else:
        #       Oversight agency
        if tot_da_amount_expended >= 0.25 * tot_amount_expended:
            over_agency, val = tot_da_amount_agency[0]
        else:
            over_agency, val = tot_amount_agency[0]
        #       print("oversight agency = ", over_agency)

    return cog_agency, over_agency
