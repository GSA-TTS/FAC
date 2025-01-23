import pandas as pd
from datetime import datetime


def merge_alns():
    date_suffix = datetime.now().strftime("%Y%m%d")
    output_file = f"./source/data/cfda-lookup-{date_suffix}.csv"

    folder = "./source/data/aln_csvs_to_be_merged"
    print(f"Looking for CSV files in: {folder}")

    csv_files = ["active-alns.csv", "inactive-alns.csv"]
    all_aln_rows = []

    for csv_file in csv_files:
        aln_rows = pd.read_csv(f"{folder}/{csv_file}", encoding="ISO-8859-1")
        all_aln_rows.append(aln_rows)

    combined_data = pd.concat(all_aln_rows, ignore_index=True)
    all_columns = combined_data.columns.unique()
    standardized_data = combined_data.reindex(columns=all_columns, fill_value=None)

    column_mapping = {
        "Title": "Program Title",
        "Assistance Listings Number": "Program Number",
        "Date Published": "Date Published",
        "Department/Ind. Agency": "Department/Ind. Agency",
        "Funded": "Funded",
        "Last Date Modified": "Last Date Modified",
        "POC Information": "POC Information",
        "Related Federal Assistance": "Related Federal Assistance",
        "Sub-Tier": "Sub-Tier",
        "Types of Assistance": "Types of Assistance",
    }

    standardized_data = standardized_data.rename(columns=column_mapping)
    print(f"Saving merged and standardized CSV to: {output_file}")
    standardized_data.to_csv(output_file, index=False, encoding="utf-8")
    print("CSV processing completed successfully.")
    return output_file


if __name__ == "__main__":
    merge_alns()
