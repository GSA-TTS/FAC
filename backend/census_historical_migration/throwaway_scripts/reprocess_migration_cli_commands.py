import argparse

from util import (
    trigger_migration_workflow,
)
import subprocess  # nosec

# This script is a one-off to reprocess mdata migration for a failed
# migration attempt associated with a specific error tag.

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
    for cmd in cmds:
        cmd.append(f"error_tag={args.error_tag}")
        print(" ".join(cmd))
        subprocess.run(cmd)  # nosec
