import json
from pathlib import Path
from django.test import TestCase
from census2019.models import Cfda19

from model_bakery import baker

from .models import User

from audit.cog_agency import cog_over_assignment

AUDIT_JSON_FIXTURES = Path(__file__).parent / "fixtures" / "json"


class CogOverAssignmentTests(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def setUp(self):
        self.user = baker.make(User)
        self.federal_awards_for_test = self._fake_federal_awards()
        self.federal_awards_2019_for_test = self._fake_federal_awards_2019()
        self.general_2019_for_test = self._fake_general_2019()

    @staticmethod
    def _fake_federal_awards():
        return {
            "FederalAwards": {
                "auditee_uei": "ABC123DEF456",
                "federal_awards": [
                    {
                        "award_reference": "ABC123",
                        "cluster": {"cluster_name": "N/A", "cluster_total": 0},
                        "program": {
                            "is_major": "Y",
                            "program_name": "RETIRED AND SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 40_000_000,
                            "audit_report_type": "U",
                            "federal_agency_prefix": "93",
                            "federal_program_total": 45_000_000,
                            "three_digit_extension": "600",
                            "number_of_audit_findings": 0,
                            "additional_award_identification": "COVID-19",
                        },
                        "subrecipients": {"is_passed": "N"},
                        "loan_or_loan_guarantee": {
                            "is_guaranteed": "N",
                            "loan_balance_at_audit_period_end": 0,
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
                        "cluster": {"cluster_name": "N/A", "cluster_total": 0},
                        "program": {
                            "is_major": "Y",
                            "program_name": "SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 11_000_000,
                            "audit_report_type": "U",
                            "federal_agency_prefix": "10",
                            "federal_program_total": 12_000_000,
                            "three_digit_extension": "600",
                            "number_of_audit_findings": 0,
                            "additional_award_identification": "COVID-19",
                        },
                        "subrecipients": {"is_passed": "N"},
                        "loan_or_loan_guarantee": {
                            "is_guaranteed": "N",
                            "loan_balance_at_audit_period_end": 0,
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

    # 'audityear': ,
    #                     'dbkey': ,
    #                     "awardidentification": ,
    #                     "rd": ,
    #                     "federalprogramname": ,
    #                     "clustername" : ,
    #                     "stateclustername" : ,
    #                     "programtotal" : ,
    #                     "clustertotal" : ,
    #                     "direct" : ,
    #                     "passthroughaward" : ,
    #                     "passthroughamount" : ,
    #                     "majorprogram" : ,
    #                     "typereport_mp" : ,
    #                     "typerequirement" : ,
    #                     "qcost2" : ,
    #                     "findings" : ,
    #                     "findingrefnums" : ,
    #                     "arra" : ,
    #                     "loans" : ,
    #                     "loanbalance" : ,
    #                     "findingscount" : ,
    #                     "elecauditsid" : ,
    #                     "otherclustername" : ,
    #                     "cfdaprogramname" : ,

    @staticmethod
    def _fake_general_2019():
        return {
            "General": {
                "ein": "731084819",
                "totfedexpend": 51_000_000,
            }
        }

    def test_cog_over_assignment(self):
        # filename = "census2019_cfda19.json"
        # info = json.loads(Path(AUDIT_JSON_FIXTURES / filename).read_text(encoding="utf-8"))
        # # info = json.loads(AUDIT_JSON_FIXTURES / filename)
        # cfda19 = baker.make(Cfda19, info)

        # fixtures = [AUDIT_JSON_FIXTURES / filename]
        # print(fixtures)
        try:
            cog_agency, over_agency = cog_over_assignment(
                self.federal_awards_for_test,
                "731084819",
                self.federal_awards_2019_for_test,
                self.general_2019_for_test,
            )
        except Exception as err:
            msg = f"cog_over_assignment failed!, got {type(err)}"
            self.fail(msg)
