from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from .util import get_message, build_cell_error_tuple

# Modified Opinion
# Other Matters
# Material Weakness
# Significant Deficiency
# Other Findings


# DESCRIPTION
# There are five Y/N fields in the audit findings workbook.
# Only certain combinations of Y/N are allowed.
# This makes sure that the right combos are present.
# WHY
# It's in the UG.
def findings_grid_validation(ir):
    # A copy of allowed_combos is in dissemination/workbooklib/findings.py
    # Values copied directly out of the UG
    allowed_combos = [
        "YNNNN",
        "YNYNN",
        "YNNYN",
        "NYNNN",
        "NYYNN",
        "NYNYN",
        "NNYNN",
        "NNNYN",
        "NNNNY",
    ]

    modified_opinion = get_range_values_by_name(ir, "modified_opinion")
    other_matters = get_range_values_by_name(ir, "other_matters")
    material_weakness = get_range_values_by_name(ir, "material_weakness")
    significant_deficiency = get_range_values_by_name(ir, "significant_deficiency")
    other_findings = get_range_values_by_name(ir, "other_findings")
    errors = []

    # These variables are the Y/N values from the columns above.
    for ndx, (mo, om, mw, sd, of) in enumerate(
        zip(
            modified_opinion,
            other_matters,
            material_weakness,
            significant_deficiency,
            other_findings,
        )
    ):
        # Build a grid and convert it to a string from the
        # individual y/n values.
        user_grid_ls = [mo, om, mw, sd, of]
        user_grid = "".join(user_grid_ls)
        # Check if the resulting string is in the allowed combinations.
        if user_grid not in allowed_combos:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "modified_opinion"),
                    ndx,
                    # Nicely format a message indicating that is not an allowed combination.
                    get_message("check_findings_grid_validation").format(
                        ", ".join(user_grid_ls)
                    ),
                )
            )

    return errors
