import argparse
from collections import defaultdict
import glob
import os
from pathlib import Path
import pandas as pd
import re
import sqlite3
import tempfile
import zipfile

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

    # Do everything in a temp dir.
    # It will disappear when we hit the end of the with block.
    with tempfile.TemporaryDirectory('_fac') as tdir:
        # https://stackoverflow.com/questions/3451111/unzipping-files-in-python
        with zipfile.ZipFile(args.zip, 'r') as zip_ref:
            zip_ref.extractall(tdir)
        for filename in glob.glob(os.path.join(tdir, '*.txt')):
            print(f'{filename}')
            # Census exports data in CP-1252.
            df = pd.read_csv(filename, delimiter="|", encoding='cp1252', dtype=dtypes)
            with sqlite3.connect(sqlitefilename) as conn:
                # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python
                tablename = Path(filename).stem
                # Remove the year
                tablename = re.sub(r"[0-9]+", "", tablename)
                df.to_sql(name=tablename, con=conn)

if __name__ == "__main__":
    parser.add_argument('--zip', type=str, required=True)
    args = parser.parse_args()
    main(args)
