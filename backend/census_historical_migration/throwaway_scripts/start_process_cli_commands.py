import argparse
import subprocess  # nosec
import time

from util import trigger_migration_workflow

# This throwaway script spits out code that can be
# copy-pasted into a bash script, or directly into the command line.
# Run from within the Github repo, it should launch <instances> instances
# of the historic data migration code.

parser = argparse.ArgumentParser(
    description="Trigger data migration Github Actions through gh API calls."
)
parser.add_argument("year", type=int, help="Year to run (2022, 2021, etc.)")
parser.add_argument("total_records", type=int, help="Total records.")
parser.add_argument("pages_per_instance", type=int, help="Pages per instance.")
parser.add_argument("instances", type=int, help="How many parallel istances to run")

args = parser.parse_args()


if __name__ == "__main__":
    cmds = trigger_migration_workflow(args)
    for ndx, cmd in enumerate(cmds):
        print(f"# Instance {ndx + 1}")
        cmd = " ".join(cmd)
        print(cmd)
        subprocess.run(cmd)  # nosec
        time.sleep(15)


# Examples

# With round numbers, it comes out nice and tidy.
# python start_process_cli_commands.py 2022 42000 5 80
# Each instance must run 525 records.
# With 5 pages per instance, the page size is 105.
# There are 400 pages in total.
# This means we will attempt 42000 records.

# Off-by-one, and we make sure we don't drop that extra.
# python start_process_cli_commands.py 2022 42001 5 80
# Each instance must run 526 records.
# With 5 pages per instance, the page size is 106.
# There are 397 pages in total.
# This means we will attempt 42082 records.

# More pages, and we get closer to the exact number.
# python start_process_cli_commands.py 2022 42001 10 80
# Each instance must run 526 records.
# With 10 pages per instance, the page size is 53.
# There are 793 pages in total.
# This means we will attempt 42029 records.
