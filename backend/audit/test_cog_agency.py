from django.test import TestCase
from model_bakery import baker
from .models import User
from audit.cog_agency import cog_over_assignment

# AUDIT_JSON_FIXTURES = Path(__file__).parent / "fixtures" / "json"

# Note:  Fake data is generated for Federal Awards and General.
#        Using only the data fields that apply to cog / over assignment.


class CogOverAssignmentTests(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def setUp(self):
        self.user = baker.make(User)
        self.federal_awards_for_test = self._fake_federal_awards()
        self.federal_awards_2019_for_test = self._fake_federal_awards_2019()
        self.general_2019_for_test = self._fake_general_2019()
        self.federal_awards_for_test2 = self._fake_federal_awards2()
        self.federal_awards_2019_for_test3 = self._fake_federal_awards_2019_3()
        self.federal_awards_for_test4 = self._fake_federal_awards4()

    @staticmethod
    def _fake_federal_awards():
        return {
            "FederalAwards": {
                "auditee_uei": "ABC123DEF456",
                "federal_awards": [
                    {
                        "award_reference": "ABC123",
                        "program": {
                            "program_name": "RETIRED AND SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 40_000_000,
                            "federal_agency_prefix": "10",
                            "federal_program_total": 45_000_000,
                            "three_digit_extension": "600",
                        },
                        "direct_or_indirect_award": {
                            "is_direct": "N",
                            "entities": [
                                {
                                    "passthrough_name": "Bob's Granting House",
                                    "passthrough_identifying_number": "12345",
                                }
                            ],
                        },
                    },
                    {
                        "award_reference": "ABC124",
                        "program": {
                            "program_name": "SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 11_000_000,
                            "federal_agency_prefix": "10",
                            "federal_program_total": 12_000_000,
                            "three_digit_extension": "600",
                        },
                        "direct_or_indirect_award": {"is_direct": "Y"},
                    },
                ],
                "total_amount_expended": 51_000_000,
            }
        }

    @staticmethod
    def _fake_federal_awards_2019():
        return {
            "FederalAwards": {
                "ein": "731084819",
                "federal_awards": [
                    {
                        "amount": 20_000_000,
                        "direct": "Y",
                        "cfda": 93123,  # Federal agency prefix + 3 digit extension
                    },
                    {
                        "amount": 31_000_000,
                        "direct": "Y",
                        "cfda": 93123,  # Federal agency prefix + 3 digit extension
                    },
                ],
            }
        }

    @staticmethod
    def _fake_federal_awards_2019_3():
        return {
            "FederalAwards": {
                "ein": "731084819",
                "federal_awards": [
                    {
                        "amount": 10_000_000,
                        "direct": "Y",
                        "cfda": 15123,  # Federal agency prefix + 3 digit extension
                    },
                    {
                        "amount": 1_000_000,
                        "direct": "Y",
                        "cfda": 15123,  # Federal agency prefix + 3 digit extension
                    },
                ],
            }
        }

    @staticmethod
    def _fake_general_2019():
        return {
            "General": {
                "ein": "731084819",
                "totfedexpend": 51_000_000,
            }
        }

    @staticmethod
    def _fake_federal_awards2():
        return {
            "FederalAwards": {
                "auditee_uei": "ABC123DEF456",
                "federal_awards": [
                    {
                        "award_reference": "ABC125",
                        "program": {
                            "program_name": "SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 11_000_000,
                            "federal_agency_prefix": "10",
                            "federal_program_total": 12_000_000,
                            "three_digit_extension": "600",
                        },
                        "direct_or_indirect_award": {"is_direct": "Y"},
                    },
                ],
                "total_amount_expended": 11_000_000,
            }
        }

    @staticmethod
    def _fake_federal_awards4():
        return {
            "FederalAwards": {
                "auditee_uei": "ABC123DEF456",
                "federal_awards": [
                    {
                        "award_reference": "ABC125",
                        "program": {
                            "program_name": "SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 15_000_000,
                            "federal_agency_prefix": "20",
                            "federal_program_total": 12_000_000,
                            "three_digit_extension": "600",
                        },
                        "direct_or_indirect_award": {"is_direct": "Y"},
                    },
                ],
                "total_amount_expended": 51_000_000,
            }
        }

    def test_cog_over_for_gt_threshold_cog_2019(self):
        # info = json.loads(Path(AUDIT_JSON_FIXTURES / filename).read_text(encoding="utf-8"))
        # # info = json.loads(AUDIT_JSON_FIXTURES / filename)
        # cfda19 = baker.make(Cfda19, info)

        # fixtures = [AUDIT_JSON_FIXTURES / filename]
        # print(fixtures)

        # Test Case #1 - Cog agency from 2019 with Direct Award > 0.25 * total expended
        # print(
        #     "\n\nTest Case 1 - Cog agency from 2019 with Direct Award > 0.25 * total expended"
        # )
        cog_agency, over_agency = cog_over_assignment(
            self.federal_awards_for_test,
            "731084819",
            self.federal_awards_2019_for_test,
            self.general_2019_for_test,
        )
        self.assertEqual(over_agency, 0)

    def test_cog_over_for_gt_threshold_oversight(self):
        # Test Case #2 - Oversight agency 2023 with Direct Award > 0.25 * total expended
        # print(
        #     "\n\n Test Case 2 - Oversight agency 2023 with Direct Award > 0.25 * total expended"
        # )
        cog_agency, over_agency = cog_over_assignment(
            self.federal_awards_for_test2,
            "731084818",
            self.federal_awards_2019_for_test,
            self.general_2019_for_test,
        )
        self.assertEqual(cog_agency, 0)

    def test_cog_over_for_lt_threshold_cog_2019(self):
        # Test Case #3 - Cog agency from 2019 with Direct Award < 0.25 * total expended
        # print(
        #     "\n\nTest Case 3 - Cog agency from 2019 with Direct Award < 0.25 * total expended"
        # )
        cog_agency, over_agency = cog_over_assignment(
            self.federal_awards_for_test,
            "731084819",
            self.federal_awards_2019_for_test3,
            self.general_2019_for_test,
        )
        self.assertEqual(over_agency, 0)

    def test_cog_over_lt_threshold_oversight(self):
        # Test Case #4 - Oversight agency 2023 with Direct Award < 0.25 * total expended
        # print(
        #     "\n\n Test Case 4 - Oversight agency 2023 with Direct Award < 0.25 * total expended"
        # )
        cog_agency, over_agency = cog_over_assignment(
            self.federal_awards_for_test4,
            "731084818",
            self.federal_awards_2019_for_test,
            self.general_2019_for_test,
        )
        self.assertEqual(over_agency, 0)
