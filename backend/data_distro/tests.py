import datetime
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from data_distro.models import General


class TestDataProcessing(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestDataProcessing, cls).setUpClass()
        out = StringIO()
        call_command(
            "public_data_loader",
            stdout=out,
            stderr=StringIO(),
            **{"file": "test_data/gen.txt"},
        )
        call_command(
            "public_data_loader",
            stdout=out,
            stderr=StringIO(),
            **{"file": "test_data/cpas.txt"},
        )

    def test_general(self):
        # confirm all objects loaded
        loaded_generals = General.objects.all()
        self.assertEqual(25, len(loaded_generals))

    def test_values_general(self):
        """Look for sample expected values in general (depends on test_general)"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2013)[0]
        self.assertEqual(True, test_value.going_concern)
        self.assertEqual(False, test_value.reportable_condition)
        self.assertEqual(datetime.date(2014, 6, 30), test_value.fac_accepted_date)

    def test_values_auditee(self):
        """Look for expected values in linked auditee from general load (depends on test_general)"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2013)[0]
        auditee_value = test_value.auditee
        self.assertEqual(
            "PAENEE DEPARTMENT OF PARKS AND RECREATION", auditee_value.auditee_name
        )
        self.assertEqual("Leslie Knope", auditee_value.auditee_contact)

    def test_linked_auditor(self):
        """Look for expected values in linked auditor from general load (depends on test_general)"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2013)[0]
        auditor_value = test_value.auditor.all()[0]
        self.assertEqual("CONES OF DUNSHIRE INC.", auditor_value.cpa_firm_name)

    def test_cpas(self):
        """Load and test CPA load"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2014)[0]
        cpa_values = test_value.auditor.all()
        # loaded from gen.txt
        self.assertEqual("Unique CPA Name", cpa_values[0].cpa_firm_name)
        # loaded from cpas.txt
        self.assertEqual("Paul Bunyan, CPA", cpa_values[1].cpa_firm_name)


class TestExceptions(TestCase):
    def call_loader(self, *args, **kwargs):
        """Helper function to call command"""
        out = StringIO()
        call_command(
            "public_data_loader",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_end_to_end_exception_handling(self):
        """Loads agency data with 2 agency_cdfa null, those should not save"""
        with self.assertLogs(level="WARNING") as log_check:
            self.call_loader(file="test_data/agency.txt")
            self.assertTrue("2 errors" in log_check.output[-1])
