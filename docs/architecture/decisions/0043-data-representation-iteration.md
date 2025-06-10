# 43. Data representation iteration

Date: 2025-04-30

## Status

Accepted

## Areas of impact

- Compliance
- Engineering
- Policy
- UX

## Related documents/links

* https://www.postgresql.org/docs/current/datatype-json.html

## Context

The Federal Audit Clearinghouse not only collects data, but maintains it over time. Just like a caretaker at a zoo, or a curator at a museum, the Clearinghouse must clean and care for the data on an ongoing basis.

The goal of this care is multi-fold. 

1. **The data must be correct**. Sometimes, data is submitted incorrectly. Even with data validations and other controls, users can still make mistakes. Or, we can. In the event of errors, the FAC must have a way to (with approvals and an audit trail) update, fix, or otherwise maintain the correctness of the data.  
2. **The data must be usable**. The FAC provides a web-based interface to search, an API, and the ability to download data as CSV-formatted files. The search and API must be usable and performant, which means that both the data and the interfaces to it may need to change to meet the changing needs of government, grantees, auditors, and the public.  
3. **The data must be growable**. As the SF-SAC changes over time, the representations of the data must be able to change flexibly. And, as we accommodate more kinds of interaction with the data (e.g. the ability to update and resubmit data), we must maintain auditable trails that maintain a history of the federal record.  
4. **The data must be performant**. Some operations can be run overnight (e.g. exporting CSV data). Some must be timely and performant, responding in less than a second (e.g. search). The way the FAC represents data impacts all of the operations people make on the data, from submission to search.

The original design of the FAC’s data systems were inspired by the model used by Census. This was to minimize the change-management costs associated with moving a system between agencies. The FAC maintained the shape and contents of both the intake forms (so that auditors and auditees would have a familiar process for submitting their Single Audit) as well as the output format. Specifically, the API was designed to reflect the CSVs that Census would export, meaning we had a `general` endpoint, a `federal_awards` endpoint, and so on.

This led to a design where we had one database table for the intake of data, and multiple tables for the output. A schematic of the data and associated processes looked like:

```
 SAC Table            Copy data to      ◄──────────►   API & web search   
 ▲   ▲   ▲            dissemination                    used to access data
 │   │   │    ───►    tables  ▲             ◄──────►                      
 │   │   │                    │                                           
                                                                          
SF-SAC pieces         Auditee & auditor                                   
uploaded to           completes the SF-SAC                                
the FAC                                                                   

```

This design keeps the intake processes (e.g. the submission and validation of the many parts of the SF-SAC form) separate from the dissemination processes (e.g. web search and APIs). This provides some benefits, like the ability to optimize the different processes differently, but it creates long-term maintenance difficulties. For example, if users want to update their data, tracking those changes must happen in one place, but be propagated (and possibly tracked) in *two* places.

In order to better handle issues of performance, maintainability, and revision, the FAC is updating its data representation to have a single “source of truth,” meaning that there will only be one data table to both capture the intake of information as well as provide dissemination of data. 

## Design

A single “source of truth” (or SOT) makes revision and changes to the data over time easier, as it eliminates the question of how to keep multiple copies of the data in sync. It presents other challenges (e.g. the tables must be performant for both intake/update operations as well as handle the load of search queries and data extraction), but the issues of *data* *consistency* and *currency* are eliminated. Ultimately, a SOT eliminates or simplifies many negative outcomes for government, auditees/auditors, and the public because we do not risk having data represented in two different ways in two different places.

The SOT table design is expressed in our code here:

[https://github.com/GSA-TTS/FAC/blob/main/backend/audit/models/audit.py](https://github.com/GSA-TTS/FAC/blob/main/backend/audit/models/audit.py)

It is a single table that represents each portion of the submission as a JSONB data structure. This allows us to take our data from upload and validation directly into the table. 

Once the audit is complete, we then express queries over the data (fundamentally) as SQL, but do so not over a strictly *relational* table, but a hybrid relational/semi-structured table. That is, to query the UEI of an auditee, we would look in the `general_information` column of the `audit` table, but we would then need to reach into the JSONB structure contained in that column for the `auditee_uei` field. Similarly, the rows of the `federal_awards` workbook are represented as a JSON array within the `federal_awards_information` column, and all queries that might have previously operated on a relational representation of this data now query into the arrays themselves.

To maintain performance, we index key data. The result is that we find many operations to be *faster* than on our prior relational tables.

## Decision

In order to accommodate accurate and reliable updates to data, the FAC is migrating its data to a single “source of truth” (SOT) data structure. This will allow audit trails of revisions to be kept. A SOT representation also makes future improvements to the SF-SAC easier to implement, as there is only one table to modify and update, as opposed to having to think about how to incrementally update two tables and maintain synchrony. 

(It is also important to note that changes to the SF-SAC—for example, adding a data field—means that all *prior* data does *not* have that field. Therefore, the FAC ends up with *generations* of data representations. A single SOT makes it easier to handle these changes over time as well.) 

## Consequences

This is a data migration, not unlike the move from Census to GSA. However, the data migration is taking place from one well-maintained and validated data source to another. Further, the FAC is able to evaluate the migration and guarantee that 100% of the data migrates from one structure to the other. It can also be done in a way that maintains the existing interfaces, meaning that the change management cost for the public and government is zero. The submission and search experiences (including the API and data export) will remain unchanged from a user’s point of view.

Ultimately, given the need to expand the SF-SAC over time, to transparently and reliably handle the update and revision of data, as well as improve our ability to analyze and provide oversight across government, the SOT model is a natural progression in the caretaking of the FAC’s data.
