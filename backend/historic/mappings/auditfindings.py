import historic.Mapping
from historic.base import NoMapping, MapRetype, MapOneOf, MapLateRemove
from historic.retyping import to_int_to_str

cfac_to_gfac = {
    'audityear': MapLateRemove(),
    'dbkey': MapLateRemove(),
    'elecauditfindingsid': NoMapping(),
    'elecauditsid': NoMapping(),
    'findingrefnums': NoMapping(),
    'materialweakness': 'is_material_weakness',
    'modifiedopinion': 'is_modified_opinion',
    'otherfindings': 'is_other_findings',
    'othernoncompliance': 'is_other_matters',
    'priorfindingrefnums': 'prior_finding_ref_numbers',
    'qcosts': 'is_questioned_costs',
    'repeatfinding': 'is_repeat_finding',
    'reportid': NoMapping(),
    'significantdeficiency': 'is_significant_deficiency',
    'typerequirement': 'type_requirement',
    'version': NoMapping(),
}
