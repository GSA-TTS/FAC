from audit.models import SingleAuditChecklist
from django.db.models import Count, Q, F


def fetch_sac_resubmission_records_postgres(AY, duplication_threshold=2, noisy=False):
    # Begin with a small set.
    # Take a full year, grab the UEIs, and look for duplicated UEIs.
    base = SingleAuditChecklist.objects.filter(
        Q(general_information__auditee_fiscal_period_end__startswith=AY)
        & Q(submission_status="disseminated")
        & ~Q(general_information__auditee_uei="GSA_MIGRATION")
    )

    ueis = (
        base.values("general_information__auditee_uei")
        .annotate(uei=F("general_information__auditee_uei"))
        .annotate(uei_duplication_count=Count("report_id"))
    ).filter(uei_duplication_count__gte=duplication_threshold)

    # Now, I want the records for those UEIs
    # Order by the first date in the transition_date array.
    records = base.filter(
        general_information__auditee_uei__in=ueis.values("uei"),
    )
    # Doing it in the model is hard.
    records = sorted(
        records, key=lambda r: r.transition_date[0].strftime("%Y-%m-%d %H:%M:%S")
    )

    if noisy:
        print("\n-=-=-=-=-=-=-=-=-=-")
        print(f"{len(base)} in AY{AY}")
        print("----")
        print(f"{ueis.count()} duplicated UEIs (dupe count >= {duplication_threshold})")
        print("-----")
        print(f"{len(records)} records for the duplicated UEIs")

    return records
