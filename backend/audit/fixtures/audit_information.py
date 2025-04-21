import json
from faker import Faker


def fake_audit_information():
    fake = Faker()

    return {
        "dollar_threshold": 10345.45,
        "gaap_results": json.dumps([fake.word()]),
        "is_going_concern_included": "Y" if fake.boolean() else "N",
        "is_internal_control_deficiency_disclosed": "Y" if fake.boolean() else "N",
        "is_internal_control_material_weakness_disclosed": (
            "Y" if fake.boolean() else "N"
        ),
        "is_material_noncompliance_disclosed": "Y" if fake.boolean() else "N",
        "is_aicpa_audit_guide_included": "Y" if fake.boolean() else "N",
        "is_low_risk_auditee": "Y" if fake.boolean() else "N",
        "agencies": json.dumps([fake.word()]),
    }
