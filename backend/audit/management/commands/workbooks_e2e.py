import argparse

from django.core.management.base import BaseCommand
from users.models import User

import datetime
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
parser = argparse.ArgumentParser()

# Peewee runs a really noisy DEBUG log.
pw = logging.getLogger('peewee')
pw.addHandler(logging.StreamHandler())
pw.setLevel(logging.INFO)

from audit.fixtures.workbooks.workbook_creation import (
    sections,
    workbook_loader,
    setup_sac
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, required=True)
        parser.add_argument("--dbkey", type=str, required=True)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(email=options["email"])
        except User.DoesNotExist:
            logger.info(
                "No user found for %s, have you logged in once?", options["email"]
            )
            return
        entity_id = "DBKEY {dbkey} {date:%Y_%m_%d_%H_%M_%S}".format(
            dbkey=options["dbkey"], date=datetime.datetime.now()
        )
        sac = setup_sac(user, entity_id, options["dbkey"])
        loader = workbook_loader(user, sac, options["dbkey"], entity_id)
        json_test_tables = []
        for section, fun in sections.items():
            # FIXME: Can we conditionally upload the addl' and secondary workbooks?
            (_, json, _) = loader(fun, section)
            json_test_tables.append(json)
