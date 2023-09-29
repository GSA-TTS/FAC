import os
import logging
from io import StringIO

from django.core.management.base import BaseCommand
from django.core.management import call_command

from data_distro.management.commands.handle_errors import make_option_string
from data_distro.management.commands.load_files import (
    load_files,
    load_agency,
    load_lists,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    For local development run this to add some data_distro records so you can have some data to see and work with.
    """

    def handle(self, *args, **kwargs):
        # I am using our test data so the findings file has intentional errors

        # load the rest of the files normally
        files_to_load_1 = [
            "test_data/cfda.txt",
            "test_data/findingstext_formatted.txt",
        ]
        files_to_load_2 = [
            "test_data/captext_formatted.txt",
            "test_data/notes.txt",
            "test_data/revisions.txt",
            "test_data/passthrough.txt",
            "test_data/gen.txt",
            "test_data/cpas.txt",
        ]

        load_files(files_to_load_1)
        load_findings_with_error()
        load_files(files_to_load_2)
        load_lists("test_data/duns.txt")
        load_lists("test_data/eins.txt")
        load_lists("test_data/ueis.txt")
        load_agency("test_data/agency.txt")

        logger.warn("Test data loading complete")


def load_findings_with_error():
    out = ""
    date_stamp = call_command(
        "public_data_loader",
        stdout=out,
        stderr=StringIO(),
        **{"file": "test_data/findings.txt"},
    )
    options = make_option_string(**{"file": "test_data/findings.txt"})
    # clean up error files
    os.remove(f"data_distro/data_to_load/run_logs/Results_{options}_{date_stamp}.json")
    os.remove(
        f"data_distro/data_to_load/run_logs/Exceptions_{options}_{date_stamp}.json"
    )
    os.remove(f"data_distro/data_to_load/run_logs/Lines_{options}_{date_stamp}.json")
    os.remove(f"data_distro/data_to_load/run_logs/Errors_{options}_{date_stamp}.json")
