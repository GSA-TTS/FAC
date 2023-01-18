import csv

from models.py import *


def read_file(file_name):
    """Simple data loader"""
    data_to_load = []
    with open(file_name, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        header_row = reader.pop(0)
        for row in reader:
            postion = 0
            for data in row:
                data_to_load.append({header_row[postion]: data})
                postion += 1
