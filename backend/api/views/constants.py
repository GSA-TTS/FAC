# Data from step 1, required for step 2 and 3
AUDITEE_INFO_DATA = [
    "auditee_fiscal_period_start",
    "auditee_fiscal_period_end",
    "auditee_uei",
]

# Data from step 2, required for step 3
ELIGIBILITY_DATA = [
    "user_provided_organization_type",
    "met_spending_threshold",
    "is_usa_based",
]

# Step 3 requirements. Data from step 1 plus data from step 2.
ACCESS_SUBMISSION_DATA_REQUIRED = (
    AUDITEE_INFO_DATA + ELIGIBILITY_DATA
)
