from copy import deepcopy
from model_bakery import baker

from django.test import TestCase

from audit.models import SingleAuditChecklist
from config.settings import GSA_MIGRATION
from curation.curationlib.generate_resubmission_chains import (
    get_and_generate_submission_chains_by_equivalence,
    get_and_generate_submission_chains_by_distance,
    get_and_generate_submission_chain_by_report_ids,
)

sac_01 = {
    "audit_year": "2022",
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
        "version": 0,
    },
}


class DistanceChainingTests(TestCase):
    def test_no_chains(self):
        # Test on a single audit.
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        sorted_chains = get_and_generate_submission_chains_by_distance("2022")
        # No audits should be chained. There is only one.
        self.assertEqual(len(sorted_chains), 0)

    def test_one_chain(self):
        # Two identical audits should yield a chain
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"][:-1] + "2",
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        sorted_chains = get_and_generate_submission_chains_by_distance("2022")
        # These audits should chain, because they have the
        # same information in the critical fields.
        self.assertEqual(len(sorted_chains), 1)

    def test_email_difference(self):
        # A single-character difference in the email
        # should yield a single chain.
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )

        # Add a single character typo to the email address.
        # We should still get a chain.
        gi = deepcopy(sac_01["general_information"])
        gi["auditee_email"] = gi["auditee_email"][:-1] + "x"

        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"][:-1] + "2",
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=gi,
        )
        sorted_chains = get_and_generate_submission_chains_by_distance("2022")
        # A single-character typo in the email should not prevent
        # chaining. Unlike entity names, we'll assume that email
        # addresses can be slightly inconsistent.
        self.assertEqual(len(sorted_chains), 1)

    def test_different_state(self):
        # Different states should force the audits
        # into different chains for the same UEI.
        rid_count = 0
        for _ in range(2):
            for state in ["PA", "ME"]:
                rid_count += 1
                gi = deepcopy(sac_01["general_information"])
                gi["auditee_state"] = state
                baker.make(
                    SingleAuditChecklist,
                    report_id=sac_01["report_id"][:-1] + f"{rid_count}",
                    submission_status=sac_01["submission_status"],
                    transition_name=sac_01["transition_name"],
                    transition_date=sac_01["transition_date"],
                    general_information=gi,
                )
        sorted_chains = get_and_generate_submission_chains_by_distance("2022")
        # With four audits on two states, I expect two chains.
        self.assertEqual(len(sorted_chains), 2)

    def test_four_audits_two_eins(self):
        # Four audits.
        # RID1, UEI1, EIN1
        # RID2, UEI1, EIN1
        # RID3, UEI2, EIN2
        # RID4, UEI2, EIN2
        # Two chains of size two.
        rid_count = 0
        for _ in range(2):
            for ein in ["123456789", "123123123"]:
                rid_count += 1

                gi = deepcopy(sac_01["general_information"])
                gi["ein"] = ein

                rid = sac_01["report_id"][:-1] + f"{rid_count}"

                baker.make(
                    SingleAuditChecklist,
                    report_id=rid,
                    submission_status=sac_01["submission_status"],
                    transition_name=sac_01["transition_name"],
                    transition_date=sac_01["transition_date"],
                    general_information=gi,
                )

        sorted_chains = get_and_generate_submission_chains_by_distance("2022")
        # I expect two chains, one for each UEI, and each
        # set to be of size two.
        self.assertEqual(len(sorted_chains), 2)
        for chain in sorted_chains:
            self.assertEqual(len(chain), 2)


class EquivalenceChainingTests(TestCase):
    def test_no_chains_single_record(self):
        """A single record can never form a chain."""
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        sorted_chains = get_and_generate_submission_chains_by_equivalence("2022")
        self.assertEqual(len(sorted_chains), 0)

    def test_one_chain_identical_fields(self):
        """Two records with identical equivalence fields form exactly one chain."""
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"][:-1] + "2",
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        sorted_chains = get_and_generate_submission_chains_by_equivalence("2022")
        self.assertEqual(len(sorted_chains), 1)
        self.assertEqual(len(sorted_chains[0]), 2)

    def test_email_difference_no_chain(self):
        """A single character difference in email does not form a chain."""
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        gi = deepcopy(sac_01["general_information"])
        gi["auditee_email"] = gi["auditee_email"][:-1] + "x"
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"][:-1] + "2",
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=gi,
        )
        sorted_chains = get_and_generate_submission_chains_by_equivalence("2022")
        # Exact-match: a changed email means no shared key, so no chain.
        self.assertEqual(len(sorted_chains), 0)

    def test_four_audits_two_eins_two_chains(self):
        """Four audits split across two EINs should produce two chains of two."""
        rid_count = 0
        for _ in range(2):
            for ein in ["123456789", "123123123"]:
                rid_count += 1
                gi = deepcopy(sac_01["general_information"])
                gi["ein"] = ein
                baker.make(
                    SingleAuditChecklist,
                    report_id=sac_01["report_id"][:-1] + f"{rid_count}",
                    submission_status=sac_01["submission_status"],
                    transition_name=sac_01["transition_name"],
                    transition_date=sac_01["transition_date"],
                    general_information=gi,
                )
        sorted_chains = get_and_generate_submission_chains_by_equivalence("2022")
        self.assertEqual(len(sorted_chains), 2)
        for chain in sorted_chains:
            self.assertEqual(len(chain), 2)

    def test_gsa_migration_chains_with_matching_partial_key(self):
        """
        A GSA_MIGRATION record should be absorbed into a bucket whose
        partial key matches, regardless of UEI.
        """
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        gi_migration = deepcopy(sac_01["general_information"])
        gi_migration["auditee_uei"] = GSA_MIGRATION
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"][:-1] + "2",
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=gi_migration,
        )
        sorted_chains = get_and_generate_submission_chains_by_equivalence("2022")

        self.assertEqual(len(sorted_chains), 1)
        self.assertEqual(len(sorted_chains[0]), 2)

    def test_gsa_migration_only_records_chain_together(self):
        """
        Two GSA_MIGRATION records with the same partial key
        should form their own chain even without a GSAFAC peer.
        """
        gi_migration = deepcopy(sac_01["general_information"])
        gi_migration["auditee_uei"] = GSA_MIGRATION
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=gi_migration,
        )
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"][:-1] + "2",
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=gi_migration,
        )
        sorted_chains = get_and_generate_submission_chains_by_equivalence("2022")

        self.assertEqual(len(sorted_chains), 1)
        self.assertEqual(len(sorted_chains[0]), 2)

class ReportIdChainingTests(TestCase):
    sub = {
        "report_id": sac_01["report_id"],
        "submission_status": sac_01["submission_status"],
        "transition_name": sac_01["transition_name"],
        "transition_date": sac_01["transition_date"],
        "general_information": sac_01["general_information"],
        "resubmission_meta": sac_01["resubmission_meta"],
    }

    rid_1 = sac_01["report_id"]
    sub_1 = {
        **sub,
        "report_id": rid_1,
    }

    rid_2 = sac_01["report_id"][:-1] + "2"
    sub_2 = {
        **sub,
        "report_id": rid_2,
    }

    def test_one_chain_identical_fields(self):
        """Two records with identical UEI and AY form exactly one chain."""
        baker.make(
            SingleAuditChecklist,
            **self.sub_1,
        )
        baker.make(
            SingleAuditChecklist,
            **self.sub_2,
        )

        sorted_chains = get_and_generate_submission_chain_by_report_ids([self.rid_1, self.rid_2])
        self.assertEqual(len(sorted_chains), 1)
        self.assertEqual(len(sorted_chains[0]), 2)

    def test_no_chains_single_record(self):
        """A single record can never form a chain."""
        baker.make(
            SingleAuditChecklist,
            **self.sub,
        )
        sorted_chains = get_and_generate_submission_chain_by_report_ids([sac_01["report_id"]])
        self.assertEqual(len(sorted_chains), 0)

    def test_no_chains_different_ueis(self):
        """Two records with different UEIs can never form a chain."""
        baker.make(
            SingleAuditChecklist,
            **self.sub_1,
        )
        baker.make(
            SingleAuditChecklist,
            **{
                **self.sub_2,
                "general_information": {
                    **self.sub_2["general_information"],
                    "auditee_uei": "FOOBARUEI",
                },
            }
        )

        sorted_chains = get_and_generate_submission_chain_by_report_ids([self.rid_1, self.rid_2])
        self.assertEqual(len(sorted_chains), 0)

    def test_no_chains_different_ays(self):
        """Two records with different UEIs can never form a chain."""
        baker.make(
            SingleAuditChecklist,
            **self.sub_1,
        )
        baker.make(
            SingleAuditChecklist,
            **{
                **self.sub_2,
                "general_information": {
                    **self.sub_2["general_information"],
                    "auditee_fiscal_period_end": "2077-12-31",
                },
            }
        )

        sorted_chains = get_and_generate_submission_chain_by_report_ids([self.rid_1, self.rid_2])
        self.assertEqual(len(sorted_chains), 0)
