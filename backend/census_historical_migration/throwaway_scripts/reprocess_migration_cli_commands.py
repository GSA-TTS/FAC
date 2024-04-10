import argparse
import time

from util import (
    trigger_migration_workflow,
)
import subprocess  # nosec

# This script is a one-off to reprocess mdata migration for a failed
# migration attempt associated with a specific error tag.
# Command is `python reprocess_migration_cli_commands.py year total_records pages_per_instance instances error_tag`
# `python reprocess_migration_cli_commands.py 2022 42000 5 80 invalid_email_error`

parser = argparse.ArgumentParser(
    description="Trigger data migration Github Actions through gh API calls"
)
parser.add_argument("year", type=int, help="Audit year")
parser.add_argument("total_records", type=int, help="Total records.")
parser.add_argument("pages_per_instance", type=int, help="Pages per instance.")
parser.add_argument("instances", type=int, help="How many parallel istances to run")
parser.add_argument("error_tag", type=str, help="Error tag to reprocess")
args = parser.parse_args()


if __name__ == "__main__":
    cmds = trigger_migration_workflow(
        args, workflow_name="failed-data-migration-reprocessor.yml"
    )
    print(args)
    for ndx, cmd in enumerate(cmds):
        print(f"# Instance {ndx + 1}")
        cmd.append("-f")
        cmd.append(f"error_tag={args.error_tag}")
        print(" ".join(cmd))
        subprocess.run(cmd)  # nosec
        time.sleep(15)
