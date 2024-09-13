from ..common.util import build_cell_error_tuple, get_message
from ..intermediate_representation import get_range_by_name, get_range_values_by_name


def check_finding_uniqueness(ir, is_gsa_migration=False):
    """
    Check the uniqueness of finding associated with the same finding reference number.
    """

    errors = []
    findings_by_reference = {}

    if is_gsa_migration:
        return errors

    modified_opinion = get_range_values_by_name(ir, "modified_opinion")
    other_matters = get_range_values_by_name(ir, "other_matters")
    material_weakness = get_range_values_by_name(ir, "material_weakness")
    significant_deficiency = get_range_values_by_name(ir, "significant_deficiency")
    other_findings = get_range_values_by_name(ir, "other_findings")
    finding_references = get_range_values_by_name(ir, "reference_number")
    compliance_requirements = get_range_values_by_name(ir, "compliance_requirement")
    questioned_costs = get_range_values_by_name(ir, "questioned_costs")
    repeat_prior_reference = get_range_values_by_name(ir, "repeat_prior_reference")
    prior_references = get_range_values_by_name(ir, "prior_references")

    # Iterate through the data rows
    for ndx, (fr, cr, mo, om, mw, sd, of, qc, rr, pr) in enumerate(
        zip(
            finding_references,
            compliance_requirements,
            modified_opinion,
            other_matters,
            material_weakness,
            significant_deficiency,
            other_findings,
            questioned_costs,
            repeat_prior_reference,
            prior_references,
        )
    ):

        finding_set = (fr, cr, mo, om, mw, sd, of, qc, rr, pr)

        if fr in findings_by_reference:
            if findings_by_reference[fr]["values"] != finding_set:
                previous_row = findings_by_reference[fr]["row"]
                current_row = ndx
                errors.append(
                    build_cell_error_tuple(
                        ir,
                        get_range_by_name(ir, "reference_number"),
                        ndx,
                        get_message("check_finding_uniqueness").format(
                            previous_row,
                            fr,
                            f"{findings_by_reference[fr]['values']}",
                            current_row,
                            f"{finding_set}",
                        ),
                    )
                )
        else:
            findings_by_reference[fr] = {"values": finding_set, "row": ndx}

    return errors
