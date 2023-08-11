from django.apps import apps
from django.core.management.base import BaseCommand
from users.models import User

import argparse
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
    setup_sac,
)

from audit.fixtures.workbooks.sac_creation import _post_upload_pdf

# # def transition(sac):
# #     SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
# #     # I couldn't use the transition functions. Don't know why.
# #     # In progress
# #     sac.transition_name.append(SingleAuditChecklist.STATUS.SUBMITTED)
# #     sac.transition_date.append(datetime.date.today())

# #     sac.transition_name.append(SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED)
# #     sac.transition_date.append(datetime.date.today())

# #     sac.transition_name.append(SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED)
# #     sac.transition_date.append(datetime.date.today())

# #     sac.transition_name.append(SingleAuditChecklist.STATUS.CERTIFIED)
# #     sac.transition_date.append(datetime.date.today())

# # def cross_validate(sac):
# #     print("CROSS VALIDATING")
# #     validation_functions = audit.cross_validation.functions

# #     shape = audit.cross_validation.sac_validation_shape(sac)
# #     for fun in validation_functions:
# #         fun(shape)

# #     sac.validate_cross()

# # def etl(sac):
# #     print("TRANSFERRING DATA... HARDER BETTER FASTER STRONGER ...")
# #     from audit.etl import ETL

# #     if sac.general_information:
# #         etl = ETL(sac)
# #         etl.load_all()

#     sac.transition_name.append(SingleAuditChecklist.STATUS.SUBMITTED)
#     sac.transition_date.append(date.today())
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
        _post_upload_pdf(sac, user, 'audit/fixtures/basic.pdf')
