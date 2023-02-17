"""Functions that the public data loader uses to handle errors"""
import logging
import json
import os

from datetime import datetime

logger = logging.getLogger(__name__)


def set_up_error_files():
    progress_files = (
        "data_distro/data_to_load/run_logs/Lines_in_progress.json",
        "data_distro/data_to_load/run_logs/Errors_in_progress.json",
        "data_distro/data_to_load/run_logs/Exceptions_in_progress.json",
    )
    for file_name in progress_files:
        file = open(file_name, "w")
        file.close()


def finish_error_files(date_stamp):
    """Rename with date stamp or delete if empty"""
    progress_files = (
        "data_distro/data_to_load/run_logs/Lines_in_progress.json",
        "data_distro/data_to_load/run_logs/Errors_in_progress.json",
        "data_distro/data_to_load/run_logs/Exceptions_in_progress.json",
    )
    new_names = (
        f"data_distro/data_to_load/run_logs/Lines_{date_stamp}.json",
        f"data_distro/data_to_load/run_logs/Errors_{date_stamp}.json",
        f"data_distro/data_to_load/run_logs/Exceptions_{date_stamp}.json",
    )

    error_files = []
    for (progress, new) in zip(progress_files, new_names):
        if os.path.getsize(progress) == 0:
            os.remove(progress)
        else:
            os.rename(progress, new)
            error_files.append(new)

    return error_files


def add_to_file(file_name, paylod):
    """Keeping track of errors in a file as the script runs"""
    data = []
    with open(file_name, "r+") as outfile:
        if os.path.getsize(file_name) != 0:
            data = json.loads(outfile.read())
            if data is None:
                data = []
        data.append(paylod)
        outfile.seek(0)
        json.dump(data, outfile, indent=2)
        outfile.truncate()


def handle_badlines(bad_line: list[str]) -> list[str] | None:
    """With parsing improvements, these are rare, but want to make sure all data is accounted for"""
    file_path = "data_distro/data_to_load/run_logs/Lines_in_progress.json"
    with open(file_path, "r+") as outfile:
        data = []
        if os.path.getsize(file_path) != 0:
            data = json.loads(outfile.read())

        data.append(bad_line)
        json.dump(data, outfile)

    logger.warn(
        f"""
        ---------------------BAD LINE---------------------
        {bad_line}
        -------------------------------------------------
        """
    )

    return None


def handle_exceptions(table, file_path, instance_dict, error_trace, exceptions_list):
    """Add detailed explanations to the logs and keep track of each type of error"""
    error_file = "data_distro/data_to_load/run_logs/Errors_in_progress.json"
    add_to_file(error_file, {table: instance_dict})

    exception_file = "data_distro/data_to_load/run_logs/Exceptions_in_progress.json"
    add_to_file(exception_file, error_trace)

    logger.warn(
        f"""
        ---------------------PROBLEM---------------------
        {table}, {file_path}
        ----
        {instance_dict}
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        {error_trace}
        -------------------------------------------------
        """
    )
    problem_text = f"Error loading {file_path}: \n \
        {error_trace}"

    if problem_text not in exceptions_list:
        exceptions_list.append(problem_text)

    return exceptions_list


def log_results(exceptions_list, expected_objects_dict):
    """This is helpful for debugging"""
    date_stamp = str(datetime.now())[:-7]
    errors = finish_error_files(date_stamp)
    exceptions_count = len(exceptions_list)

    payload = {
        "expected_objects_dict": expected_objects_dict,
        "exceptions_list": exceptions_list,
    }

    with open(
        f"data_distro/data_to_load/run_logs/Results_{date_stamp}.json", "w"
    ) as outfile:
        json.dump(payload, outfile)

    if len(errors) > 0:
        logger.warning(
            f"""
            ###############################
            Expected Objects: {expected_objects_dict}
            ###############################
            Error count: {exceptions_count}
            ###############################
            ❌ Check run_logs for error details"""
        )

    else:
        logger.warning(
            f"""
            ###############################
            Expected Objects: {expected_objects_dict}
            ###############################
            Successful upload 🏆"""
        )

    return date_stamp
