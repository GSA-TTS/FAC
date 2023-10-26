from workbook_generator import generate_workbooks

import os
import sys

import argparse

parser = argparse.ArgumentParser()

def main():
    out_basedir = None
    if args.output:
        out_basedir = args.output
    else:
        out_basedir = 'output'

    if not os.path.exists(out_basedir):
        try:
            os.mkdir(out_basedir)
        except Exception as e:
            pass
    outdir = os.path.join(out_basedir, args.dbkey)
    if not os.path.exists(outdir):
        try:
            os.mkdir(outdir)
        except Exception as e:
            print('could not create output directory. exiting.')
            sys.exit()

    generate_workbooks(args.dbkey, outdir)

if __name__ == '__main__':
    parser.add_argument('--dbkey', type=str, required=True)
    parser.add_argument('--output', type=str, required=False)
    args = parser.parse_args()
    main()
