from curation.curationlib.update_uei_or_ein import update_uei, update_ein
from model_bakery import baker
from django.test import TestCase
from audit.models import SingleAuditChecklist
from django.contrib.auth import get_user_model

User = get_user_model()

ORIG_UEI = "GNU9RNVE6J68"
NEW_UEI = "NEWUEINEWUEI"

ORIG_EIN = "123456789"
NEW_EIN = "987654321"

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
        "ein": "123456789",
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


class Args:
    pass


class UEIReplacementTests(TestCase):

    def test_update_uei(self):
        user = baker.make(User)
        user.email = "test@fac.gsa.gov"
        user.save()

        # Test on a single audit.
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )

        options = dict()
        options["report_id"] = "2022-42-MAGIC-0000000001"
        options["old_uei"] = ORIG_UEI
        options["new_uei"] = NEW_UEI
        options["email"] = user.email

        update_uei(options)
        sac = SingleAuditChecklist.objects.get(general_information__auditee_uei=NEW_UEI)
        self.assertEqual(sac.general_information["auditee_uei"], NEW_UEI)

    def test_update_one_record_uei_not_the_other(self):
        user = baker.make(User)
        user.email = "test@fac.gsa.gov"
        user.save()

        # Test on a single audit.
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        # Make sure we do not change this one.
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"][:-1] + "2",
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )

        options = dict()
        options["report_id"] = "2022-42-MAGIC-0000000001"
        options["old_uei"] = ORIG_UEI
        options["new_uei"] = NEW_UEI
        options["email"] = user.email

        update_uei(options)

        # Make sure the first audit changed
        sac = SingleAuditChecklist.objects.get(report_id="2022-42-MAGIC-0000000001")

        # This record should have a new UEI
        self.assertEqual(sac.general_information["auditee_uei"], NEW_UEI)
        # It should not have the old UEI (redundant)
        self.assertNotEqual(sac.general_information["auditee_uei"], ORIG_UEI)

        # Make sure the first audit changed, but the second audit (with the same UEI)
        # was not updated. This makes sure we only update by report ID.
        sac = SingleAuditChecklist.objects.get(report_id="2022-42-MAGIC-0000000002")
        self.assertEqual(sac.general_information["auditee_uei"], ORIG_UEI)


class EINReplacementTests(TestCase):

    def test_update_ein(self):
        user = baker.make(User)
        user.email = "test@fac.gsa.gov"
        user.save()

        # Test on a single audit.
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )

        options = dict()
        options["report_id"] = "2022-42-MAGIC-0000000001"
        options["old_ein"] = ORIG_EIN
        options["new_ein"] = NEW_EIN
        options["email"] = user.email

        update_ein(options)

        sac = SingleAuditChecklist.objects.get(report_id="2022-42-MAGIC-0000000001")
        self.assertEqual(sac.general_information["ein"], NEW_EIN)

    def test_update_one_record_ein_not_the_other(self):
        user = baker.make(User)
        user.email = "test@fac.gsa.gov"
        user.save()

        # Test on a single audit.
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"],
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )
        # Make sure we do not change this one.
        baker.make(
            SingleAuditChecklist,
            report_id=sac_01["report_id"][:-1] + "2",
            submission_status=sac_01["submission_status"],
            transition_name=sac_01["transition_name"],
            transition_date=sac_01["transition_date"],
            general_information=sac_01["general_information"],
        )

        options = dict()
        options["report_id"] = "2022-42-MAGIC-0000000001"
        options["old_ein"] = ORIG_EIN
        options["new_ein"] = NEW_EIN
        options["email"] = user.email

        update_ein(options)

        # Make sure the first audit changed
        sac = SingleAuditChecklist.objects.get(report_id="2022-42-MAGIC-0000000001")
        # This record should have a new EIN
        self.assertEqual(sac.general_information["ein"], NEW_EIN)
        # It should not have the old EIN (redundant)
        self.assertNotEqual(sac.general_information["ein"], ORIG_EIN)

        # Make sure the first audit changed, but the second audit (with the same UEI)
        # was not updated. This makes sure we only update by report ID.
        sac = SingleAuditChecklist.objects.get(report_id="2022-42-MAGIC-0000000002")
        self.assertEqual(sac.general_information["ein"], ORIG_EIN)
