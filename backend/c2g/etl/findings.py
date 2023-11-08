import json

from audit.models import SingleAuditChecklist
from c2g.models import (
    ELECAUDITFINDINGS as Findings,
)
from .section import Section

import logging

logger = logging.getLogger(__name__)


class FindingUniformGuidance(Section):
    def __init__(self, finding: Findings, seq):
        super().__init__()

        finding.LOANBALANCE = self.normalize_number(finding.LOANBALANCE)
        finding.AMOUNT = self.normalize_number(finding.AMOUNT)
        finding.FINDINGSCOUNT = self.normalize_number(finding.FINDINGSCOUNT)
        finding.AWARDIDENTIFICATION = self.normalize_addl_award_id(
            finding.AWARDIDENTIFICATION, finding.CFDA, finding.DBKEY
        )
        finding.STATECLUSTERNAME = (
            finding.STATECLUSTERNAME if "STATE CLUSTER" == finding.CLUSTERNAME else ""
        )

        self.dict_instance["compliance_requirement"] = finding.TYPEREQUIREMENT
        self.dict_instance["reference_number"] = finding.FINDINGREFNUMS
        self.dict_instance["modified_opinion"] = finding.MODIFIEDOPINION
        self.dict_instance["other_matters"] = finding.OTHERNONCOMPLIANCE
        self.dict_instance["material_weakness"] = finding.MATERIALWEAKNESS
        self.dict_instance["significant_deficiency"] = finding.SIGNIFICANTDEFICIENCY
        self.dict_instance["other_findings"] = finding.OTHERFINDINGS
        self.dict_instance["questioned_costs"] = finding.QCOSTS
        self.dict_instance["repeat_prior_reference"] = finding.REPEATFINDING
        self.dict_instance["prior_references"] = finding.PRIORFINDINGREFNUMS


def findings_to_json(sac: SingleAuditChecklist, dbkey, audit_year):
    json_str: str = (
        '{"FindingsUniformGuidance" : {"findings_uniform_guidance_entries":['
    )
    findings = Findings.objects.filter(DBKEY=dbkey, AUDITYEAR=audit_year)
    finding: Findings
    for i in range(len(findings)):
        finding = findings[i]
        finding_obj = FindingUniformGuidance(finding, i)
        if i > 0:
            json_str += ","
        json_str += json.dumps(finding_obj.get_dict())
    json_str += "]}}"
    json_obj = json.loads(json_str)
    sac.federal_awards = json_obj
