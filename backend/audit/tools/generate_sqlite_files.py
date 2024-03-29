from collections import defaultdict
from pathlib import Path
import argparse
import os
import pandas as pd
import re
import sqlite3
import zipfile

import csv

# Usage:
# python main.py --zip all.zip --sqlite file.sqlite3
parser = argparse.ArgumentParser()
dtypes: defaultdict = defaultdict(lambda: str)


def main(args):
    # Name the sqlite the same as the zipfile.
    sqlitefilename = f"{Path(args.zip).stem}.sqlite3"
    print(f"Writing to {sqlitefilename}")
    if os.path.isfile(sqlitefilename):
        os.remove(sqlitefilename)

    tdir = args.outdir
    os.makedirs(tdir, exist_ok=True)
    os.makedirs(f"clean-{tdir}", exist_ok=True)

    with zipfile.ZipFile(args.zip, "r") as zip_ref:
        zip_ref.extractall(tdir)
    # for filename in glob.glob(os.path.join(tdir, "[!clean]*.txt")):
    for filename in os.listdir(tdir):
        filepath = os.path.join(tdir, filename)
        print(f"Extracted {filepath}")
        # print(f'{filename} - {translate[encoding["encoding"]]}')
        # clean_filename = os.path.join(f"clean-{tdir}", f"{Path(filename).stem}.txt")
        clean_filename = os.path.join(f"clean-{tdir}", filename)
        print(f"{filepath} -> {clean_filename}")

        content = open(filepath, "rb").read().decode("cp1252")
        ascii_encoded = content.encode("ascii", "ignore")
        f = open(clean_filename, "wb")
        f.write(ascii_encoded)
        f.close()

        # print(f'Skipped {counter} lines in {filename} for encoding reasons.')
        # shutil.move(clean_filename, filename)
        df = pd.read_csv(
            open(clean_filename, "rb"),
            delimiter="|",
            dtype=dtypes,
            low_memory=False,
            on_bad_lines="skip",
            quoting=csv.QUOTE_NONE,
            lineterminator="\n",
        )
        with sqlite3.connect(sqlitefilename) as conn:
            # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python
            tablename = Path(filename).stem
            # Remove the year
            tablename = re.sub(r"[0-9]+", "", tablename)
            df.to_sql(name=tablename, con=conn)

        print(f"loaded {clean_filename} to {tablename}")


if __name__ == "__main__":
    parser.add_argument("--zip", type=str, required=True)
    parser.add_argument("--outdir", type=str, required=True)

    args = parser.parse_args()
    main(args)
