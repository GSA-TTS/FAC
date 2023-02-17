"""
Download data from https://facdissem.census.gov/PublicDataDownloads.aspx
Then unzip the files and place the them in data_distro/data_to_load/

Load them with: manage.py public_data_loader
"""
from django.core.management.base import BaseCommand

from data_distro.management.commands.load_files import load_files
from data_distro.management.commands.handle_errors import (
    set_up_error_files,
    log_results,
)
from data_distro.management.commands.link_data import (
    add_duns_eins,
    add_agency,
)


class Command(BaseCommand):
    help = """
        Loads data from public download files into Django models. Add the data to "/backend/data_distro/data_to_load". \
        If you just want one file, you can pass the name of the file with -f.

        Requires pandas.

        See docs/data_loaing.md for more details.
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
        """
        1) Find the files for upload
        2) Grab just the files we want
        3) Load data into Django models
        4) Add DUNS relationships
        """
        set_up_error_files()

        if kwargs["file"] is not None:
            load_file_names = [kwargs["file"]]
            if "duns" in load_file_names or "ein" in load_file_names:
                add_duns_eins(load_file_names)
            elif "agency" in load_file_names:
                add_agency(load_file_names)
            else:
                exceptions_list, expected_objects_dict = load_files(load_file_names)

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

            exceptions_list, expected_objects_dict = load_files(load_file_names)
            # doing manually for this pass
            add_duns_eins(f"duns{year}.txt")
            add_duns_eins(f"eins{year}.txt")
            add_agency(f"agency{year}.txt")

        timestamp = log_results(exceptions_list, expected_objects_dict)
        return str(timestamp)
