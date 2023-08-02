from historic.base import NoMapping, MapLateRemove, MapRetype
from historic.retyping import to_boolean

cfac_to_gfac = {
    "audityear": NoMapping(),
    "dbkey": MapLateRemove(),
    "elecauditfindingsid": NoMapping(),
    "elecauditsid": NoMapping(),
    "findingrefnums": NoMapping(),
    "materialweakness": MapRetype("is_material_weakness", to_boolean),
    "modifiedopinion": MapRetype("is_modified_opinion", to_boolean),
    "otherfindings": MapRetype("is_other_findings", to_boolean),
    "othernoncompliance": MapRetype("is_other_matters", to_boolean),
    "priorfindingrefnums": "prior_finding_ref_numbers",
    "qcosts": MapRetype("is_questioned_costs", to_boolean),
    "repeatfinding": MapRetype("is_repeat_finding", to_boolean),
    "reportid": NoMapping(),
    "significantdeficiency": MapRetype("is_significant_deficiency", to_boolean),
    "typerequirement": "type_requirement",
    "version": NoMapping(),
}
