import os
import json
from cog_agency import cog_over_assignment

# Test 1
print("\n\n Test 1:")
file = "../data_fixtures/audit/test_data_entries/test_cog_over.json"
print("File used: ", file)
with open(file, "r") as f:
    test_data = json.load(f)
#print(test_data['FederalAwards']['federal_awards'])

cog_agency, over_agency = cog_over_assignment(test_data)
print("cognizant agency = ", cog_agency)
print("oversignt agency = ", over_agency)

# Test 2
print("\n\n Test 2:")
file = "../data_fixtures/audit/test_data_entries/test_cog_over_more_awards.json"
print("File used: ", file)
with open(file, "r") as f:
    test_data = json.load(f)
#print(test_data['FederalAwards']['federal_awards'])

cog_agency, over_agency = cog_over_assignment(test_data)
print("cognizant agency = ", cog_agency)
print("oversignt agency = ", over_agency)