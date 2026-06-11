from copy import deepcopy
from typing import Any, Dict
from model_bakery import baker
from copy import deepcopy

from django.test import TestCase
from django.contrib.auth.models import User

from audit.models import SingleAuditChecklist
from config.settings import GSA_MIGRATION
from curation.management.commands.undo_link_resubmissions import (
    _chain_creates_orphan,
    _get_ordered_sac_chain,
    _load_report_ids,
    _parse_meta,
    _restore_sacs,
    _safe_sac_getter,
)
from audit.models.constants import RESUBMISSION_STATUS


SAC: Dict[str, Any] = {
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
        "resubmission_status": RESUBMISSION_STATUS.UNKNOWN,
        "version": 1,
    },
}

rid_1 = SAC["report_id"]
rid_2 = SAC["report_id"][:-1] + "2"
rid_3 = SAC["report_id"][:-1] + "3"

sac_1 = {
    **SAC,
    "report_id": rid_1,
    "resubmission_meta": {
        **SAC["resubmission_meta"],
        "resubmission_status": RESUBMISSION_STATUS.DEPRECATED,
        "version": 1,
        "next_report_id": rid_2,
    },
}

sac_2 = {
    **SAC,
    "report_id": rid_2,
    "resubmission_meta": {
        **SAC["resubmission_meta"],
        "resubmission_status": RESUBMISSION_STATUS.DEPRECATED,
        "version": 2,
        "previous_report_id": rid_1,
        "next_report_id": rid_3,
    },
}

sac_3 = {
    **SAC,
    "report_id": rid_3,
    "resubmission_meta": {
        **SAC["resubmission_meta"],
        "resubmission_status": RESUBMISSION_STATUS.MOST_RECENT,
        "version": 3,
        "previous_report_id": rid_2,
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

class SafeSacGetterTests(TestCase):
    def test_safe_sac_getter(self):
        """Standard case"""
        _bake_sacs([sac_1])

        err, sac = _safe_sac_getter(rid_1)

        self.assertIsNone(err)
        self.assertEqual(sac.report_id, rid_1)

    def test_report_id_not_found(self):
        """report_id is not found"""
        err, sac = _safe_sac_getter(rid_1)

        self.assertIsInstance(err, SingleAuditChecklist.DoesNotExist)
        self.assertIsNone(sac)

class ParseMetaTests(TestCase):
    def test_parse_meta_report_ids(self):
        """Standard case from loading report_ids"""
        _bake_sacs([sac_1])
        row = _load_report_ids([rid_1])[0]

        err, meta = _parse_meta(row)

        self.assertIsNone(err)
        self.assertEqual(
            meta,
            {'version': 0, 'resubmission_status': RESUBMISSION_STATUS.UNKNOWN},
        )

class ChainCreatesOrphanTests(TestCase):
    def test_chain_creates_orphan_start(self):
        """Detects an orphan at the start of the chain"""
        _bake_sacs([sac_1, sac_2, sac_3])

        # Orphans sac_1
        rows = _load_report_ids([rid_2, rid_3])

        self.assertTrue(_chain_creates_orphan(rows, init_len=len(rows)))

    def test_chain_creates_orphan_middle(self):
        """Detects an orphan in the middle of the chain"""
        _bake_sacs([sac_1, sac_2, sac_3])

        # Orphans sac_2
        rows = _load_report_ids([rid_1, rid_3])

        self.assertTrue(_chain_creates_orphan(rows, init_len=len(rows)))

    def test_chain_creates_orphan_end(self):
        """Detects an orphan at the end of the chain"""
        _bake_sacs([sac_1, sac_2, sac_3])

        # Orphans sac_3
        rows = _load_report_ids([rid_1, rid_2])

        self.assertTrue(_chain_creates_orphan(rows, init_len=len(rows)))

    def test_chain_creates_orphan_missing_prev_rid(self):
        """Detects a missing previous_report_id"""
        bad_sac_2 = deepcopy(sac_2)
        bad_sac_2["resubmission_meta"]["previous_report_id"] = None
        _bake_sacs([sac_1, bad_sac_2, sac_3])
        rows = _load_report_ids([rid_1, rid_2, rid_3])

        self.assertTrue(_chain_creates_orphan(rows, init_len=len(rows)))

    def test_chain_creates_orphan_missing_next_rid(self):
        """Detects a missing next_report_id"""
        bad_sac_2 = deepcopy(sac_2)
        bad_sac_2["resubmission_meta"]["next_report_id"] = None
        _bake_sacs([sac_1, bad_sac_2, sac_3])
        rows = _load_report_ids([rid_1, rid_2, rid_3])

        self.assertTrue(_chain_creates_orphan(rows, init_len=len(rows)))

    def test_chain_creates_orphan_unordered(self):
        """Detects chain ordering doesn't match previous/next_report_id in resub metas"""
        _bake_sacs([sac_1, sac_2, sac_3])

        # _load_report_ids auto-sorts by version, so undo that
        rows = _load_report_ids([rid_1, rid_2, rid_3])
        unordered_rows = [rows[0], rows[2], rows[1]]

        self.assertTrue(_chain_creates_orphan(unordered_rows, init_len=len(rows)))

    def test_chain_no_orphan(self):
        """Detects no orphan"""
        _bake_sacs([sac_1, sac_2, sac_3])
        rows = _load_report_ids([rid_1, rid_2, rid_3])

        self.assertFalse(_chain_creates_orphan(rows, init_len=len(rows)))

class RestoreSacsTests(TestCase):
    def test_restore_sacs(self):
        """Standard case"""
        _bake_sacs([sac_1, sac_2, sac_3])
        rids = [rid_1, rid_2, rid_3]
        rows = _load_report_ids(rids)

        user = baker.make(User, is_staff=True)
        _restore_sacs(rows, user)

        sacs = SingleAuditChecklist.objects.filter(report_id__in=rids)
        for sac in sacs:
            self.assertEqual(sac.resubmission_meta["resubmission_status"], RESUBMISSION_STATUS.UNKNOWN)
            self.assertEqual(sac.resubmission_meta["version"], 0)

    def test_restore_sacs_orphan(self):
        """Doesn't link due to orphan detected"""
        _bake_sacs([sac_1, sac_2, sac_3])
        rids = [rid_1, rid_2] # sac_3 missing
        rows = _load_report_ids(rids)

        user = baker.make(User, is_staff=True)
        _restore_sacs(rows, user)

        sacs = SingleAuditChecklist.objects.filter(report_id__in=rids)
        for sac in sacs:
            self.assertNotEqual(sac.resubmission_meta["resubmission_status"], RESUBMISSION_STATUS.UNKNOWN)
            self.assertNotEqual(sac.resubmission_meta["version"], 0)
