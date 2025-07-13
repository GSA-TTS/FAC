from curation.curationlib.cluster_resubmitted_reports import generate_clusters
from model_bakery import baker
from django.test import TestCase
from audit.models import SingleAuditChecklist
from copy import deepcopy

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


class ClusteringTests(TestCase):
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
        sorted_sets = generate_clusters("2022")
        # No audits should be clustered. There is only one.
        self.assertEqual(len(sorted_sets), 0)

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
        sorted_sets = generate_clusters("2022")
        # No audits should be clustered. There is only one.
        self.assertEqual(len(sorted_sets), 1)

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
        sorted_sets = generate_clusters("2022")
        # No audits should be clustered. There is only one.
        self.assertEqual(len(sorted_sets), 1)

    def test_different_state(self):
        # Different states should force the audits
        # into different clusters for the same UEI.
        rid_count = 0
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
        sorted_sets = generate_clusters("2022")
        # I expect each audit to be in its own cluster.
        self.assertEqual(len(sorted_sets), 2)

    def test_four_audits_two_eins(self):
        # Four audits.
        # RID1, UEI1, EIN1
        # RID2, UEI1, EIN1
        # RID3, UEI2, EIN2
        # RID4, UEI2, EIN2
        # Two clusters of size two.
        rid_count = 0
        for i in range(2):
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

        sorted_sets = generate_clusters("2022")
        # I expect two clusters, one for each UEI, and each
        # set to be of size two.
        self.assertEqual(len(sorted_sets), 2)
        for s in sorted_sets:
            self.assertEqual(len(s), 2)
