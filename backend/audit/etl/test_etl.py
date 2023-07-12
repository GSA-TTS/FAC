from django.test import TestCase

from model_bakery import baker

from audit.models import SingleAuditChecklist, User
from dissemination.models import General, GenAuditor
from . import sac_fixture as sac_fixture


class ETLTests(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        self.report_id_1 = ""
        super().__init__(methodName)

    def setUp(self):
        user = baker.make(User)
        self.sac = sac_fixture.load_single_audit_checklists_for_user(user)

    def test_load_all(self):
        self.sac.transition_to_ready_for_certification()
        sac_status = self.sac.submission_status
        self.assertEqual(sac_status, "ready_for_certification")

        self.sac.transition_to_auditor_certified()
        self.sac.transition_to_auditee_certified()
        self.sac.transition_to_certified()
        self.sac.transition_to_submitted()
        for name in self.sac.transition_name:
            print(name, self.sac.get_transition_date(name))
        sac_status = self.sac.submission_status
        self.assertEqual(sac_status, "submitted")

        gen = General.objects.first()
        print("General:", gen)
        self.assertEquals(self.sac.general_information["auditee_uei"], gen.auditee_uei)

        gen_auditor = GenAuditor.objects.first()
        print("GenAuditor:", gen_auditor)
        self.assertEquals(self.sac.report_id, gen_auditor.report_id)
