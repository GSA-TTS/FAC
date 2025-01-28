import pandas as pd
from datetime import datetime


def has_valid_aln(row):
    """
    Check if the Assistance Listings Number (ALN) is valid.
    Valid formats include ##.###, ##.##, and ##.#.
    """
    aln = str(row["Program Number"])

    if "." in aln:
        prefix, extension = aln.split(".", 1)
        if prefix.isdigit() and extension:
            return True

    print(f"Warning: Invalid Program Number '{aln}'. Skipping.")
    return False


def merge_alns():
    date_suffix = datetime.now().strftime("%Y%m%d")
    output_file = f"./source/data/cfda-lookup-{date_suffix}.csv"

    folder = "./source/data/aln_csvs_to_be_merged"
    print(f"Looking for CSV files in: {folder}")

    csv_files = ["active-alns.csv", "inactive-alns.csv"]
    all_aln_rows = []
    column_mapping = {
        "Title": "Program Title",
        "Assistance Listings Number": "Program Number",
    }

    for csv_file in csv_files:
        print(f"Processing file: {csv_file}")
        aln_rows = pd.read_csv(f"{folder}/{csv_file}", encoding="ISO-8859-1")
        aln_rows = aln_rows.rename(columns=column_mapping)
        aln_rows_filtered = aln_rows[aln_rows.apply(has_valid_aln, axis=1)]
        all_aln_rows.append(aln_rows_filtered)

    # Combine all data into a single DataFrame
    combined_data = pd.concat(all_aln_rows, ignore_index=True)

    # Keep only necessary columns
    final_columns = ["Program Title", "Program Number"]
    if not all(col in combined_data.columns for col in final_columns):
        raise ValueError(
            f"Expected columns {final_columns} not found in {combined_data.columns}."
        )
    reduced_data = combined_data[final_columns]

    # Save the final merged and sorted file
    print(f"Saving merged and standardized CSV to: {output_file}")
    reduced_data.to_csv(output_file, index=False, encoding="utf-8")
    print("CSV processing completed successfully.")
    return output_file


if __name__ == "__main__":
    merge_alns()
