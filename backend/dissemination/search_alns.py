def search_alns(results, params):
    return results

def foo():
    ##############################
    # Now that we have reduced the result set to something
    # manageable, we can apply ALN operations.
    if alns:
        # q_alns = Q(report_id_id__in=results.values_list('report_id', flat=True))
        q_alns = Q()
        # Split out the agency numbers
        split_alns = _split_alns(alns)
        query_set = _get_aln_match_query(split_alns)
        # If we did a search on ALNs, and got nothing (because it does not exist),
        # we need to bail out from the entire search early with no results.
        if not query_set:
            logger.info("No query_set; returning []")
            return []
        else:
            # If results came back from our ALN query, add it to the Q() and continue.
            q_alns.add(query_set, Q.AND)
        # We want the distinct report_ids for these ALNs
        distinct_alns = FederalAward.objects.values(
            'report_id_id'
        ).annotate(
            report_id_id_count = Count('report_id_id')
        ).filter(report_id_id_count=1)

        # And, we want to reduce the results from above by the report_ids
        # that are in this set.
        results = results.filter(report_id__in=[ 
            rec['report_id_id'] 
            for rec 
            in distinct_alns
            ])

    t1 = time.time()
    logger.info(f"SEARCH GENERAL T1: {t1-t0}")


    # if order_by == ORDER_BY.findings_my_aln:
    #     results = sorted(
    #         results,
    #         key=lambda obj: obj.finding_my_aln,
    #         reverse=bool(order_direction == DIRECTION.descending),
    #     )
    # elif order_by == ORDER_BY.findings_all_aln:
    #     results = sorted(
    #         results,
    #         key=lambda obj: obj.finding_all_aln,
    #         reverse=bool(order_direction == DIRECTION.descending),
    #     )
