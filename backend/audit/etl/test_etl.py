from django.test import TestCase

from model_bakery import baker

from ..models import User
from dissemination.models import General, GenAuditor, FederalAward
from . import sac_fixture
from .etl import ETL


class ETLTests(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        self.report_id = ""
        super().__init__(methodName)

    def setUp(self):
        user = baker.make(User)
        self.sac = sac_fixture.load_single_audit_checklists_for_user(user)

    def test_load_general(self):
        etl = ETL(self.sac)
        etl.load_general()
        generals = General.objects.all()
        self.assertEqual(len(generals), 1)
        general = generals.first()
        self.assertEqual(self.sac.report_id, general.report_id)

    def test_load_federal_award(self):
        etl = ETL(self.sac)
        etl.load_federal_award()
        federal_awards = FederalAward.objects.all()
        self.assertEqual(len(federal_awards), 1)
        federal_award = federal_awards.first()
        self.assertEqual(self.sac.report_id, federal_award.report_id)

    def test_load_gen_auditor(self):
        etl = ETL(self.sac)
        etl.load_gen_auditor()
        gen_auditors = GenAuditor.objects.all()
        self.assertGreaterEqual(len(gen_auditors), 1)
        self.assertLessEqual(len(gen_auditors), 3)
        gen_auditor = gen_auditors.first()
        self.assertEqual(self.sac.report_id, gen_auditor.report_id)

    # TODO:  Let's work on this test and uncomment it later.
    # def test_load_all(self):
    #     self.sac.transition_to_ready_for_certification()
    #     sac_status = self.sac.submission_status
    #     self.assertEqual(sac_status, "ready_for_certification")

    #     self.sac.transition_to_auditor_certified()
    #     self.sac.transition_to_auditee_certified()
    #     self.sac.transition_to_certified()
    #     self.sac.transition_to_submitted()
    #     sac_status = self.sac.submission_status
    #     self.assertEqual(sac_status, "submitted")
