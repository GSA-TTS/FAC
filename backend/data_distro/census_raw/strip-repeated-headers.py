import sys
import os
import csv
import re


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"GIVEN: {sys.argv}")
        print("Need an infile and destination directory.")
        exit()

    cleaned_dir = sys.argv[2]
    try:
        os.mkdir(cleaned_dir)
    except:
        pass

    infile = sys.argv[1]
    outfile = os.path.basename(sys.argv[1])
    # inp = open(infile, mode="r")
    # outp = open(os.path.join(cleaned_dir, outfile), mode="w")
    
    bonus_headers = 0 

    # FIXME: May have unicode issues...
    with open(infile, newline='', encoding='utf-8') as inp:
        with open(os.path.join(cleaned_dir, outfile), mode="w") as outp:
            writer = csv.writer(outp)
            # Skip the headers...
            headers = next(inp, None)  
            # But, put them in the output file!
            outp.write(headers)

            headers = headers.split(",")
            reader = csv.reader(inp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            columncount_shown = 0
            for row in reader:
                if len(row) != columncount_shown:
                    print(f"\tColumns: {len(row)}")
                    columncount_shown = len(row)
                if headers[0] in row:
                    bonus_headers += 1
                else:
                    newrow = list()
                    for cell in row:
                        if '\n' in cell:
                            origtext = cell.split('\n')
                            origtext = list(map(lambda s: s.replace('\r', ''), origtext))
                            origtext = list(map(lambda s: s.replace('\t', ' '), origtext))
                            # print(f"ORIGTEXT {origtext}")
                            text = ' '.join(origtext)
                            text = re.sub(' +', ' ', text)
                        else:
                            text = cell
                        newrow.append(text)
                    writer.writerow(newrow)

    print(f"\tFound {bonus_headers} bonus headers.")