from .sac_general_lib.sac_creator import setup_sac
from audit.models import User

from model_bakery import baker
from unittest import TestCase
from django.conf import settings


class TestSacTribalConsent(TestCase):
    class MockAuditHeader:
        def __init__(
            self,
            entity_type,
            suppression_code,
        ):
            self.AUDITEECONTACT = "Scrooge Jones"
            self.AUDITEEEMAIL = "auditee.mcaudited@leftfield.com"
            self.AUDITEENAME = "Designate Representative"
            self.AUDITEEPHONE = "5558675309"
            self.AUDITEETITLE = "Lord of Doors"
            self.AUDITOR_EIN = "987654321"
            self.AUDITTYPE = "S"
            self.AUDITYEAR = "2022"
            self.CITY = "New York"
            self.CPACITY = "Podunk"
            self.CPACONTACT = "Qualified Human Accountant"
            self.CPACOUNTRY = "US"
            self.CPAEMAIL = "qualified.human.accountant@dollarauditstore.com"
            self.CPAFIRMNAME = "Dollar Audit Store"
            self.CPAPHONE = "0008675309"
            self.CPASTATE = "NY"
            self.CPASTREET1 = "100 Percent Respectable St."
            self.CPATITLE = "Just an ordinary person"
            self.CPAZIPCODE = "14886"
            self.DBKEY = "123456789"
            self.DOLLARTHRESHOLD = "750000"
            self.EIN = "134278617"
            self.ENTITY_TYPE = entity_type
            self.FYENDDATE = "01/01/2022 00:00:00"
            self.GOINGCONCERN = "N"
            self.LOWRISK = "N"
            self.MATERIALNONCOMPLIANCE = "N"
            self.MATERIALWEAKNESS = "N"
            self.MATERIALWEAKNESS_MP = "N"
            self.MULTIPLE_CPAS = "N"
            self.MULTIPLEEINS = "N"
            self.MULTIPLEUEIS = "N"
            self.PERIODCOVERED = "A"
            self.REPORTABLECONDITION = "N"
            self.SP_FRAMEWORK = "cash"
            self.SP_FRAMEWORK_REQUIRED = "Y"
            self.STATE = "NY"
            self.STREET1 = "200 feet into left field"
            self.SUPPRESSION_CODE = suppression_code
            self.TYPEREPORT_FS = "UQADS"
            self.TYPEREPORT_SP_FRAMEWORK = "UQAD"
            self.UEI = "ZQGGHJH74DW7"
            self.ZIPCODE = "10451"
            self.COGAGENCY = "14"
            self.OVERSIGHTAGENCY = "84"

    def _mock_audit_header(self, entity_type, suppression_code=None):
        """Returns a mock audit header with all necessary fields"""
        return self.MockAuditHeader(entity_type, suppression_code)

    def _test_consent(self, consent, is_public):
        """Tests the values found within sac.tribal_data_consent"""
        self.assertEqual(
            consent["tribal_authorization_certifying_official_title"],
            settings.GSA_MIGRATION,
        )
        self.assertEqual(
            consent["is_tribal_information_authorized_to_be_public"],
            is_public,
        )
        self.assertEqual(
            consent["tribal_authorization_certifying_official_name"],
            settings.GSA_MIGRATION,
        )

    def test_non_tribal(self):
        """Only 'tribal' entity types have tribal_data_consent populated"""
        audit_header = self._mock_audit_header("non-profit")
        user = baker.make(User)
        sac = setup_sac(user, audit_header)

        self.assertIsNone(sac.tribal_data_consent)

    def test_tribal_public(self):
        """Misc suppression codes makes them public"""
        audit_header = self._mock_audit_header("tribal", "foo")
        user = baker.make(User)
        sac = setup_sac(user, audit_header)
        consent = sac.tribal_data_consent

        self.assertIsNotNone(sac.tribal_data_consent)
        self._test_consent(consent, True)

    def test_tribal_public_no_code(self):
        """A missing suppression code makes them public"""
        audit_header = self._mock_audit_header("tribal", "")
        user = baker.make(User)
        sac = setup_sac(user, audit_header)
        consent = sac.tribal_data_consent

        self.assertIsNotNone(sac.tribal_data_consent)
        self._test_consent(consent, True)

    def test_tribal_private(self):
        """A tribal audit with suppression code 'it' will be private"""
        audit_header = self._mock_audit_header("tribal", "it")
        user = baker.make(User)
        sac = setup_sac(user, audit_header)
        consent = sac.tribal_data_consent

        self.assertIsNotNone(sac.tribal_data_consent)
        self._test_consent(consent, False)
