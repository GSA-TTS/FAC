import json

from audit.models import SingleAuditChecklist
from c2g.models import (
    ELECFINDINGSTEXT as FindingsText,
)

from .section import Section

import logging

logger = logging.getLogger(__name__)


class FindingUniformGuidance(Section):
    def __init__(self, finding_text: FindingsText, seq):
        super().__init__()

        self.dict_instance["reference_number"] = finding_text.FINDINGREFNUMS
        self.dict_instance["text_of_finding"] = finding_text.TEXT
        self.dict_instance["contains_chart_or_table"] = finding_text.CHARTSTABLES


def findings_text_to_json(sac: SingleAuditChecklist, dbkey, audit_year):
    json_str: str = (
        '{"FindingsUniformGuidance" : {"findings_uniform_guidance_entries":['
    )
    finding_texts = FindingsText.objects.filter(DBKEY=dbkey, AUDITYEAR=audit_year)
    finding_text: FindingsText
    for i in range(len(finding_texts)):
        finding_text = finding_texts[i]
        finding_text_obj = FindingUniformGuidance(finding_text, i)
        if i > 0:
            json_str += ","
        json_str += json.dumps(finding_text_obj.get_dict())
    json_str += "]}}"
    json_obj = json.loads(json_str)
    sac.federal_awards = json_obj
