import pandas as pd


def merge_alns():
    output_file = "./source/data/cfda-lookup.csv"
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
        aln_rows = pd.read_csv(f"{folder}/{csv_file}", encoding="ISO-8859-1", dtype={"Assistance Listings Number": str})
        aln_rows = aln_rows.rename(columns=column_mapping)
        all_aln_rows.append(aln_rows)

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
