import csv
import glob
import os


# Pull in agency names from the most recent cfda-agencies-YYYYMMDD.csv
# Scraps rows with non-int agency nums and rows with empty agency names.
def get_agency_names():
    agency_names = []
    list_of_files = glob.glob("./schemas/source/data/cfda-agencies*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, "r") as file:
        csvreader = csv.reader(file)
        csvreader = sorted(csvreader, key=lambda x: x[0])
        for row in csvreader:
            if row[0].isnumeric() and row[1] != "":
                agency_names.append(f"{row[0]} - {row[1]}")
    return agency_names
