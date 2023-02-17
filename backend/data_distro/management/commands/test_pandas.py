from pandas import read_csv
import csv
import logging

from django.core.management.base import BaseCommand

from data_distro.management.commands.handle_errors import (
    handle_badlines,
    set_up_error_files,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Find parsing errors. Run the pandas to find bad data and manually edit files. This won't catch smaller errors.
    """

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", type=str, help="file name")
        parser.add_argument(
            "-y",
            "--year",
            type=str,
            help="Two digit year of downloads, as they appear in the file names. Leave blank for all years. Not needed if using file name kwarg.",
        )

    def handle(self, *args, **kwargs):
        if kwargs["file"] is not None:
            load_file_names = [kwargs["file"]]

        else:
            year = kwargs["year"]
            if year is None:
                year = ""

            # Dependent objects are created first
            load_file_names = [
                f"findingstext_formatted{year}.txt",
                f"findings{year}.txt",
                f"captext_formatted{year}.txt",
                f"cfda{year}.txt",
                f"notes{year}.txt",
                f"revisions{year}.txt",
                f"passthrough{year}.txt",
                f"gen{year}.txt",
                f"cpas{year}.txt",
            ]

        test_panda_parsing(load_file_names)


def test_panda_parsing(load_file_names):
    set_up_error_files()
    for file in load_file_names:
        file_path = f"data_distro/data_to_load/{file}"
        file_name = file_path.replace("data_distro/data_to_load/", "")
        # Remove numbers, there are years in the file names, remove file extension
        table = "".join([i for i in file_name if not i.isdigit()])[:-4]
        # Remove for testing
        table = table.replace("test_data/", "")
        logger.warning(f"Starting to load {file_name}...")
        expected_object_count = 0

        for i, chunk in enumerate(
            read_csv(
                file_path,
                chunksize=30000,
                sep="|",
                encoding="mac-roman",
                on_bad_lines=handle_badlines,
                engine="python",
                quoting=csv.QUOTE_NONE,
            )
        ):
            csv_dict = chunk.to_dict(orient="records")
            expected_object_count += len(csv_dict)

            logger.warning(f"finished {table} chunk")

        logger.warning(f"--{expected_object_count} expected {table} objects--")
