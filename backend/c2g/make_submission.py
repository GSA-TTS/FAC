import pprint
import sys
import traceback
from django.contrib.auth import get_user_model

from .etl.sac_creation import create_sac
from .etl.federal_awards import federal_awards_to_json
from .etl.findings import findings_to_json
from .models import ELECAUDITHEADER
from audit.models import SingleAuditChecklist

User = get_user_model()


def load_historic_data(audit_year, dbkey):
    result = {"success": [], "errors": []}
    gen = ELECAUDITHEADER.objects.get(AUDITYEAR=audit_year, DBKEY=dbkey)
    user = create_or_get_user(result, gen)
    make_one_submission(result, gen, user)

    return result


sections = {
    # FORM_SECTIONS.ADDITIONAL_EINS: generate_additional_eins,
    # FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    # FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    # FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: generate_corrective_action_plan,
    "federal_awards": federal_awards_to_json,
    # FORM_SECTIONS.FINDINGS_TEXT: generate_findings_text,
    "findings": findings_to_json,
    # FORM_SECTIONS.NOTES_TO_SEFA: generate_notes_to_sefa,
    # FORM_SECTIONS.SECONDARY_AUDITORS: generate_secondary_auditors,
}


def step_through_certifications(sac: SingleAuditChecklist):
    sac.transition_to_ready_for_certification()
    sac.transition_to_auditor_certified()
    sac.transition_to_auditee_certified()
    sac.transition_to_submitted()
    sac.transition_to_disseminated()


def make_one_submission(result, gen, user):
    try:
        sac: SingleAuditChecklist = create_sac(user, gen)
        for _, fun in sections.items():
            fun(sac, dbkey=gen.DBKEY, audit_year=gen.AUDITYEAR)
        step_through_certifications(sac)

        errors = sac.validate_cross()
        if errors.get("errors"):
            pprint(errors.get("errors", "No errors found in cross validation"))

        sac.save()

        result["success"].append(f"{sac.report_id} created")
    except Exception as exc:
        tb = traceback.extract_tb(sys.exc_info()[2])
        for frame in tb:
            print(f"{frame.filename}:{frame.lineno} {frame.name}: {frame.line}")
        result["errors"].append(f"{exc}")


def create_or_get_user(result, gen):
    user_email = gen.AUDITEEEMAIL
    user_name = gen.AUDITEECONTACT.split()[0] + "_generated"
    if not user_email or len(user_email) == 0:
        user_email = "loader_generated_email@history_data.org"
        user_name = "loader_generatoed_name"
    users = User.objects.filter(email=user_email)
    if len(users) == 1:
        return users.first()
    users = User.objects.filter(username=user_name)
    if len(users) == 1:
        return users.first()

    print("Creating user", user_email, user_name)
    user = User(username=user_name, email=user_email)
    user.save()
    result["success"] = [
        f"User with email {user_email} created",
    ]
    return user
