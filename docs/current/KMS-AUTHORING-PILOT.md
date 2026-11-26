# KMS authoring and review pilot

This internal desk review uses 15 existing guides from the 568-guide release seed. Five represent each level. The sample includes the three generic Help examples, a returned registration and a payment decision. The findings apply to this sample. The operational rules still need PMO or NSIPA validation.

## How to draft and review

| Level | Authoring prompt | Reviewer checks |
| --- | --- | --- |
| Field | What does this input mean? What should the user enter or select? Give the supported format and the response to an unknown or invalid value when relevant. | The value, constraint and recovery are clear from the field guidance alone. |
| Screen | Name the role and starting state. Use visible controls in task order. Give the result, next role and recovery from a common exception. | A user in the stated role can follow the controls. A read-only user is directed to the appropriate next role. |
| Workflow | Identify the entry and exit, who acts at each stage, what evidence changes hands, and where returns and exceptions go. Link to applicable child guides. | Each handoff has a recipient. A return can be followed back to the correct stage. The reader can locate the next task. |

Use the staff authority-reference field for the owner, revision and section supporting each policy claim. Enter unresolved claims as NEEDS SOURCE in review comments. Published sandbox examples, UI labels and upstream documentation can support technical observations. They do not establish Government policy. Record editorial findings against the article version through the existing review or return action.

## Sample findings

The article keys below omit the common `context-` prefix. “Retain” means the wording supports the sampled task. Every sample lacks a named Government authority reference in the seed.

| Level | Article key | Editorial finding |
| --- | --- | --- |
| Field | register-consent-answer | Source needed. The field gives an explicit refusal action. Obtain the controlled consent wording and refusal procedure before operational use. |
| Field | register-member-age | Revise. Keep the completed-years instruction and identify the procedure to use when the reported date is uncertain. The field article also contains guidance outside its main text. |
| Field | imports-return-note | Retain. It gives the purpose, the 500-character limit and where the operator sees the reason. Verify the limit against the receiving control during integration. |
| Field | pbms-approval-comment | Retain. It identifies the decision maker, what a rejection comment should explain and where to find it in history. |
| Field | pbms-sponsor-routing | Retain. It tells the user what route to select and who can resolve a missing route. Confirm the authorised route source. |
| Screen | register-intake-queue | Route by reviewer level. The queue explains how to locate an assignment but gives no level-specific handoff. Keep the queue guide for an empty queue or unknown role. |
| Screen | register-submission-detail | Route by action. Keep the inspection guide for a read-only record. Show the relevant decision guide when an assigned reviewer has decision controls. |
| Screen | register-returned-intake | Retain. It names the feedback, the correction, the resubmission and the next level. Check the return loop with a synthetic record in integrated UAT. |
| Screen | pbms-flow-open | Route by state. The overview explains list totals and tabs. A verified list with missing routing needs the existing payment-specific guide. |
| Screen | pbms-finance | Retain the decision sequence. Separate initial checks from corrective-payment and reopening checks when editing this guide next. |
| Workflow | register-journey | Revise. Make the creator’s responsibility for a returned record explicit and link to the returned-registration guide. |
| Workflow | imports-journey | Retain the operator and approver handoff. Link the reconciliation and receipt guides at the transfer step. |
| Workflow | pbms-flow-journey | Retain the ordered Finance, Audit and CEO decisions. Add direct links to decision and payment-report guides at their respective stages. |
| Workflow | pbms-duplicate-reversal-workflow | Retain the distinction between an exact resend and a different movement. Link the named discrepancy guide and obtain the controlled reopening authority. |
| Workflow | pbms-partial-payment-workflow | Retain the instruction-level handoff. Add a reference for deciding when CEO escalation is needed. |

## Unpublished wording examples

- **Field, member age.** “Enter the known date of birth. If it is unknown and the form offers an age field, enter the estimated age in completed years. Preserve the precision the respondent supplied.” The verification procedure remains open for sourcing.
- **Screen, submission details.** “Check the submission reference and review history. If you have an assigned decision, open it from Approvals and confirm the review level.” Use the returned-registration guide when the creator is correcting a returned record.
- **Workflow, registration return.** “The reviewer records the reason. The creator opens the same submission, reads Review feedback, corrects the affected section and resubmits. Level 1 receives the corrected submission.” Validate this sequence against the final integrated workflow.

No sampled article was republished. This was an editorial review against the source snapshot, without an independent human calibration exercise or a Government approval decision.
