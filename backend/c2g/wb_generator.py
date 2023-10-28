from django.contrib.auth import get_user_model

from .workbooklib import workbook_creation
from .models import ELECAUDITHEADER

User = get_user_model()


def generate_workbooks(audit_year, dbkey):
    gen = ELECAUDITHEADER.objects.get(AUDITYEAR=audit_year, DBKEY=dbkey)
    user_email = gen.AUDITEEEMAIL
    user = create_or_get_user(user_email)
    result = {}
    result["success"] = [
        f"{user.email} created or found",
    ]
    sac = workbook_creation.setup_sac(user, gen)
    result["success"].append(f"{sac.report_id} created")
    return result


def create_or_get_user(email):
    user, _ = User.objects.get_or_create(email=email)
    return user
