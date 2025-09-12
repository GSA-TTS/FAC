# 46. Digitally signing data

Date: 2025-09-12

## Status

Accepted

## Areas of impact

*   Compliance
*   Engineering
*   Policy

## Related resources

* https://en.wikipedia.org/wiki/Hash_function
* https://www.codecademy.com/resources/blog/what-is-hashing

## Context

The FAC holds nearly $9T in audit records and financial history of federal spending. However, we do not sign, or hash, any of this data. While we trust ourselves and our security processes (e.g. NIST controls, encryption at rest, etc.), this is still a problem.

Although it is difficult to engineer a system that is robust against changes made by owners of the system, the FAC has the benefit of all of its data being public. Therefore, if we cryptographically sign our data, we are asserting (mathematically) the state of the data at a single point in time. By publishing those signatures, others can verify that the data they have matches what it was at some point in the past. And, if the data ever chagnes, one of two things will be true:

1. The data changes, and the signature does not. This means the data was tampered with or changed without a new signature being calculated. It could be an honest mistake, or it could be a sign that data in the FAC was tampered with. 
2. The data changes, and the signature changes. This could be because the data legitimately changed, and the signature had to be recalculated. Or, it could have been tampered with, and the signature updated to make the change look legitimate.

In the case of #1, consumers of the data are able to compare the data they downloaded in the past with the new data, and determine exactly what changed. The fact that the signatures did *not* change serves as a red flag, and encourages them to look closely at the contents of (say) a row of data or a PDF report.

In the case of #2, the FAC can easily post updates pubilcly when all of the signatures are going to change. For example, if a new field is added to the data, the signatures will change. In this example, it should be the case that the *prior* fields would still hash to the same value, meaning that consumers of the data could determine that nothing in their prior downloads changed. They could, in a word, trust the new signatures.

However, it could also be that (in the case of #2), there were changes to the data such that consumers of our data see things that no longer align with the past record. In this case, they have a path to enquire. There are many reasons this might happen; for example, we know we have "off-by-one" errors in some of our dates (see fac.gov/data). When this is fixed, those signatures will change. But regardless of the reason, the change of the signatures are a clear indicator that *something* of import has changed.

Fundamentally, this is basic data security and integrity work. Further, it provides a way for downstream users of the data to quickly and reliably assess the correctness of their own data downloads. It is a light lift, engineering-wise, with powerful and positive impacts to the data integrity and quality in the FAC. 

## Decision

1. Add row-level hasing to all internal and external tables in the FAC.
   1. Specifically, to `SingleAuditChecklist` and `SingleAuditReportFile` internally, and all `dissemination_` tables externally.
2. Add a hash of the Single Audit Report PDF table (internally). Include that hash in the `general` table in dissemination. 

The algorithm used is (as of this draft):

1. Take a list of fields to compute over/hash from the data object (e.g. a `General` object).
2. We convert the object to a dictionary.
4. Convert the dictionary (of the shape `{"key": "value"}`) to a list of tuples of the shape `[("key", "value")]`.
5. Sort the list of tuples alphabetically by the key (the 0th element of the tuples).
6. Filter the list of tuples so we only keep values associated with hashable fields.
7. Get rid of the field names, so we have a list of only the values.
8. Combine all values into a single string without adding spaces. Any existing spaces in the data are left as-is. Strip any whitespace from the beginning and end of the line (including newlines, etc.). Convert that to a UTF-8-encoded byte array.
9. Run a SHA1 on the resulting byte array.
10. Return the hex digest of the SHA1.

```
def hash_dissemination_object(obj):
    # Given a hash, alpha sort the keys. We do this by taking
    # the object to a list of tuples, and then sorting
    # the resulting list on the first element of the tuple.
    #
    # See https://stackoverflow.com/a/22003440
    # for reference. It isn't obvious how to do this well, and in particular,
    # while leaving the JSON object keys out of the hash.

    # 1. Get the fields we're going to hash from the object
    fields_to_hash = obj.HASH_FIELDS
    # 2. We are given a Django object. Convert it to a dictionary.
    d = model_to_dict(obj)
    # 3. Dictionary to tuples
    tupes = list(d.items())
    # 4. Tuples sorted by key
    sorted_tupes = sorted(tupes, key=lambda k: k[0])
    # 5. Get rid of fields that we're not hashing
    filtered_sorted = list(filter(lambda t: t[0] in fields_to_hash, sorted_tupes))
    # 6. Strip the keys
    # Why strip the keys? We don't want our field names to impact
    # the hashing value. We want to make sure the values in the object, in a consistent sort
    # order, are what get hashed. If we change field names, yes, the hash will change. But
    # our object field names are very consistent.
    # It is unclear if we're going to get consistent, cross-language hashing here.
    # It depends on how Python chooses to reprseent values as strings. If we don't quite get this right
    # the first time, it will have to be improved, and the full dataset re-disseminated.
    # p[0] is the key, p[1] is the value in the tuple list.
    # Strings must be encoded to bytes before hashing.
    just_values = list(map(lambda p: convert_to_string(p[1]), filtered_sorted))
    # 7. Append the values with no spaces.
    smooshed = "".join(just_values).strip().encode("utf-8")
    # This is now hashable. Run a SHA1.
    shaobj = sha1()
    shaobj.update(smooshed)
    digest = shaobj.hexdigest()
    return digest
```

as found in `intake_to_dissemination.py`. 

## Consequences

The consequences are all net-positive. We will be able to write more validations that assert the consistency of our data, and our users will similarly have more confidence, over time, in the data we publish. 
