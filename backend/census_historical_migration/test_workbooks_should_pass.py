import logging
from django.test import TestCase
import os
from functools import reduce
from audit.context import set_sac_to_context
from model_bakery import baker
from audit.models import SingleAuditChecklist
from audit.test_workbooks_should_pass import process_workbook_set

logger = logging.getLogger(__name__)


class PassingWorkbooks(TestCase):
    def test_passing_workbooks(self):
        workbook_sets = reduce(
            os.path.join,
            ["census_historical_migration", "fixtures", "workbooks", "should_pass"],
        )
        sac = baker.make(SingleAuditChecklist)
        with set_sac_to_context(sac):
            for dirpath, dirnames, _ in os.walk(workbook_sets):
                for workbook_set in dirnames:
                    logger.info("Walking ", workbook_set)
                    process_workbook_set(
                        os.path.join(dirpath, workbook_set), is_gsa_migration=True
                    )
