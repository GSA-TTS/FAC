from collections import defaultdict
from pathlib import Path
import argparse
import glob
import os
import pandas as pd
import re
import sqlite3
import zipfile
import shutil

import csv

# Usage:
# python main.py --zip all.zip --sqlite file.sqlite3
parser = argparse.ArgumentParser()
dtypes = defaultdict(lambda: str)

def main(args):
    # Name the sqlite the same as the zipfile.
    sqlitefilename = f'{Path(args.zip).stem}.sqlite3'
    print(f'Writing to {sqlitefilename}')
    if os.path.isfile(sqlitefilename):
        os.remove(sqlitefilename)

    tdir = args.outdir
    os.makedirs(tdir, exist_ok=True)
    os.makedirs(f'clean-{tdir}', exist_ok=True)

    with zipfile.ZipFile(args.zip, 'r') as zip_ref:
        zip_ref.extractall(tdir)
    for filename in glob.glob(os.path.join(tdir, '*.txt')):
        # print(f'{filename} - {translate[encoding["encoding"]]}')
        clean_filename = os.path.join(f'clean-{tdir}', f'{Path(filename).stem}.txt')
        print(f'{filename} -> {clean_filename}')

        content = open(filename, 'rb').read().decode('cp1252')
        ascii = content.encode('ascii', 'ignore')
        f = open(clean_filename, 'wb')
        f.write(ascii)
        f.close()

        #print(f'Skipped {counter} lines in {filename} for encoding reasons.')
        #shutil.move(clean_filename, filename)
        df = pd.read_csv(open(clean_filename, 'rb'),
                        delimiter="|", 
                        dtype=dtypes,
                        low_memory=False,
                        on_bad_lines='skip',
                        quoting=csv.QUOTE_NONE,
                        lineterminator='\n'
                        )
        with sqlite3.connect(sqlitefilename) as conn:
            # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python
            tablename = Path(filename).stem
            # Remove the year
            tablename = re.sub(r"[0-9]+", "", tablename)
            df.to_sql(name=tablename, con=conn)

if __name__ == "__main__":
    parser.add_argument('--zip', type=str, required=True)
    parser.add_argument('--outdir', type=str, required=True)

    args = parser.parse_args()
    main(args)
