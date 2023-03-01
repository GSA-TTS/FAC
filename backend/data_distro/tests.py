import os
import datetime
import json
import csv
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from data_distro.models import General, FederalAward, Finding
from data_distro.mappings.upload_mapping import upload_mapping
from data_distro.management.commands.load_files import load_files, load_agency
from data_distro.management.commands.handle_errors import make_option_string


def delete_files(date_stamp, options):
    os.remove(f"data_distro/data_to_load/run_logs/Results_{options}_{date_stamp}.json")
    os.remove(
        f"data_distro/data_to_load/run_logs/Exceptions_{options}_{date_stamp}.json"
    )
    os.remove(f"data_distro/data_to_load/run_logs/Lines_{options}_{date_stamp}.json")
    os.remove(f"data_distro/data_to_load/run_logs/Errors_{options}_{date_stamp}.json")


def return_json(file):
    with open(file, "r") as results_raw:
        results = json.load(results_raw)
        return results


class TestDataProcessing(TestCase):
    """Testing mapping and transformations"""

    date_stamp1 = ""
    date_stamp2 = ""
    options1 = ""
    options2 = ""

    @classmethod
    def setUpClass(cls):
        """Sets up data and calls both kinds of file options using the management command"""
        super(TestDataProcessing, cls).setUpClass()
        load_files(["test_data/cfda.txt"])
        load_files(["test_data/captext_formatted.txt"])
        load_files(["test_data/notes.txt"])
        load_files(["test_data/revisions.txt"])
        load_files(["test_data/passthrough.txt"])
        out = StringIO()
        TestDataProcessing.date_stamp1 = call_command(
            "public_data_loader",
            stdout=out,
            stderr=StringIO(),
            **{"file": "test_data/gen.txt"},
        )
        TestDataProcessing.options1 = make_option_string(
            **{"file": "test_data/gen.txt"}
        )
        load_files(["test_data/cpas.txt"])
        TestDataProcessing.date_stamp2 = call_command(
            "public_data_loader",
            stdout=out,
            stderr=StringIO(),
            **{"file": "test_data/eins.txt"},
        )
        TestDataProcessing.options2 = make_option_string(
            **{"file": "test_data/eins.txt"}
        )
        load_agency("test_data/agency.txt")

    @classmethod
    def tearDownClass(cls):
        super(TestDataProcessing, cls).tearDownClass()
        os.remove(
            f"data_distro/data_to_load/run_logs/Results_{TestDataProcessing.options1}_{TestDataProcessing.date_stamp1}.json"
        )
        os.remove(
            f"data_distro/data_to_load/run_logs/Results_{TestDataProcessing.options2}_{TestDataProcessing.date_stamp2}.json"
        )

    def test_general(self):
        """Confirm all gen objects loaded"""
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
        auditor_value = test_value.primary_auditor
        self.assertEqual("CONES OF DUNSHIRE INC.", auditor_value.cpa_firm_name)

    def test_cpas(self):
        """Load and test CPA load"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2014)[0]
        primary_value = test_value.primary_auditor
        secondary_values = test_value.secondary_auditors.all()[0]
        # loaded from gen.txt
        self.assertEqual("Unique CPA Name", primary_value.cpa_firm_name)
        # loaded from cpas.txt
        self.assertEqual("Paul Bunyan, CPA", secondary_values.cpa_firm_name)

    def test_ein_list(self):
        """Load EIN in correct order"""
        test_value = General.objects.filter(dbkey=100000, audit_year=2014)[0]
        test_agency = test_value.auditee
        # order matters
        self.assertEqual(
            [730776899, 8675309, 8675310, 8675311], list(test_agency.ein_list)
        )

    def test_federal_awards(self):
        """Load cfda table and link to general"""
        test_value = General.objects.get(dbkey=100000, audit_year=2003)
        fed_award = test_value.federal_awards.first()
        self.assertEqual(fed_award.federal_program_name, "PARK PROGRAM")

    def test_uei(self):
        test_value = General.objects.get(dbkey=100001, audit_year=1997).auditee
        self.assertEqual(["888888889"], test_value.uei_list)

    def test_captext_linkage(self):
        test_value = General.objects.get(dbkey=100001, audit_year=1997).cap_text
        cap_text_refs = test_value.values_list("finding_ref_number", flat=True)
        self.assertEqual(
            ["2021-002", "2021-001"],
            list(cap_text_refs),
        )

    def test_note_linkage(self):
        test_value = General.objects.get(dbkey=100000, audit_year=2021).notes
        note_sequence = test_value.values_list("sequence_number", flat=True)
        self.assertEqual(
            [3, 2, 1, 4],
            list(note_sequence),
        )

    def test_revision_linkage(self):
        test_value = General.objects.get(dbkey=100000, audit_year=2021).revision
        self.assertEqual(
            "EDUCATION STABILIZATION FUND ADDED AS MAJOR PROGRAM.",
            test_value.federal_awards_explain,
        )

    def test_passthough_linkage(self):
        test_value = General.objects.get(dbkey=100000, audit_year=2016)
        passthrough = test_value.passthrough.first()
        self.assertEqual("ENVHL202055881-00", passthrough.passthrough_id)

    def test_agency_linkage(self):
        """Load agency in correct order"""
        test_value = FederalAward.objects.filter(
            dbkey=100000, audit_year=2014, cpa_ein=8675309
        )[0]
        agency_prior_findings_list = test_value.agency_prior_findings_list
        self.assertEqual(
            [2, 77, 10],
            list(agency_prior_findings_list),
        )


class TestExceptions(TestCase):
    """
    Make sure we are keeping track of exceptions throughout the process, so all data is accounted for.
    Also testing linkage for findings
    """

    out = ""
    date_stamp = ""
    options = ""

    @classmethod
    def setUpTestData(cls):
        TestExceptions.out = StringIO()
        load_files(["test_data/cfda.txt"])
        load_files(["test_data/findingstext_formatted.txt"])
        TestExceptions.date_stamp = call_command(
            "public_data_loader",
            stdout=TestExceptions.out,
            stderr=StringIO(),
            **{"file": "test_data/findings.txt"},
        )
        TestExceptions.options = make_option_string(
            **{"file": "test_data/findings.txt"}
        )
        load_files(["test_data/gen.txt"])

    @classmethod
    def tearDownClass(cls):
        super(TestExceptions, cls).tearDownClass()
        delete_files(TestExceptions.date_stamp, TestExceptions.options)

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
        options = make_option_string(**{"file": "test_data/findings.txt"})
        delete_files(date_stamp, options)

    def test_result_logs(self):
        result_file = f"data_distro/data_to_load/run_logs/Results_{self.options}_{self.date_stamp}.json"
        results = return_json(result_file)

        # bad lines won't be included in the expected objects count
        expected_objects_dict = {"test_data/findings.txt": 6}
        self.assertEqual(results["expected_objects_dict"], expected_objects_dict)

    def test_error_logs(self):
        error_file = f"data_distro/data_to_load/run_logs/Errors_{self.options}_{self.date_stamp}.json"
        results = return_json(error_file)
        db_error = results[0]["findings"]["Finding"]["audit_id"]
        self.assertEqual(db_error, 14012297)

    def test_exception_logs(self):
        exeception_file = f"data_distro/data_to_load/run_logs/Exceptions_{self.options}_{self.date_stamp}.json"
        results = return_json(exeception_file)
        self.assertEqual(len(results), 2)

    def test_line_logs(self):
        line_file = f"data_distro/data_to_load/run_logs/Lines_{self.options}_{self.date_stamp}.json"
        results = return_json(line_file)
        self.assertEqual(len(results), 1)

    # The following tests aren't exception tests, but they work well with the setup class

    # this one
    def test_gen_finding_linkage(self):
        test_value = General.objects.get(dbkey=100000, audit_year=2014).findings
        finding_audit_ids = test_value.values_list("audit_id", flat=True)
        self.assertEqual(
            [14012297, 14012304, 14012297],
            list(finding_audit_ids),
        )

    def test_gen_findingtext_linkage(self):
        test_value = General.objects.get(dbkey=100000, audit_year=2014).findings_text
        sequence_numbers = test_value.values_list("seqence_number", flat=True)
        self.assertEqual(
            [1, 2, 3],
            list(sequence_numbers),
        )

    def test_finding_findingtext_linkage(self):
        test_value = Finding.objects.get(
            dbkey=100000, audit_year=2014, finding_ref_number="2021-002"
        ).findings_text
        sequence_numbers = test_value.values_list("seqence_number", flat=True)
        self.assertEqual(
            [1, 2],
            list(sequence_numbers),
        )


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

        known_discrepencies_in_current = {}

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

            # Missing from the current mapping
            if len(missing_from_current) > 0:
                self.assertEqual(
                    known_discrepencies_in_current[table], missing_from_current
                )

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
