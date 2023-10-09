from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

# Modified Opinion
# Other Matters
# Material Weakness
# Significant Deficiency
# Other Findings

def findings_grid_validation(ir):
    # Values copied directly out of the UG
    allowed_raw = [
        "1YNNNN",
        "2YNYNN",
        "3YNNYN",
        "4NYNNN",
        "5NYYNN",
        "6NYNYN",
        "7NNYNN",
        "8NNNYN",
        "9NNNNY",
    ]
    allowed_split = list(map(lambda s: list(s), allowed_raw))
    just_allowed_y_n = list(map(lambda loyn: loyn[1:], allowed_split))
    allowed_as_str = list(map(lambda loc: "".join(loc), just_allowed_y_n))
    # This results in a list like ["YNNNN", "...", ...]

    modified_opinion = get_range_by_name(ir, "modified_opinion")
    other_matters = get_range_by_name(ir, "other_matters")
    material_weakness = get_range_by_name(ir, "material_weakness")
    significant_deficiency = get_range_by_name(ir, "significant_deficiency")
    other_findings = get_range_by_name(ir, "other_findings")
    errors = []
    for ndx, (mo, om, mw, sd, of) in enumerate(
        zip(
            modified_opinion["values"],
            other_matters["values"],
            material_weakness["values"],
            significant_deficiency["values"],
            other_findings["values"],
        )
    ):
        user_grid_ls = [mo, om, mw, sd, of]
        user_grid = "".join(user_grid_ls)
        if user_grid not in allowed_as_str:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    modified_opinion,
                    ndx,
                    get_message("check_findings_grid_validation").format(
                        ", ".join(user_grid_ls)
                    ),
                )
            )

    return errors
