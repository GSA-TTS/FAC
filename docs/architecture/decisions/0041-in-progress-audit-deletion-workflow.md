# 41. In-Progress Audit Deletion Workflow

Date: 2024-12-11

## Status

Accepted

## Areas of impact

*   Design
*   Engineering
*   Process


## Related documents/links

## Context:  
**Problem Statement:**  
Users frequently create new audit submissions but often abandon them before completion, resulting in a cluttered dashboard view. These incomplete audits create confusion among editors and certifying officials as they navigate numerous partially completed entries. A solution is needed to allow users to manage incomplete audits without risking the accidental deletion of valid or in-progress audits.
While allowing users to delete audits could help reduce dashboard clutter, it introduces the risk of accidental deletion of important or in-progress audits. Such actions could lead to increased user support requests for audit recovery, a task that we are not well-equipped to handle with current resources.

**Objective:** 
Develop a controlled workflow that enables users to remove incomplete audits only (not completed) while minimizing the risk of accidental deletion. The workflow should incorporate checks and balances, such as inactivity thresholds or dual approval mechanisms, to ensure that audits are removed only when appropriate.

## Decision (Proposed Workflow Solution):

 **User-Initiated Deletion Process:**
- Access-Based Deletion: Any user with access to a specific audit can initiate a deletion request.
- Flagging as Deleted: Once deletion is initiated, the audit record is flagged as "deleted," removing it from the initiating user's audit list and making it inaccessible to all other users. However, the record itself remains in the database for future auditing purposes.
- Auto-Cleanup: A Django command or Django Admin process will periodically scan for flagged records and remove those marked "deleted" for more than a specified duration (to be determined by the team) from the database.

## Consequences

**- Reduced Dashboard Clutter:** The workflow will help maintain a cleaner dashboard view by allowing users to remove incomplete audits, reducing confusion for editors and certifying officials navigating audit entries.

**- Minimized Risk of Accidental Deletion:** By flagging audits for deletion rather than immediately removing them, the system provides a buffer period, allowing users or administrators to intervene if an important audit is flagged in error.

**- Improved User Experience:**  Users will have more control over their audit list, leading to a streamlined experience, as they can manage abandoned audits without cluttering their workspace.

**- Additional Database Management Requirement:** The system will need periodic monitoring to ensure flagged entries are appropriately purged. 

## Metrics 
- Decrease in Zendesk Helpdesk tickets after the feature gets released as tracked by number of times macro gets used.
