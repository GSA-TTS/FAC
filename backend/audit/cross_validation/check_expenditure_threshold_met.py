from config.settings import DOLLAR_THRESHOLDS
from .errors import err_total_amount_expended

from datetime import date


def check_expenditure_threshold_met(
    sac_dict, thresholds=DOLLAR_THRESHOLDS, *_args, **_kwargs
):
    """
    Check that the total amount expended meets the minimum threshold for its fy_start_date.
    For now, we are counting reimbursements as positive values, hence using abs().
    See ticket #4198 for more info.
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

        # Entities with an outstanding balance over the threshold are also required to submit.
        # In the name of keeping it simple, we simply add any loan balance amounts to the total.
        is_loan_or_loan_guarantee = (
            award["loan_or_loan_guarantee"]["is_guaranteed"] == "Y"
        )
        if is_loan_or_loan_guarantee:
            loan_balance = award["loan_or_loan_guarantee"]["loan_balance_at_audit_period_end"]
            if isinstance(loan_balance, (int, float)):  # 20260115 - Hotfix. This is not guaranteed to be either empty or an integer.
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
