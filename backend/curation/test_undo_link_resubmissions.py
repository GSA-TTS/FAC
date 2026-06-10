from copy import deepcopy
from typing import Any, Dict
from model_bakery import baker

from django.test import TestCase

from audit.models import SingleAuditChecklist
from config.settings import GSA_MIGRATION
from curation.management.commands.undo_link_resubmissions import (
    _get_ordered_sac_chain,
    _load_report_ids,
)

sac: Dict[str, Any] = {
    "report_id": "2022-42-MAGIC-0000000001",
    "submission_status": "disseminated",
    "transition_name": [
        "ready_for_certification",
        "auditor_certified",
        "auditee_certified",
        "certified",
        "submitted",
        "disseminated",
    ],
    "transition_date": [
        "2023-09-26T00:00:00.000Z",
        "2023-09-26T10:11:52.000Z",
        "2023-09-26T13:19:56.000Z",
        "2023-09-26T00:00:00.000Z",
        "2023-09-26T00:00:00.000Z",
        "2024-01-20T01:12:35.065Z",
    ],
    "general_information": {
        "ein": "237399677",
        "auditee_uei": "GNU9RNVE6J68",
        "auditee_zip": "15942",
        "auditor_ein": "251390233",
        "auditee_city": "MINERAL POINT",
        "auditee_name": "JACKSON TOWNSHIP VOLUNTEER FIRE COMPANY",
        "auditee_email": "MS74CCHS@ATLANTICBB.NET",
        "auditee_state": "PA",
        "auditee_fiscal_period_end": "2022-12-31",
    },
    "resubmission_meta": {
        "version": 1,
    },
}

rid_1 = sac["report_id"]
sac_1 = {
    **sac,
    "report_id": rid_1,
}

rid_2 = sac["report_id"][:-1] + "2"
sac_2 = {
    **sac_1,
    "report_id": rid_2,
    "resubmission_meta": {
        **sac_1["resubmission_meta"],
        "version": 2,
    },
}

rid_3 = sac["report_id"][:-1] + "3"
sac_3 = {
    **sac_1,
    "report_id": rid_3,
    "resubmission_meta": {
        **sac_1["resubmission_meta"],
        "version": 3,
    },
}

def _bake_sacs(sacs):
    for sac in sacs:
        baker.make(
            SingleAuditChecklist,
            **sac,
        )

class GetOrderedSacChainTests(TestCase):
    def test_get_ordered_sac_chain(self):
        """Standard case"""
        _bake_sacs([sac_1, sac_2, sac_3])

        # report_ids out of order
        sac_chain = _get_ordered_sac_chain([rid_3, rid_1, rid_2])

        self.assertEqual(len(sac_chain), 3)
        sac_chain[0].report_id = rid_1
        sac_chain[1].report_id = rid_2
        sac_chain[2].report_id = rid_3

    def test_missing_sac(self):
        """Raises an exception when it can't find SACs for all report_ids"""
        _bake_sacs([sac_1, sac_2]) # sac_3 missing

        with self.assertRaises(RuntimeError):
            _get_ordered_sac_chain([rid_3, rid_1, rid_2])

class LoadReportIdsTests(TestCase):
    def test_load_report_ids(self):
        """Standard case"""
        _bake_sacs([sac_1, sac_2])

        rows = _load_report_ids([rid_1, rid_2])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["report_id"], rid_1)
        self.assertEqual(rows[1]["report_id"], rid_2)
