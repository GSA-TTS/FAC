import sys
import traceback
from django.contrib.auth import get_user_model

from .workbooklib.end_to_end_workbook import generate_workbooks
from .models import ELECAUDITHEADER
from audit.models import SingleAuditChecklist

User = get_user_model()


def load_historic_data(audit_year, dbkey):
    result = {"success": [], "errors": []}
    gen = ELECAUDITHEADER.objects.get(AUDITYEAR=audit_year, DBKEY=dbkey)
    user = create_or_get_user(result, gen)
    try:
        sac: SingleAuditChecklist = generate_workbooks(user, gen)
        result["success"].append(f"{sac.report_id} created")
    except Exception as exc:
        tb = traceback.extract_tb(sys.exc_info()[2])
        for frame in tb:
            print(f"{frame.filename}:{frame.lineno} {frame.name}: {frame.line}")
        result["errors"].append(f"{exc}")

    return result


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
