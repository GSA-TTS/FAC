from .models import ELECAUDITHEADER as Gen
from .workbooklib.end_to_end_core import run_end_to_end

from django.contrib.auth import get_user_model

User = get_user_model()


def load_historic_data_for_year(audit_year, start_dbkey, end_dbkey):
    """Iterates over and processes submissions for the given audit year"""
    result_log = {}
    total_count = error_count = 0
    user = create_or_get_user()

    if start_dbkey == end_dbkey:
        # Find a single submission
        submissions_for_year = Gen.objects.filter(
            AUDITYEAR=audit_year, DBKEY=str(start_dbkey)
        )
    else:
        submissions_for_year = Gen.objects.filter(AUDITYEAR=audit_year)

    print(f"Migrating dbkeys in range {start_dbkey} to {end_dbkey}")

    for submission in submissions_for_year:
        dbkey = submission.DBKEY
        # Only migrate if the dbkey is within range
        if int(dbkey) < start_dbkey or int(dbkey) > end_dbkey:
            continue

        result = {"success": [], "errors": []}

        try:
            # Migrate a single submission
            run_end_to_end(user, dbkey, audit_year, result)
        except Exception as exc:
            result["errors"].append(f"{exc}")

        result_log[(audit_year, dbkey)] = result
        total_count += 1

        if len(result["errors"]) > 0:
            error_count += 1
        if total_count % 5 == 0:
            print(f"Processed = {total_count}, Errors = {error_count}")
        if error_count > 5:
            break

    print("********* Loader Summary ***************")

    for k, v in result_log.items():
        print(k, v)
        print("-------------------")

    print(f"{error_count} errors out of {total_count}")


def create_or_get_user():
    """Returns the default migration user"""
    user_email = "fac-census-migration-auditee-official@fac.gsa.gov"
    user_name = "fac-census-migration-auditee-official"
    user = None

    users = User.objects.filter(email=user_email)
    if users:
        user = users.first()
    else:
        print("Creating user", user_email, user_name)
        user = User(username=user_name, email=user_email)
        user.save()

    return user
