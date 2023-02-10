import os
import datetime
import json
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from data_distro.models import General
from data_distro.management.commands.link_data import add_agency, add_duns_eins
from data_distro.mappings.upload_mapping import upload_mapping


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
        add_duns_eins("test_data/eins.txt")
        add_agency("test_data/agency.txt")

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
            "PAWNEE DEPARTMENT OF PARKS AND RECREATION", auditee_value.auditee_name
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

    def test_ein_list(self):
        """load EIN in correct order"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2014)[0]
        test_agency = test_value.auditee
        # order matters
        self.assertEqual(
            [730776899, 8675309, 8675310, 8675311], list(test_agency.ein_list)
        )

    def test_agency_linkage(self):
        test_value = General.objects.filter(dbkey=100000, audit_year=2014)[0]
        agencies = test_value.agency
        self.assertEqual(
            [10, 77, 2], list(agencies.values_list("agency_cfda", flat=True))
        )


class TestExceptions(TestCase):
    """Make sure we are keeping track of exceptions throughout the process"""

    def test_end_to_end_exception_handling(self):
        """Loads findings table with 2 dbkeys null, those should not save"""
        with self.assertLogs(level="WARNING") as log_check:
            out = StringIO()
            call_command(
                "public_data_loader",
                stdout=out,
                stderr=StringIO(),
                **{"file": "test_data/findings.txt"},
            )
            self.assertTrue("2 errors" in log_check.output[-1])


class TestDataMapping(TestCase):
    """Make sure that as we update our models, we update our mapping for out upload script"""

    def test_upload_mapping(self):
        out = StringIO()
        call_command(
            "create_upload_mapping",
            stdout=out,
            stderr=StringIO(),
        )

        known_discrepencies_in_new = {
            # We use these to link the data but we don't store them to reduce redundancy
            "agency": {"DBKEY", "AUDITYEAR", "EIN"},
            # The same data is covered in general and cfda
            "cfda": {"EIN"},
            # We use these to link the data but we don't store them to reduce redundancy
            "cpas": {"DBKEY"},
            "gen": {"CPAEIN", "EIN"},
        }

        current_mapping = upload_mapping
        new_mapping_file = open("data_distro/mappings/new_upload_mapping.json")
        new_mapping = json.load(new_mapping_file)

        for table in current_mapping:
            current_table_set = set(current_mapping[table])
            new_table_set = set(new_mapping[table])

            missing_from_new = current_table_set - new_table_set
            missing_from_current = new_table_set - current_table_set

            # Missing from the new mapping
            if len(missing_from_new) > 0:
                self.assertEqual(
                    set(known_discrepencies_in_new[table]), missing_from_new
                )

            # Missing from the current mapping, nothing should be there now
            self.assertEqual(len(missing_from_current), 0)

    @classmethod
    def tearDownClass(cls):
        super(TestDataMapping, cls).tearDownClass()
        os.remove("data_distro/mappings/new_upload_mapping.json")
