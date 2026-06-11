
# Determining the Cognizant and Oversight Agency

This document describes the algorithm used to determine agency cognizance or oversight for audits submitted to the FAC.  
**[This algorithm](https://github.com/GSA-TTS/FAC/blob/main/backend/support/cog_over.py)** is implemented in code, automatically executing for every GSA FAC submission, and is guided by the **[Code of Federal Regulation (CFR) 200.513](https://www.ecfr.gov/current/title-2/subtitle-A/chapter-II/part-200/subpart-F/subject-group-ECFRed80de82be1f4a3/section-200.513)**.

**GIVENS:**
- **federal_awards**
- **submission_status**
- **auditee_ein**
- **auditee_uei**
- **audit_year**

**RETURNS:**  
A tuple of **(cog, over)** values. If cognizant is assigned, then oversight will be None, and vice-versa.

1.  If there are no **federal_awards**
    1. Return **(None, None)** for  **(cog, over)**. This is an error condition.
    1. Validations prevent the submission of audits with no **federal_awards**

2.  Set **total_amount_expended** to the total of the **amount_expended** field in all **federal_awards**.

3.  Set **max_total_agency** and **max_da_agency** to hash tables computed by **[calc_award_amounts](https://github.com/GSA-TTS/FAC/blob/main/backend/support/cog_over.py#L78)**:
    1. **max_total_agency** is a hash table that keys the agency number to the total **amount_expended** for every **program** for the agency.
    1. **max_da_agency** is a hash table that keys the agency number to the amount expended for the awards where **is_direct** is **Y** for that agency.
    1. Those hash tables are then pruned, so that only the maximum values are kept. If there are ties (e.g. two agencies have the same, maximum-value expenditures), then both are kept.

4.  **agency** is computed using **[determine_agency](https://github.com/GSA-TTS/FAC/blob/main/backend/support/cog_over.py#L92)**. It uses **total_amount_expended** and the two hash tables computed in the previous step.
    1. For each agency and expenditure in the **max_da_agency** hash table, we ask if the total direct awards expended are greater than 25% of the **total_amount_expended**. If so, we put the agency into a **tie_breaker** hash table, keying the agency number to the **direct_awards** added to the corresponding value from **max_total_agency**.
    1. This is then pruned, so only maximum values are kept.
        - We try and return the agency who won the tiebreaker, by returning the max value from the **tie_breaker** hash table.
        - If we did not have any ties, we return the maximum from the **max_total_agency** hash table, computed in the previous step.
5.  If the **total_amount_expended** is less than or equal to the **COG_LIMIT** (which is $50M)
    1. The **agency** computed in the previous step is returned as the oversight agency. We return the tuple **(None, agency)**, meaning there is no cognizant but there is oversight. **We exit the algorithm if an oversight agency is assigned**.
6.  If no oversight agency was assigned, then we continue. The agency is now determined by the **[determine_hist_agency function](https://github.com/GSA-TTS/FAC/blob/main/backend/support/cog_over.py#L103)**, which uses the **auditee_ein**, **auditee_uei**, and **audit_year**:
    1. First, we calculate the **[base_year](https://github.com/GSA-TTS/FAC/blob/main/backend/support/cog_over.py#L64)**. For years 2019–2023, this is 2019. For years 2024–2028, this is 2024, and so on.
    1. If we are in the **FIRST_BASELINE_YEAR**, that means we have to use **[the dbkey to hash values; this is computed](https://github.com/GSA-TTS/FAC/blob/main/backend/support/cog_over.py#L130)** via hash against both the published data in the GSAFAC as well as the migration inspection records.
    1. **cog_agency** is then computed using the function **[lookup_latest_cog](https://github.com/GSA-TTS/FAC/blob/main/backend/support/cog_over.py#L154)**:
        - We look at our disseminated data for audits matching **auditee_ein** and **auditee_uei** for all audits with an audit year between **base_year** and and the **audit_year** of the audit being evaluated.
        - We reverse order, and take the **cognizant** value from the most recent submission matching. There might not be one.
    1. If we found a **cog_agency** in the previous step, we return this and return it as the historical agency. We then return **(cog_agency, None)** as a tuple. **This exits the algorithm**.
7.  If no historical agency was found in step 6, we set **cognizant_agency** to the same value as **agency** computed in step 4, and return the tuple **(cognizant, oversight)**. This may still be **(None, None)** which would be an error condition.

The nature of the algorithm is that we do not exit without a value for one of either **cog** or **over**. We expect, in all cases, that either the tuple **(cog, None)** will be returned, or **(None, over)**.

