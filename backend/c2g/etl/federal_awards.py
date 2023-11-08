import json
from audit.models import SingleAuditChecklist
from .section import Section


from c2g.models import (
    ELECAUDITS as Cfda,
)


import logging

logger = logging.getLogger(__name__)


class FederalAward(Section):
    def __init__(self, cfda: Cfda, seq):
        super().__init__()
        cfda.LOANBALANCE = self.normalize_number(cfda.LOANBALANCE)
        cfda.AMOUNT = self.normalize_number(cfda.AMOUNT)
        cfda.FINDINGSCOUNT = self.normalize_number(cfda.FINDINGSCOUNT)
        cfda.AWARDIDENTIFICATION = self.normalize_addl_award_id(
            cfda.AWARDIDENTIFICATION, cfda.CFDA, cfda.DBKEY
        )
        cfda.STATECLUSTERNAME = (
            cfda.STATECLUSTERNAME if "STATE CLUSTER" == cfda.CLUSTERNAME else ""
        )

        self.dict_instance["program_name"] = cfda.FEDERALPROGRAMNAME
        self.dict_instance["state_cluster_name"] = cfda.STATECLUSTERNAME
        self.dict_instance["federal_program_total"] = cfda.PROGRAMTOTAL
        self.dict_instance["cluster_total"] = cfda.CLUSTERTOTAL
        self.dict_instance["is_guaranteed"] = cfda.LOANS
        self.dict_instance["loan_balance_at_audit_period_end"] = cfda.LOANBALANCE
        self.dict_instance["is_direct"] = cfda.DIRECT
        self.dict_instance["is_passed"] = cfda.PASSTHROUGHAWARD
        self.dict_instance["subrecipient_amount"] = cfda.PASSTHROUGHAMOUNT
        self.dict_instance["is_major"] = cfda.MAJORPROGRAM
        self.dict_instance["amount_expended"] = cfda.AMOUNT
        self.dict_instance["program"] = {
            "number_of_audit_findings": int(cfda.FINDINGSCOUNT)
        }

        self.dict_instance["award_reference"] = f"AWARD-{seq+1:04}"

    def normalize_number(self, number: str):
        if number in ["N/A", "", None]:
            return "0"
        if self.is_positive(number):
            return number
        return "0"

    def is_positive(self, s):
        try:
            value = int(s)
            return value >= 0
        except ValueError:
            return False

    def normalize_addl_award_id(self, award_id: str, cfda_id: str, dbkey):
        if "u" in cfda_id.lower() or "rd" in cfda_id.lower():
            if not award_id or len(award_id) == 0:
                return f"ADDITIONAL AWARD INFO - DBKEY {dbkey}"
            return award_id
        return ""


def federal_awards_to_json(sac: SingleAuditChecklist, dbkey, audit_year):
    json_str: str = '{"FederalAwards" : {"federal_awards":['
    cfdas = Cfda.objects.filter(DBKEY=dbkey, AUDITYEAR=audit_year)
    cfda: Cfda
    for i in range(len(cfdas)):
        cfda = cfdas[i]
        award = FederalAward(cfda, i)
        if i > 0:
            json_str += ","
        json_str += json.dumps(award.get_dict())
    json_str += "]}}"
    json_obj = json.loads(json_str)
    sac.federal_awards = json_obj
