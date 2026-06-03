from django.db.models import Q

from audit.models import SingleAuditChecklist


def fetch_disseminated_sacs_for_ay(AY, noisy=False):
    """
    Return all disseminated SACs for the given audit year.

    Equivalence or distance-based clustering will decide which submissions actually form resubmission chains.
    We just need the full population of disseminated submissions for the year.
    """
    sacs = SingleAuditChecklist.objects.filter(
        Q(general_information__auditee_fiscal_period_end__startswith=AY)
        & Q(submission_status="disseminated")
    )

    # Sort in Python rather than the ORM - transition_date is a JSON array
    # and ordering on array elements is awkward in the ORM.
    sacs = sorted(
        sacs, key=lambda r: r.transition_date[0].strftime("%Y-%m-%d %H:%M:%S")
    )

    if noisy:
        print("\n-=-=-=-=-=-=-=-=-=-")
        print(f"AY{AY}: {len(sacs)} disseminated submissions fetched")

    return sacs


def fetch_disseminated_sacs_for_report_ids(report_ids, noisy=False):
    """
    Return all disseminated SACs for the given report IDs.
    """
    sacs = SingleAuditChecklist.objects.filter(
        Q(report_id__in=report_ids)
        & Q(submission_status="disseminated")
    )

    # Sort in Python rather than the ORM - transition_date is a JSON array
    # and ordering on array elements is awkward in the ORM.
    sacs = sorted(
        sacs, key=lambda r: r.transition_date[0].strftime("%Y-%m-%d %H:%M:%S")
    )

    if noisy:
        print("\n-=-=-=-=-=-=-=-=-=-")
        print(f"{len(sacs)} disseminated submissions fetched")

    return sacs
