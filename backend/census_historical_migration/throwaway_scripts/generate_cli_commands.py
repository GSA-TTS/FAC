import argparse
import math
import subprocess  # nosec

# This throwaway script spits out code that can be
# copy-pasted into a bash script, or directly into the command line.
# Run from within the Github repo, it should launch <instances> instances
# of the historic data migration code.

parser = argparse.ArgumentParser(description="Print some commands for copy-pasting.")
parser.add_argument("year", type=int, help="Year to run (2022, 2021, etc.)")
parser.add_argument("total_records", type=int, help="Total records.")
parser.add_argument("pages_per_instance", type=int, help="Pages per instance.")
parser.add_argument("instances", type=int, help="How many parallel istances to run")
args = parser.parse_args()


# Ceiling division
# We need to always round *up* so we don't miss any records.
def cdiv(a, b):
    return math.ceil(a / b)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield list(map(str, lst[i : i + n]))


if __name__ == "__main__":
    # The number of pages is the total records // instances
    recs_per_instance = cdiv(args.total_records, args.instances)
    print(f"Each instance must run {recs_per_instance} records.")
    page_size = cdiv(recs_per_instance, args.pages_per_instance)
    print(
        f"With {args.pages_per_instance} pages per instance, the page size is {page_size}."
    )
    total_pages = cdiv(args.total_records, page_size)
    print(f"There are {total_pages} pages in total.")
    print(f"This means we will attempt {total_pages * page_size} records.")
    # Run one extra page for good measure. This "rounds up."
    page_chunks = chunks(range(1, total_pages + 1), args.pages_per_instance)
    for ndx, page_set in enumerate(page_chunks):
        # gh workflow run historic-data-migrator-with-pagination.yml -f environment=preview -f year=2022 -f page_size=1 -f pages=1
        print(f"# Instance {ndx + 1}")
        cmd = " ".join(
            [
                "gh",
                "workflow",
                "run",
                "historic-data-migrator-with-pagination.yml",
                "-f",
                "environment=preview",
                "-f",
                f"year={args.year}",
                "-f",
                f"page_size={page_size}",
                "-f",
                "pages={}".format(",".join(page_set)),
            ]
        )
        print(cmd)
        subprocess.run(cmd)  # nosec


# Examples

# With round numbers, it comes out nice and tidy.
# python generate_cli_commands.py 2022 42000 5 80
# Each instance must run 525 records.
# With 5 pages per instance, the page size is 105.
# There are 400 pages in total.
# This means we will attempt 42000 records.

# Off-by-one, and we make sure we don't drop that extra.
# python generate_cli_commands.py 2022 42001 5 80
# Each instance must run 526 records.
# With 5 pages per instance, the page size is 106.
# There are 397 pages in total.
# This means we will attempt 42082 records.

# More pages, and we get closer to the exact number.
# python generate_cli_commands.py 2022 42001 10 80
# Each instance must run 526 records.
# With 10 pages per instance, the page size is 53.
# There are 793 pages in total.
# This means we will attempt 42029 records.
