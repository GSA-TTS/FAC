from django.db.models import Q

from audit.models import SingleAuditChecklist


def fetch_sac_disseminated_records_postgres(AY, noisy=False):
    """
    Return all disseminated records for the given audit year.

    Equivalence or distance-based clustering will decide which records actually form resubmission chains.
    We just need the full population of disseminated records for the year.
    """
    records = SingleAuditChecklist.objects.filter(
        Q(general_information__auditee_fiscal_period_end__startswith=AY)
        & Q(submission_status="disseminated")
    )

    # Sort in Python rather than the ORM - transition_date is a JSON array
    # and ordering on array elements is awkward in the ORM.
    records = sorted(
        records, key=lambda r: r.transition_date[0].strftime("%Y-%m-%d %H:%M:%S")
    )

    if noisy:
        print("\n-=-=-=-=-=-=-=-=-=-")
        print(f"AY{AY}: {len(records)} disseminated records fetched")

    return records
