import json
import string
from unittest import TestCase
from unittest.mock import patch
from django.conf import settings
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import TemporaryUploadedFile
from random import choice, randrange
from openpyxl import Workbook
from tempfile import NamedTemporaryFile

import requests

from audit.fixtures.excel import (
    SIMPLE_CASES_TEST_FILE,
    CORRECTIVE_ACTION_TEMPLATE_DEFINITION,
    ADDITIONAL_UEIS_TEMPLATE_DEFINITION,
    SECONDARY_AUDITORS_TEMPLATE_DEFINITION,
    NOTES_TO_SEFA_TEMPLATE_DEFINITION,
)

from .validators import (
    ALLOWED_EXCEL_CONTENT_TYPES,
    ALLOWED_EXCEL_FILE_EXTENSIONS,
    MAX_EXCEL_FILE_SIZE_MB,
    validate_additional_ueis_json,
    validate_notes_to_sefa_json,
    validate_corrective_action_plan_json,
    validate_file_content_type,
    validate_file_extension,
    validate_excel_file_integrity,
    validate_file_size,
    validate_federal_award_json,
    validate_secondary_auditors_json,
    validate_file_infection,
    validate_pdf_file_integrity,
    validate_uei,
    validate_uei_alphanumeric,
    validate_uei_valid_chars,
    validate_uei_leading_char,
    validate_uei_nine_digit_sequences,
)

# Simplest way to create a new copy of simple case rather than getting
# references to things used by other tests:
jsoncopy = lambda v: json.loads(json.dumps(v))


# use this to match the class signature expected in validate_excel_file_content_type, file.file.content_type
class FileWrapper:
    def __init__(self, file):
        self.file = file
        self.name = file.name


class FederalAwardsValidatorTests(SimpleTestCase):
    """
    We want to make sure that SingleAuditChecklist.federal_awards is going
    through JSON Schema validation, but the full set of JSON Schema tests is in
    test_schemas.py
    """

    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "FederalAwardsCases"
    ][0]

    def test_validation_is_applied(self):
        """
        Empty Federal Awards should fail, simple case should pass.
        """
        invalid = json.loads('{"FederalAwards":{}}')
        expected_msg = "[\"'Federal Awards' is a required property.\"]"
        self.assertRaisesRegex(
            ValidationError, expected_msg, validate_federal_award_json, invalid
        )

        simple = FederalAwardsValidatorTests.SIMPLE_CASE
        validate_federal_award_json(simple)

    def test_prefix_under_ten(self):
        """
        Prefixes between 00 and 09 should fail
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        # pick a prefix between 00 and 09 (invalid)
        prefix = f"{randrange(10):02}"
        # 20230512 HDMS FIXME: For some reasons, this fails randomly. I suspect it's because the random number generated is sometimes incorrect ,i.e., has less than three digits.
        # pick an extension beteween 001 and 999 (valid)
        extension = f"{randrange(100, 1000):03}"

        simple["FederalAwards"]["federal_awards"][0]["program"][
            "federal_agency_prefix"
        ] = f"{prefix}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "three_digit_extension"
        ] = f"{extension}"

        with self.assertRaises(
            ValidationError,
            msg=f"ValidationError not raised with prefix = {prefix}, extension = {extension}",
        ):
            validate_federal_award_json(simple)

    def test_prefix_over_99(self):
        """
        Prefixes over 99 should fail
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        # pick a prefix between 100 and 999 (invalid)
        prefix = f"{randrange(100, 1000):03}"
        # pick an extension beteween 001 and 999 (valid)
        extension = f"{randrange(100, 1000):03}"

        simple["FederalAwards"]["federal_awards"][0]["program"][
            "federal_agency_prefix"
        ] = f"{prefix}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "three_digit_extension"
        ] = f"{extension}"

        with self.assertRaises(
            ValidationError,
            msg=f"ValidationError not raised with prefix = {prefix}, extension = {extension}",
        ):
            validate_federal_award_json(simple)

    def test_prefix_non_numeric(self):
        """
        Prefixes with non-numeric characters should fail
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        # pick prefixes that contain one or two non-numeric characters
        prefixes = [
            f"{choice(string.ascii_letters)}{randrange(10):1}",  # e.g. A1
            f"{randrange(10):1}{choice(string.ascii_letters)}",  # e.g. 1A
            f"{choice(string.ascii_letters)}{choice(string.ascii_letters)}",  # e.g. AA
        ]

        # pick an extension between 001 and 999 (valid)
        extension = f"{randrange(100, 1000):03}"

        for prefix in prefixes:
            with self.subTest():
                simple["FederalAwards"]["federal_awards"][0]["program"][
                    "federal_agency_prefix"
                ] = f"{prefix}"
                simple["FederalAwards"]["federal_awards"][0]["program"][
                    "three_digit_extension"
                ] = f"{extension}"

                with self.assertRaises(
                    ValidationError,
                    msg=f"ValidationError not raised with prefix = {prefix}, extension = {extension}",
                ):
                    validate_federal_award_json(simple)

    def test_extension_RD(self):
        """
        A CFDA extension of RD should pass
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)
        # 20230512 HDMS FIXME: This is wrong. Not all two digits from 10 to 20  are valid. Changed to 10 to 69 for now.
        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 20):02}"
        # use RD as extension (valid)
        extension = "RD"

        simple["FederalAwards"]["federal_awards"][0]["program"][
            "federal_agency_prefix"
        ] = f"{prefix}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "three_digit_extension"
        ] = f"{extension}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "additional_award_identification"
        ] = "1234567"
        validate_federal_award_json(simple)

    def test_extension_U(self):
        """
        A CFDA extension of U## should pass
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 20):02}"
        # pick an extension between U10 and U99 (valid)
        extension = f"U{randrange(10, 100):02}"

        simple["FederalAwards"]["federal_awards"][0]["program"][
            "federal_agency_prefix"
        ] = f"{prefix}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "three_digit_extension"
        ] = f"{extension}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "additional_award_identification"
        ] = "1234567"

        validate_federal_award_json(simple)

    def test_extension_U_single_digit(self):
        """
        A CFDA extension of U# should fail
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 70):02}"
        # pick an extension between U0 and U9
        extension = f"U{randrange(10):1}"

        simple["FederalAwards"]["federal_awards"][0]["program"][
            "federal_agency_prefix"
        ] = f"{prefix}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "three_digit_extension"
        ] = f"{extension}"

        with self.assertRaises(
            ValidationError,
            msg=f"ValidationError not raised with prefix = {prefix}, extension = {extension}",
        ):
            validate_federal_award_json(simple)

    def test_extension_U_three_digit(self):
        """
        A CFDA extension of U### should fail
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        prefix = f"{randrange(10, 70):02}"
        # pick an extension between U001 and U999
        extension = f"U{randrange(1000):03}"

        simple["FederalAwards"]["federal_awards"][0]["program"][
            "federal_agency_prefix"
        ] = f"{prefix}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "three_digit_extension"
        ] = f"{extension}"

        with self.assertRaises(
            ValidationError,
            msg=f"ValidationError not raised with prefix = {prefix}, extension = {extension}",
        ):
            validate_federal_award_json(simple)

    def test_three_digit_extension(self):
        """
        A three digit numeric CFDA extension should pass
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 20):02}"
        # pick an extension between 001 and 999 (valid)
        extension = f"{randrange(100, 1000):03}"

        simple["FederalAwards"]["federal_awards"][0]["program"][
            "federal_agency_prefix"
        ] = f"{prefix}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "three_digit_extension"
        ] = f"{extension}"

        validate_federal_award_json(simple)

    def test_four_plus_extension(self):
        """
        A CFDA extension with four digits should fail
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 20):02}"
        # pick an extension with four or more digits
        extension = f"{randrange(1000):04}"

        simple["FederalAwards"]["federal_awards"][0]["program"][
            "federal_agency_prefix"
        ] = f"{prefix}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "three_digit_extension"
        ] = f"{extension}"

        with self.assertRaises(
            ValidationError,
            msg=f"ValidationError not raised with prefix = {prefix}, extension = {extension}",
        ):
            validate_federal_award_json(simple)

    def test_trailing_extension_letter(self):
        """
        A CFDA extension with 3 numeric digits and a trailing letter should pass
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 20):02}"
        # pick an extension between 001 and 999 with a trailing letter (valid)
        extension = f"{randrange(100, 1000):03}{choice(string.ascii_letters)}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "federal_agency_prefix"
        ] = f"{prefix}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "three_digit_extension"
        ] = f"{extension}"

        validate_federal_award_json(simple)

    def test_trailing_extension_letters(self):
        """
        A CFDA extension with 3 numeric digits and multiple trailing letters should fail
        """
        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 20):02}"
        # pick an extension between 001 and 999 with 2 trailing letters (invalid)
        extension = f"{randrange(100, 1000):03}{choice(string.ascii_letters)}{choice(string.ascii_letters)}"

        simple["FederalAwards"]["federal_awards"][0]["program"][
            "federal_agency_prefix"
        ] = f"{prefix}"
        simple["FederalAwards"]["federal_awards"][0]["program"][
            "three_digit_extension"
        ] = f"{extension}"

        with self.assertRaises(
            ValidationError,
            msg=f"ValidationError not raised with prefix = {prefix}, extension = {extension}",
        ):
            validate_federal_award_json(simple)

    def test_extension_non_numeric(self):
        """
        Extensions with non-numeric characters (except RD, U##, and trailing letter) should fail
        """
        ascii_letters_omit_RD = string.ascii_letters.replace("D", "").replace("R", "")
        ascii_letters_omit_U = string.ascii_letters.replace("U", "")

        simple = jsoncopy(FederalAwardsValidatorTests.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 20):02}"

        # pick extensions with one or more non-numeric characters
        extensions = [
            f"{choice(string.ascii_letters)}",  # e.g. A
            f"{choice(ascii_letters_omit_RD)}{choice(ascii_letters_omit_RD)}",  # e.g. AB
            f"{choice(string.ascii_letters)}{choice(string.ascii_letters)}{choice(string.ascii_letters)}",  # e.g. ABC
            f"{choice(ascii_letters_omit_U)}{randrange(100):02}",  # e.g. A01
            f"{choice(string.ascii_letters)}{choice(string.ascii_letters)}{randrange(10):1}",  # e.g. AB1
        ]

        for extension in extensions:
            with self.subTest():
                simple["FederalAwards"]["federal_awards"][0]["program"][
                    "federal_agency_prefix"
                ] = f"{prefix}"
                simple["FederalAwards"]["federal_awards"][0]["program"][
                    "three_digit_extension"
                ] = f"{extension}"

                with self.assertRaises(
                    ValidationError,
                    msg=f"ValidationError not raised with prefix = {prefix}, extension = {extension}",
                ):
                    validate_federal_award_json(simple)


class UEIValidatorTests(SimpleTestCase):
    """
    This is for local and pattern-based validation only; this does not perform
    any external queries to verify that given UEIs exist in the world.
    """

    # Valid UEI
    valid = "ABC123DEF456"

    def test_uei(self):
        """UEI is valid using all tests"""
        invalid = "000000000000"

        # Invalid UEI
        self.assertRaises(ValidationError, validate_uei, invalid)
        # Valid UEI
        validate_uei(self.valid)

    def test_uei_is_alphanumeric_only(self):
        """UEI is alphanumeric only"""
        invalid = "!@#123ABC456"

        # Invalid UEI
        self.assertRaises(ValidationError, validate_uei_alphanumeric, invalid)
        # Valid UEI
        validate_uei(self.valid)

    def test_uei_does_not_contain_o_or_i(self):
        """UEI does not contain O or I"""
        contains_o = "ABCo123"
        contains_O = "ABCO123"
        contains_i = "ABC0i23"
        contains_I = "ABC0I23"

        # UEI with o
        self.assertRaises(ValidationError, validate_uei_valid_chars, contains_o)
        # UEI with O
        self.assertRaises(ValidationError, validate_uei_valid_chars, contains_O)
        # UEI with i
        self.assertRaises(ValidationError, validate_uei_valid_chars, contains_i)
        # UEI with I
        self.assertRaises(ValidationError, validate_uei_valid_chars, contains_I)
        # Valid UEI
        validate_uei_valid_chars(self.valid)

    def test_uei_does_not_start_with_0(self):
        """UEI does not start with 0"""
        invalid = "012345678901"

        # UEI starts with O
        self.assertRaises(ValidationError, validate_uei_leading_char, invalid)
        # Valid UEI
        validate_uei_leading_char(self.valid)

    def test_uei_does_not_contain_9_digit_sequence(self):
        """UEI does not contain 9 digit sequence"""
        invalid = "12345678901"

        # UEI contains 9 digit sequence
        self.assertRaises(ValidationError, validate_uei_nine_digit_sequences, invalid)
        # Valid UEI
        validate_uei_nine_digit_sequences(self.valid)


class FileExtensionValidatorTests(SimpleTestCase):
    def test_invalid_file_extensions(self):
        """
        Filenames that have disallowed extensions are not valid
        """

        def random_extension(len):
            return "." + "".join(choice(string.ascii_lowercase) for _ in range(len))

        # generate a random length-3 file extension not listed as being allowed
        while (random_ext_3 := random_extension(3)) in ALLOWED_EXCEL_FILE_EXTENSIONS:
            pass

        # generate a random length-4 file extension not listed as being allowed
        while (random_ext_4 := random_extension(4)) in ALLOWED_EXCEL_FILE_EXTENSIONS:
            pass

        test_cases = [
            "file.pdf",
            "file.doc",
            "file.docx",
            "file.png",
            "file.jpeg",
            f"file.{random_ext_3}",
            f"file.{random_ext_4}",
            "file",
            "file.",
        ]

        for test_case in test_cases:
            with self.subTest():
                file = TemporaryUploadedFile(
                    test_case, ALLOWED_EXCEL_CONTENT_TYPES[0], 10000, "utf-8"
                )

                with self.assertRaises(
                    ValidationError,
                    msg=f"ValidationError not raised with filename = {test_case}",
                ):
                    validate_file_extension(file, ALLOWED_EXCEL_FILE_EXTENSIONS)

    def test_valid_file_extensions(self):
        """Filenames that have allowed extensions are valid"""
        test_cases = [e.lower() for e in ALLOWED_EXCEL_FILE_EXTENSIONS] + [
            e.upper() for e in ALLOWED_EXCEL_FILE_EXTENSIONS
        ]

        for test_case in test_cases:
            with self.subTest():
                filename = f"file.{test_case}"
                file = TemporaryUploadedFile(
                    filename, ALLOWED_EXCEL_CONTENT_TYPES[0], 10000, "utf-8"
                )

                validate_file_extension(file, ALLOWED_EXCEL_FILE_EXTENSIONS)


class FileContentTypeValidatorTests(SimpleTestCase):
    def test_invalid_file_content_types(self):
        """Files that have disallowed content types are invalid"""
        test_cases = [
            "application/msword",
            "application/octet-stream",
            "application/pdf",
            "application/vnd.ms-outlook",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "audio/mpeg",
            "audio/wav",
            "audio/x-aiff",
            "image/bmp",
            "image/jpeg",
            "image/gif",
            "image/png",
            "image/tiff",
            "text/csv",
            "text/plain",
        ]

        for test_case in test_cases:
            with self.subTest():
                file = FileWrapper(
                    TemporaryUploadedFile("file.ext", test_case, 10000, "utf-8")
                )

                self.assertRaises(
                    ValidationError,
                    validate_file_content_type,
                    file,
                    ALLOWED_EXCEL_CONTENT_TYPES,
                )

    def test_valid_file_content_types(self):
        """Files that have allowed content types are valid"""
        for content_type in ALLOWED_EXCEL_CONTENT_TYPES:
            with self.subTest():
                file = FileWrapper(
                    TemporaryUploadedFile("file.xlsx", content_type, 10000, "utf-8")
                )

                validate_file_content_type(file, ALLOWED_EXCEL_CONTENT_TYPES)


class FileFileSizeValidatorTests(SimpleTestCase):
    def test_valid_file_size(self):
        """Files that are under (or equal to) the maximum file size are valid"""
        max_file_size = MAX_EXCEL_FILE_SIZE_MB * 1024 * 1024

        test_cases = [
            max_file_size / 2,
            max_file_size,
        ]

        for test_case in test_cases:
            with self.subTest():
                file = TemporaryUploadedFile(
                    "file.xlsx", b"this is a file", test_case, "utf-8"
                )

                validate_file_size(file, MAX_EXCEL_FILE_SIZE_MB)

    def test_invalid_file_size(self):
        """Files that are over the maximum file size are invalid"""
        max_file_size = MAX_EXCEL_FILE_SIZE_MB * 1024 * 1024

        test_cases = [
            max_file_size + 1,
            max_file_size * 2,
        ]

        for test_case in test_cases:
            with self.subTest():
                file = TemporaryUploadedFile(
                    "file.xlsx", b"this is a file", test_case, "utf-8"
                )

                self.assertRaises(
                    ValidationError, validate_file_size, file, MAX_EXCEL_FILE_SIZE_MB
                )


class MockHttpResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


class FileInfectionValidatorTests(TestCase):
    def setUp(self):
        self.fake_file = TemporaryUploadedFile("file.txt", "text/plain", 10000, "utf-8")

    @patch("requests.post")
    def test_av_service_unavailable(self, mock_post):
        """If the AV service is unavailable, the file should not pass validation"""
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "service unavailable"
        )

        with self.assertRaises(ValidationError):
            validate_file_infection(self.fake_file)

    @patch("audit.validators._scan_file")
    def test_validation_fails_on_av_service_error(self, mock_scan_file):
        """If the AV service returns an internal error, the file should not pass validation"""
        mock_scan_file.return_value = MockHttpResponse(500, "error text")

        with self.assertRaises(ValidationError):
            validate_file_infection(self.fake_file)

    @patch("audit.validators._scan_file")
    def test_validation_fails_on_non_success_response(self, mock_scan_file):
        """If the AV service indicates that the file is infected, the file should not pass validation"""
        mock_scan_file.return_value = MockHttpResponse(406, "infected!")

        with self.assertRaises(ValidationError):
            validate_file_infection(self.fake_file)

    @patch("audit.validators._scan_file")
    def test_validation_succeeds_on_success_response(self, mock_scan_file):
        """If the AV service indicates that the file is clean, the file should pass validation"""
        mock_scan_file.return_value = MockHttpResponse(200, "clean!")

        try:
            validate_file_infection(self.fake_file)
        except ValidationError:
            self.fail("validate_file_infection unexpectedly raised ValidationError!")


class ExcelFileIntegrityValidatorTests(TestCase):
    def test_broken_excel_file(self):
        """XLS/X files that are not readable by openpyxl are invalid"""
        file = TemporaryUploadedFile(
            "file.xlsx", b"this is not really an excel file", 10000, "utf-8"
        )

        self.assertRaises(ValidationError, validate_excel_file_integrity, file)

    def test_valid_excel_file(self):
        """XLS/X files that are readable by openpyxl are valid"""
        wb = Workbook()
        with NamedTemporaryFile() as file:
            wb.save(file.name)
            file.seek(0)

            validate_excel_file_integrity(file)


class CorrectiveActionPlanValidatorTests(SimpleTestCase):
    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "CorrectiveActionPlanCase"
    ]

    def test_validation_is_applied(self):
        """
        Empty Corrective Action Plan should fail, simple case should pass.
        """
        template_definition_path = (
            settings.XLSX_TEMPLATE_JSON_DIR / CORRECTIVE_ACTION_TEMPLATE_DEFINITION
        )
        template = json.loads(template_definition_path.read_text(encoding="utf-8"))
        invalid = json.loads('{"CorrectiveActionPlan":{}}')
        expected_msg = str(
            [
                (
                    "B",
                    "4",
                    "Auditee UEI",
                    template["sheets"][0]["single_cells"][2]["help"],
                )
            ]
        )
        self.assertRaisesRegex(
            ValidationError, expected_msg, validate_corrective_action_plan_json, invalid
        )

        validate_corrective_action_plan_json(
            CorrectiveActionPlanValidatorTests.SIMPLE_CASE
        )


class PdfFileIntegrityValidatorTests(SimpleTestCase):
    def test_broken_pdf_file(self):
        """PDF files that are not readable by PyPDF are invalid"""
        file = TemporaryUploadedFile(
            "file.pdf", b"this is not really a pdf file", 10000, "utf-8"
        )

        self.assertRaises(ValidationError, validate_pdf_file_integrity, file)

    def test_locked_pdf_file(self):
        """PDF files that are locked / require a password are invalid"""
        with open("audit/fixtures/locked.pdf", "rb") as file:
            self.assertRaises(ValidationError, validate_pdf_file_integrity, file)

    def test_scanned_pdf_file(self):
        with open("audit/fixtures/scanned.pdf", "rb") as file:
            self.assertRaises(ValidationError, validate_pdf_file_integrity, file)

    def test_valid_pdf_file(self):
        with open("audit/fixtures/basic.pdf", "rb") as file:
            validate_pdf_file_integrity(file)


class AdditionalUeisValidatorTests(SimpleTestCase):
    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "AdditionalUeisCase"
    ]

    def test_validation_is_applied(self):
        """
        Empty Additional UEIs should fail, simple case should pass.
        """
        template_definition_path = (
            settings.XLSX_TEMPLATE_JSON_DIR / ADDITIONAL_UEIS_TEMPLATE_DEFINITION
        )
        template = json.loads(template_definition_path.read_text(encoding="utf-8"))
        invalid = json.loads('{"AdditionalUEIs":{}}')
        expected_msg = str(
            [
                (
                    "B",
                    "4",
                    "Auditee UEI",
                    template["sheets"][0]["single_cells"][2]["help"],
                )
            ]
        )
        self.assertRaisesRegex(
            ValidationError, expected_msg, validate_additional_ueis_json, invalid
        )

        validate_additional_ueis_json(AdditionalUeisValidatorTests.SIMPLE_CASE)


class NotesToSefaValidatorTests(SimpleTestCase):
    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "NotesToSefaCase"
    ]

    def test_validation_is_applied(self):
        """
        Empty Notes to SEFA should fail, simple case should pass.
        """
        template_definition_path = (
            settings.XLSX_TEMPLATE_JSON_DIR / NOTES_TO_SEFA_TEMPLATE_DEFINITION
        )
        template = json.loads(template_definition_path.read_text(encoding="utf-8"))
        invalid = json.loads('{"NotesToSefa":{}}')
        expected_msg = str(
            [
                (
                    "B",
                    "4",
                    "Auditee UEI",
                    template["sheets"][0]["single_cells"][2]["help"],
                )
            ]
        )
        self.assertRaisesRegex(
            ValidationError, expected_msg, validate_notes_to_sefa_json, invalid
        )

        validate_notes_to_sefa_json(NotesToSefaValidatorTests.SIMPLE_CASE)


class SecondaryAuditorsValidatorTests(SimpleTestCase):
    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "SecondaryAuditorsCase"
    ]

    def test_validation_is_applied(self):
        """
        Empty secondary auditors should fail, simple case should pass.
        """
        template_definition_path = (
            settings.XLSX_TEMPLATE_JSON_DIR / SECONDARY_AUDITORS_TEMPLATE_DEFINITION
        )
        template = json.loads(template_definition_path.read_text(encoding="utf-8"))
        invalid = json.loads('{"SecondaryAuditors":{}}')
        expected_msg = str(
            [
                (
                    "B",
                    "4",
                    "Auditee UEI",
                    template["sheets"][0]["single_cells"][2]["help"],
                )
            ]
        )
        self.assertRaisesRegex(
            ValidationError, expected_msg, validate_secondary_auditors_json, invalid
        )

        validate_secondary_auditors_json(SecondaryAuditorsValidatorTests.SIMPLE_CASE)
