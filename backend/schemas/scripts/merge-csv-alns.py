import os
import pandas as pd
import glob
from datetime import datetime

def merge_alns():
    folder = './backend/schemas/source/data/ALNs_raw_downloads'
    date_suffix = datetime.now().strftime('%Y%m%d')
    output_file = f'./backend/schemas/source/data/cfda-lookup-{date_suffix}.csv'

    print(f'Looking for CSV files in: {folder}')
    csv_files = glob.glob(f'{folder}/*.csv')
    print(f'CSV files found: {csv_files}')

    if not csv_files:
        print('No data found in the input files.')
        return False

    all_data = []
    for f in csv_files:
        try:
            df = pd.read_csv(f, encoding='utf-8')
        except UnicodeDecodeError:
            print(f'Warning: Could not read {f} with UTF-8. Trying ISO-8859-1.')
            df = pd.read_csv(f, encoding='ISO-8859-1')
        all_data.append(df)

    combined_data = pd.concat(all_data, ignore_index=True)
    all_columns = combined_data.columns.unique()
    standardized_data = combined_data.reindex(columns=all_columns, fill_value=None)

    column_mapping = {
        'Title': 'Program Title',
        'Assistance Listings Number': 'Program Number',
        'Date Published': 'Date Published',
        'Department/Ind. Agency': 'Department/Ind. Agency',
        'Funded': 'Funded',
        'Last Date Modified': 'Last Date Modified',
        'POC Information': 'POC Information',
        'Related Federal Assistance': 'Related Federal Assistance',
        'Sub-Tier': 'Sub-Tier',
        'Types of Assistance': 'Types of Assistance'
    }

    standardized_data = standardized_data.rename(columns=column_mapping)
    print(f'Saving merged and standardized CSV to: {output_file}')
    standardized_data.to_csv(output_file, index=False, encoding='utf-8')
    print('CSV processing completed successfully.')
    return output_file

if __name__ == "__main__":
    merge_alns()
