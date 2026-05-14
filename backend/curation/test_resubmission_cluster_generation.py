from copy import deepcopy
from model_bakery import baker

from django.test import TestCase

from audit.models import SingleAuditChecklist
from config.settings import GSA_MIGRATION
from curation.curationlib.generate_resubmission_clusters import (
    generate_resubmission_chains,
    generate_resubmission_chains_by_distance,
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
}


class DistanceClusteringTests(TestCase):
    def test_no_clusters(self):
        # Test on a single audit.
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        sorted_chains = generate_resubmission_chains_by_distance("2022")
        # No audits should be clustered. There is only one.
        self.assertEqual(len(sorted_chains), 0)

    def test_one_cluster(self):
        # Two identical audits should yield a cluster
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
        sorted_chains = generate_resubmission_chains_by_distance("2022")
        # These audits should cluster, because they have the
        # same information in the critical fields.
        self.assertEqual(len(sorted_chains), 1)

    def test_email_difference(self):
        # A single-character difference in the email
        # should yield a single cluster.
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )

        # Add a single character typo to the email address.
        # We should still get a cluster.
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
        sorted_chains = generate_resubmission_chains_by_distance("2022")
        # A single-character typo in the email should not prevent
        # clustering. Unlike entity names, we'll assume that email
        # addresses can be slightly inconsistent.
        self.assertEqual(len(sorted_chains), 1)

    def test_different_state(self):
        # Different states should force the audits
        # into different clusters for the same UEI.
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
        sorted_chains = generate_resubmission_chains_by_distance("2022")
        # With four audits on two states, I expect two clusters.
        self.assertEqual(len(sorted_chains), 2)

    def test_four_audits_two_eins(self):
        # Four audits.
        # RID1, UEI1, EIN1
        # RID2, UEI1, EIN1
        # RID3, UEI2, EIN2
        # RID4, UEI2, EIN2
        # Two clusters of size two.
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

        sorted_chains = generate_resubmission_chains_by_distance("2022")
        # I expect two clusters, one for each UEI, and each
        # set to be of size two.
        self.assertEqual(len(sorted_chains), 2)
        for chain in sorted_chains:
            self.assertEqual(len(s), 2)


class EquivalenceClusteringTests(TestCase):
    def test_no_clusters_single_record(self):
        """A single record can never form a chain."""
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        sorted_chains = generate_resubmission_chains("2022")
        self.assertEqual(len(sorted_chains), 0)

    def test_one_cluster_identical_fields(self):
        """Two records with identical equivalence fields form exactly one cluster."""
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
        sorted_chains = generate_resubmission_chains("2022")
        self.assertEqual(len(sorted_chains), 1)
        self.assertEqual(len(sorted_chains[0]), 2)

    def test_email_difference_no_cluster(self):
        """A single character difference in email does not form a cluster."""
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
        sorted_chains = generate_resubmission_chains("2022")
        # Exact-match: a changed email means no shared key, so no cluster.
        self.assertEqual(len(sorted_chains), 0)

    def test_four_audits_two_eins_two_clusters(self):
        """Four audits split across two EINs should produce two clusters of two."""
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
        sorted_chains = generate_resubmission_chains("2022")
        self.assertEqual(len(sorted_chains), 2)
        for chain in sorted_chains:
            self.assertEqual(len(s), 2)

    def test_gsa_migration_clusters_with_matching_partial_key(self):
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
        sorted_chains = generate_resubmission_chains("2022")

        self.assertEqual(len(sorted_chains), 1)
        self.assertEqual(len(sorted_chains[0]), 2)

    def test_gsa_migration_only_records_cluster_together(self):
        """
        Two GSA_MIGRATION records with the same partial key
        should form their own cluster even without a GSAFAC peer.
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
        sorted_chains = generate_resubmission_chains("2022")

        self.assertEqual(len(sorted_chains), 1)
        self.assertEqual(len(sorted_chains[0]), 2)
