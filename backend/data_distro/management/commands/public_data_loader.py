"""
Download data from https://facdissem.census.gov/PublicDataDownloads.aspx
Then unzip the files and place the them in data_distro/data_to_load/

Load them with: manage.py public_data_loader
"""
from django.core.management.base import BaseCommand

from data_distro.management.commands.load_files import (
    load_files,
    load_lists,
    load_agency,
)
from data_distro.management.commands.handle_errors import (
    set_up_error_files,
    log_results,
)


def lookup_files(year):
    """Different years have different files. Dependent objects are created first."""
    all_files = [
        f"cfda{year}.txt",
        f"findingstext_formatted{year}.txt",
        f"findings{year}.txt",
        f"captext_formatted{year}.txt",
        f"notes{year}.txt",
        f"revisions{year}.txt",
        f"passthrough{year}.txt",
        f"gen{year}.txt",
        f"cpas{year}.txt",
    ]
    files_18 = [
        f"cfda{year}.txt",
        f"findings{year}.txt",
        f"passthrough{year}.txt",
        f"gen{year}.txt",
        f"cpas{year}.txt",
    ]
    files_13 = [
        f"cfda{year}.txt",
        f"findings{year}.txt",
        f"gen{year}.txt",
        f"cpas{year}.txt",
    ]
    # I am going to see if I can save time by doing 97-09 as one task
    files_09 = [
        f"cfda{year}.txt",
        f"gen{year}.txt",
        f"cpas{year}.txt",
    ]

    if year is None:
        year = ""
        load_file_names = all_files
    elif int(year) >= 19:
        load_file_names = all_files
    elif int(year) >= 18:
        load_file_names = files_18
    elif int(year) >= 13:
        load_file_names = files_13
    elif int(year) >= 9:
        load_file_names = files_09
    else:
        load_file_names = all_files

    return load_file_names


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
        4) Add relationships
        """
        set_up_error_files()

        if kwargs["file"] is not None:
            load_file_names = kwargs["file"]
            # add uei
            if "duns" in load_file_names or "ein" in load_file_names or "ueis" in load_file_names:
                expected_objects_dict = load_lists(load_file_names)
            elif "agency" in load_file_names:
                expected_objects_dict = load_agency(load_file_names)
            else:
                expected_objects_dict = load_files([load_file_names])

        else:
            year = kwargs["year"]
            load_file_names = lookup_files(year)
            objects_dict = load_files(load_file_names)
            duns_objects_dict = load_lists(f"duns{year}.txt")
            eins_objects_dict = load_lists(f"eins{year}.txt")
            uei_objects_dict = load_lists(f"ueis{year}.txt")
            agency_objects_dict = load_agency(f"agency{year}.txt")

            expected_objects_dict = (
                objects_dict
                | duns_objects_dict
                | eins_objects_dict
                | agency_objects_dict
                | uei_objects_dict
            )

        timestamp = log_results(expected_objects_dict, kwargs)
        return str(timestamp)
