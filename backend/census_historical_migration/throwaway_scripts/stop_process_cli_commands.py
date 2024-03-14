import argparse
import re
import subprocess  # nosec
import sys

# This script stops running tasks for a specified app space in Cloud Foundry.
# It identifies tasks by their ID. If no specific IDs are given, it will attempt to stop all currently running tasks.


def check_cf_environment():
    # Run 'cf target' and capture the output
    result = subprocess.run(["cf", "target"], capture_output=True, text=True)  # nosec

    # Check if the command was successful
    if result.returncode != 0:
        print("Error retrieving Cloud Foundry target information")
        sys.exit(1)

    return "preview" in result.stdout


def get_running_task_ids():
    # Run `cf tasks gsa-fac` and capture the output
    result = subprocess.run(
        ["cf", "tasks", "gsa-fac"], capture_output=True, text=True
    )  # nosec

    if result.returncode != 0:
        print("Error running command")
        return []

    # Process the output
    output = result.stdout
    lines = output.split("\n")
    running_tasks = [line for line in lines if "RUNNING" in line]

    # Extract IDs
    task_ids = []
    for task in running_tasks:
        match = re.match(r"(\d+)", task)
        if match:
            task_ids.append(match.group(1))

    return task_ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Terminate running tasks.")
    parser.add_argument(
        "--start_id", type=int, help="Id of first instance", required=False
    )
    parser.add_argument(
        "--end_id", type=int, help="Id of last instance", required=False
    )

    args = parser.parse_args()

    if not check_cf_environment():
        print("This script can only be run in the PREVIEW environment.")
        sys.exit(1)

    # If start_id and end_id are not provided
    if args.start_id is None or args.end_id is None:
        user_input = input("Terminate all running tasks? (Y/N): ")
        if user_input.lower() == "y":
            running_ids = get_running_task_ids()
            print("Terminating Running task IDs:", running_ids)
            for id in running_ids:
                print(f"# Stopping process {id}")
                cmd = ["cf", "terminate-task", "gsa-fac", id]
                subprocess.run(cmd)  # nosec
    else:
        for id in range(int(args.start_id), int(args.end_id) + 1):
            # cf terminate-task gsa-fac <task_id>
            print(f"# Stopping process {id}")
            cmd = [
                "cf",
                "terminate-task",
                "gsa-fac",
                f"{id}",
            ]

            print(" ".join(cmd))
            subprocess.run(cmd)  # nosec


# Examples

# python stop_process_cli_commands.py 20 50
# will stop all instances with IDs 20 through 50, inclusive.
# To see the running instances IDs, run `cf tasks gsa-fac`
