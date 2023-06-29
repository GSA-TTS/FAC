import re, sys

EMPTY_STRING = ""
repls = [
    (' COLLATE "USING_NLS_COMP"', EMPTY_STRING),
    ("VARCHAR2\(.*?\)", "TEXT"),
    (' DEFAULT COLLATION "USING_NLS_COMP"', EMPTY_STRING),
    ("NUMBER\([0-9]+\,[ \t]+0\)", "NUMERIC"),
    ("CHAR\(.*?\)", "TEXT"),
    ("EDITIONABLE", EMPTY_STRING),
    ("END TEXT", "END"),
    ("END content", "END"),
    ("NUMBER", "NUMERIC"),
    ("FACDISSEM_OWNER\.", EMPTY_STRING),
    ("([a-z]+) ([a-z]{1})", "\\1 AS \\2"),
    ("CREATE TABLE (.*?) \(", "DROP TABLE IF EXISTS \\1;\nCREATE TABLE \\1 ("),
    ("CREATE TABLE", "CREATE TABLE"),
]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"repair-sql.py INFILE OUTFILE")
        exit()
    tables_file_to_be_cleaned = sys.argv[1]
    outp = open(sys.argv[2], "w")

    newlines = []
    for line in open(tables_file_to_be_cleaned, "r"):
        for pat_repl in repls:
            line = re.sub(pat_repl[0], pat_repl[1], line)
        newlines.append(line)

    for line in newlines:
        outp.write(line.strip() + "\n")

    outp.close()
