from config.settings import DOLLAR_THRESHOLDS
from .errors import err_total_amount_expended

from datetime import date
from decimal import Decimal, InvalidOperation


def _to_decimal(value) -> Decimal:
    """
    Coerce numeric-ish inputs to Decimal.
    Handles ints, floats, Decimals, and strings like "1,234" or "$1,234.00".
    Treats None/blank/unparseable as 0.
    """
    if value is None:
        return Decimal("0")

    if isinstance(value, Decimal):
        return value

    if isinstance(value, (int, float)):
        # Convert through str to avoid float rounding surprises
        return Decimal(str(value))

    if isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace("$", "")
        if cleaned == "":
            return Decimal("0")
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return Decimal("0")

    # Unknown type → treat as 0 (or raise, but 0 is safest for test-data gen)
    return Decimal("0")


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

    abs_total = Decimal("0")
    for award in federal_awards["federal_awards"]:
        amount = award["program"]["amount_expended"]
        abs_total += abs(_to_decimal(amount))

        # Entities with an outstanding balance over the threshold are also required to submit.
        # In the name of keeping it simple, we simply add any loan balance amounts to the total.
        is_loan_or_loan_guarantee = (
            award["loan_or_loan_guarantee"]["is_guaranteed"] == "Y"
        )
        if is_loan_or_loan_guarantee:
            loan_bal = award["loan_or_loan_guarantee"][
                "loan_balance_at_audit_period_end"
            ]
            abs_total += abs(_to_decimal(loan_bal))

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
