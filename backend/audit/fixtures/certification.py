from faker import Faker


def fake_auditor_certification():
    """Create fake auditor confirmation form data."""
    fake = Faker()
    data_step_1 = {
        "is_OMB_limited": True,
        "is_auditee_responsible": True,
        "has_used_auditors_report": True,
        "has_no_auditee_procedures": True,
        "is_FAC_releasable": True,
    }
    data_step_2 = {
        "auditor_name": fake.name(),
        "auditor_title": fake.job(),
        "auditor_certification_date_signed": fake.date(),
    }

    return data_step_1, data_step_2


def fake_auditee_certification():
    """Create fake auditee confirmation form data."""
    fake = Faker()
    data_step_1 = {
        "has_no_PII": True,
        "has_no_BII": True,
        "meets_2CFR_specifications": True,
        "is_2CFR_compliant": True,
        "is_complete_and_accurate": True,
        "has_engaged_auditor": True,
        "is_issued_and_signed": True,
        "is_FAC_releasable": True,
    }
    data_step_2 = {
        "auditee_name": fake.name(),
        "auditee_title": fake.job(),
        "auditee_certification_date_signed": fake.date(),
    }

    return data_step_1, data_step_2
