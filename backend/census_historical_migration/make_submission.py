from django.contrib.auth import get_user_model
from .workbooklib.end_to_end_core import make_one_submission

from .models import ELECAUDITHEADER

User = get_user_model()


def load_historic_data(audit_year, dbkey):
    result = {"success": [], "errors": []}
    gen = ELECAUDITHEADER.objects.get(AUDITYEAR=audit_year, DBKEY=dbkey)
    user = create_or_get_user(result, gen)
    make_one_submission(result, gen, user)

    return result


def create_or_get_user(result, gen):
    user_email = gen.AUDITEEEMAIL
    user_name = gen.AUDITEECONTACT.split()[0] + "_generated"
    if not user_email or len(user_email) == 0:
        user_email = "loader_generated_email@history_data.org"
        user_name = "loader_generated_name"
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
