# 46. Convert dissemination_combined MV into a real table

Date: 2026-06-05

## Status

Accepted

## Areas of impact

<delete any from the below list that do not apply>

* Engineering

## Related resources

* https://github.com/GSA-TTS/FAC/issues/5664
* The "Convert dissemination_combined to a “real table” section of [Matt's farewell brain dump](https://docs.google.com/document/d/1-gx-UcwtbUEwrPrELAsK3sO8vYzR1WwDwctY0oVRqF4/edit?tab=t.0#heading=h.bl8kv7jgvig)

## Context
We have a "table" called `dissemination_combined`, which does joins across general info, federal awards, findings, and passthroughs. Specifically, it's a materialized view that's generated nightly and is used by advanced search and SF-SAC downloads. Having to generate this table so that it can be used and up to date comes with some negative side effects:
* The MV being generated once per day means that it can take up to 24 hours for submissions to show up for users in advanced search and for SF-SACs to be available for download
  * This MV generation job can sometimes fail, meaning the previous day's submissions won't appear until a later run succeeds
* We can't make the data reliably available to users as an API because of the nightly downtime, but it is useful for devs
  * Because of this, v1.1.0 is currently the only one with the combined data available, but we have to keep updating it as we create new API versions. This is cumbersome to implement and test.
* Locally testing some features, most notably advance searched, requires us to regenerate the table any time submissions are disseminated

## Decision
Due to the pain points mentioned, we want make a standard (non-MV) table for this data called `dissemination_unified`. It will populate alongside the other `dissemination_*` tables during the normal dissemination process. The existing MV version of the table will initially exist alongside the new table and will only be removed when we're confident there are no issues (performance being the primary concern).

### API
As mentioned previously, the current API has no endpoint available for public users to fetch the combined data. Moving away from a MV will let us create an endpoint that's always available. The schema/version of this API will be v1.3.0 and the endpoint will be `/unified`. Communication with users will be done as prescribed by the doc created by https://github.com/GSA-TTS/FAC/issues/5661.

### Backfilling
Existing submissions will need to be rediseminated to populate the new table. This can be done with the `delete_and_regenerate_dissemination_from_intake` command, which will ensure all dissemination tables are synchronized.

### Performance profiling
The performance of searches using the new table will need to be profiled and compared with current search. Indexes will need to be created as needed to match or improve search performance. The API should be reasonably performant, though it's data that wasn't previously made available, so there's no risk of "degraded" performance from a user's perspective. Also, insertion during dissemination may be slower due to additional inserts into a new table. We should ensure that the delay is minimal and wouldn't be especially noticeable to users.

### Removing basic search
Once we're confident in the new table's performance, we can remove basic search and only have advanced search available. This is because submissions will become available immediately after submission, which currently is only the case when using basic search. Effectively, "basic search" will be gone and "advanced search" just becomes "search".
* Remove all related views, tests, etc., for basic search
* The new (advanced) search should now live at `dissemination/search/`, where basic search used to be
  * Make the `dissemination/search/advanced/` URL path redirect to `dissemination/search/` so that user bookmarks and whatnot don't break.
* Remove tooltip saying SF-SACs can take 24h to appear

This change should be communicated with users, in a similar manner as described in the `API` section of this writeup.

Also, update any instructions and documents related to basic/advanced search. These can be found on the search pages themselves and on the static site. Some I've found:
* [FAQ page](https://support.fac.gov/hc/en-us/articles/29043839561869-I-just-submitted-my-audit-report-Why-can-t-I-download-my-report-from-Search-Is-there-an-error-with-my-submission)
* https://www.fac.gov/search-resources/filters/
* https://www.fac.gov/search-resources/ also seems weirdly empty
* Look for others!

### Post-search fixes
Once we're confident that the new table is working as intended and the old `dissemination_combined` MV is no longer needed, we can begin the process of removing it from the app:
1. Remove the nightly MV job
2. Remove API v1.1.1. This is the only version that relies on the MV and isn't available in prod, meaning it's not available to users
3. Remove the MV (necessarily last)

## Consequences

### Pros
* Immediate submission/SF-SAC availability
* More straightforward search experience
* A new and useful API made available to users
* Easier local testing
* No more MV generation job

### Cons
* Slightly slower dissemination
* Temporarily, more storage will be used while both the MV and new table coexist
