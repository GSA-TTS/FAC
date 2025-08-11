from audit.models import SingleAuditChecklist
from django.db.models import Count, Q, F


def fetch_sac_resubmission_records_postgres(AY, duplication_threshold=2, noisy=False):
    # Begin with a small set.
    # Take a full year, grab the UEIs, and look for duplicated UEIs.
    base = SingleAuditChecklist.objects.filter(
        # We should only be clustering things that have no metadata.
        # The assumption is we will be using the clustering of these records
        # to then link them. Therefore, those records will get metadata, meaning
        # those records should no longer become part of automatic cluster generation.
        Q(resubmission_meta__isnull=True)
        # It can only be a "resubmission" if it is from the same audit year/fiscal period.
        # Otherwise, we must assume it is a different audit.
        & Q(general_information__auditee_fiscal_period_end__startswith=AY)
        # An audit that is in-progress cannot be linked.
        # An audit that has a "redisseminated" status should never be linked,
        # because that would imply branching (a tree). Therefore, only
        # records that are "disseminated" can represent the end of a chain.
        & Q(submission_status="disseminated")
        # We have to have a real UEI, not GSA_MIGRATION
        # FIXME: Could the start of a chain have GSA_MIGRATION, and a
        # "resubmission" have a real UEI? Meaning, it spanned systems? I think
        # this is possible. Elch. Possibly ignore this, or allow the
        # distance algorithm to consider "GSA_MIGRATION" to be distance zero
        # from any real UEI?
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
    # Doing it in the model is hard. Breaking it out into a
    # python sort.
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
