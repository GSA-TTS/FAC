from config.settings import DOLLAR_THRESHOLDS
from .errors import err_total_amount_expended
from ..intakelib.common.util import is_int

from datetime import date


def check_expenditure_threshold_met(
    sac_dict, thresholds=DOLLAR_THRESHOLDS, *_args, **_kwargs
):
    """
    Check that the total amount expended meets the minimum threshold for its fy_start_date.
    For now, we are counting reimbursements as positive values, hence using abs().
    See ticket #4198 for more info.
    Now includes both federal expenditures (Column K) and loan balances (Column M).
    """
    all_sections = sac_dict["sf_sac_sections"]
    general_information = all_sections.get("general_information", {})
    federal_awards = all_sections.get("federal_awards", {})

    if not (general_information and federal_awards):
        return []

    abs_total = 0
    for award in federal_awards["federal_awards"]:
        amount = award["program"]["amount_expended"]
        abs_total += abs(amount)

        # NEW: Include loan balance (Column M)
        loan_balance = award["program"].get("loan_balance_at_audit_period_end")
        if is_int(loan_balance):
            abs_total += abs(loan_balance)

    fy_start_date = date.fromisoformat(
        general_information["auditee_fiscal_period_start"]
    )
    threshold_met = False

    for dt in thresholds:
        start = dt["start"]
        end = dt["end"]

        if not start and end:
            threshold_met = fy_start_date < end and abs_total >= dt["minimum"]
        elif start and end:
            threshold_met = start <= fy_start_date < end and abs_total >= dt["minimum"]
        elif start and not end:
            threshold_met = fy_start_date >= start and abs_total >= dt["minimum"]

        if threshold_met:
            break

    if not threshold_met:
        return [{"error": err_total_amount_expended(abs_total)}]
    else:
        return []
