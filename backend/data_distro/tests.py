import os
import datetime
import json
import csv
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from data_distro.models import General
from data_distro.mappings.upload_mapping import upload_mapping
from data_distro.management.commands.load_files import load_files, load_agency


def delete_files(date_stamp):
    os.remove(f"data_distro/data_to_load/run_logs/Results_{date_stamp}.json")
    os.remove(f"data_distro/data_to_load/run_logs/Exceptions_{date_stamp}.json")
    os.remove(f"data_distro/data_to_load/run_logs/Lines_{date_stamp}.json")
    os.remove(f"data_distro/data_to_load/run_logs/Errors_{date_stamp}.json")


def return_json(file):
    with open(file, "r") as results_raw:
        results = json.load(results_raw)
        return results


class TestDataProcessing(TestCase):
    """Testing mapping and transformations"""

    date_stamp1 = ""
    date_stamp2 = ""

    @classmethod
    def setUpClass(cls):
        """Sets up data and calls both kinds of file options using the management command"""
        super(TestDataProcessing, cls).setUpClass()
        out = StringIO()
        TestDataProcessing.date_stamp1 = call_command(
            "public_data_loader",
            stdout=out,
            stderr=StringIO(),
            **{"file": "test_data/gen.txt"},
        )
        load_files(["test_data/cpas.txt"])
        TestDataProcessing.date_stamp2 = call_command(
            "public_data_loader",
            stdout=out,
            stderr=StringIO(),
            **{"file": "test_data/eins.txt"},
        )
        load_agency("test_data/agency.txt")

    @classmethod
    def tearDownClass(cls):
        super(TestDataProcessing, cls).tearDownClass()
        os.remove(
            f"data_distro/data_to_load/run_logs/Results_{TestDataProcessing.date_stamp1}.json"
        )

        # If both logs are run in the same second, they will have the same file name
        if TestDataProcessing.date_stamp1 != TestDataProcessing.date_stamp2:
            os.remove(
                f"data_distro/data_to_load/run_logs/Results_{TestDataProcessing.date_stamp2}.json"
            )

    def test_general(self):
        """Confirm all objects loaded"""
        loaded_generals = General.objects.all()
        self.assertEqual(25, len(loaded_generals))

    def test_values_general(self):
        """Look for sample expected values in general"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2013)[0]
        self.assertEqual(True, test_value.going_concern)
        self.assertEqual(False, test_value.reportable_condition)
        self.assertEqual(datetime.date(2014, 6, 30), test_value.fac_accepted_date)

    def test_values_auditee(self):
        """Look for expected values in linked auditee from general load"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2013)[0]
        auditee_value = test_value.auditee
        self.assertEqual(
            "PAWNEE DEPARTMENT OF PARKS AND RECREATION", auditee_value.auditee_name
        )
        self.assertEqual("Leslie Knope", auditee_value.auditee_contact)

    def test_linked_auditor(self):
        """Look for expected values in linked auditor from general load"""
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
        """Load EIN in correct order"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2014)[0]
        test_agency = test_value.auditee
        # order matters
        self.assertEqual(
            [730776899, 8675309, 8675310, 8675311], list(test_agency.ein_list)
        )

    def test_agency_linkage(self):
        """Load agency in correct order"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2014)[0]
        agencies = test_value.agency
        self.assertEqual(
            [10, 77, 2], list(agencies.values_list("agency_cfda", flat=True))
        )


class TestExceptions(TestCase):
    """
    Make sure we are keeping track of exceptions throughout the process, so all data is accounted for.
    """

    out = ""
    date_stamp = ""

    @classmethod
    def setUpTestData(cls):
        TestExceptions.out = StringIO()
        load_files(["test_data/findingstext_formatted.txt"])
        TestExceptions.date_stamp = call_command(
            "public_data_loader",
            stdout=TestExceptions.out,
            stderr=StringIO(),
            **{"file": "test_data/findings.txt"},
        )

    @classmethod
    def tearDownClass(cls):
        super(TestExceptions, cls).tearDownClass()
        delete_files(TestExceptions.date_stamp)

    def run_with_logging(self):
        with self.assertLogs(level="WARNING") as log_check:
            out = StringIO()
            date_stamp = call_command(
                "public_data_loader",
                stdout=out,
                stderr=StringIO(),
                **{"file": "test_data/findings.txt"},
            )
        self.assertTrue("2 errors" in log_check.output[-1])
        delete_files(date_stamp)

    def test_result_logs(self):
        result_file = (
            f"data_distro/data_to_load/run_logs/Results_{self.date_stamp}.json"
        )
        results = return_json(result_file)

        expected_objects_dict = {"test_data/findings.txt": 4}
        self.assertEqual(results["expected_objects_dict"], expected_objects_dict)

    def test_error_logs(self):
        error_file = f"data_distro/data_to_load/run_logs/Errors_{self.date_stamp}.json"
        results = return_json(error_file)
        db_error = results[0]["findings"]["Findings"]["elec_audits_id"]
        self.assertEqual(db_error, 14012297)

    def test_exception_logs(self):
        exeception_file = (
            f"data_distro/data_to_load/run_logs/Exceptions_{self.date_stamp}.json"
        )
        results = return_json(exeception_file)
        self.assertEqual(len(results), 2)

    def test_line_logs(self):
        line_file = f"data_distro/data_to_load/run_logs/Lines_{self.date_stamp}.json"
        results = return_json(line_file)
        self.assertEqual(len(results), 1)


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
        with open("data_distro/mappings/new_upload_mapping.json") as new_mapping_file:
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

    def test_create_docs(self):
        out = StringIO()
        call_command(
            "create_docs",
            stdout=out,
            stderr=StringIO(),
        )

        headers = []
        with open("data_distro/mappings/FAC_data_dict.csv", newline="") as doc_file:
            csv_reader = csv.reader(doc_file)
            for row in csv_reader:
                headers = row
                break

        self.assertEqual(
            headers,
            ["Model name", "Field name", "Description", "Data Source", "Validation"],
        )

    @classmethod
    def tearDownClass(cls):
        super(TestDataMapping, cls).tearDownClass()
        os.remove("data_distro/mappings/new_upload_mapping.json")
        os.remove("data_distro/mappings/FAC_data_dict.csv")
