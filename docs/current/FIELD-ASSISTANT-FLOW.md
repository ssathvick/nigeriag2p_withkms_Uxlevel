# Field assistants and two-level Master Registry authorization

This is the complete native Master Registry journey, starting from the service homepage. **Field assistant** is the operating persona; the application's existing native role and screen label remain **Registry Field Agent**. Registry approval is separate from the PBMS Finance → Audit → CEO approval and XLS workflow in [USAGE.md](USAGE.md).

## Accounts and responsibilities

| Persona | Native client role | Records and actions |
|---|---|---|
| Field assistants 01–05 | Registry Field Agent | Capture, save and submit their own records; correct their own returned interviews |
| Level 1 authorizer | Registry First Reviewer | Review field-origin submissions awaiting Level 1; approve, revalidate or reject |
| Level 2 authorizer | Registry Second Reviewer | Review submissions approved by Level 1; approve, revalidate or reject |
| MBR Officer | Registry Officer | Read-only access to published field-origin records approved by both authorizers |
| MBR Admin | Registry Administrator | View all records and rejected archives; administer staff/configuration; cannot replace the independent authorizers |

There are five dedicated field logins: `field-agent-01@nsipa.example.invalid` through `field-agent-05@nsipa.example.invalid`. The original Abuchi account may coexist as an additional field agent. Existing Abutu and Adaku remain the Level 1 and Level 2 identities on the original installation. Their passwords are preserved. A fresh installation uses its own staff identities and generated private credentials; no password is supplied by public Git.

Use exactly one Registry persona per identity. Never share a login between the two authorizers, and never give one field assistant another assistant's login or Collect QR. Login identifiers ending in `.invalid` are demonstration identifiers, not working email addresses.

## Destination setup

1. Install the native Registry, IAM, AWE, registration utility and ODK baseline described in [INSTALLATION.md](INSTALLATION.md). Preserve the existing NSIPA logo with words and sections reserved for later removal.
2. Establish the Officer, initial field agent, Level 1, Level 2 and Admin identities. Use `release/registry-accounts.example.json` with `integrate_native_registry_accounts.py --accounts PRIVATE_FILE`, inspect the plan, then apply with `--apply`. This configures the native role grants and assigns the two distinct reviewers in versioned AWE policies. It does not reset identity passwords or rewrite historical decisions.
3. For the five standard demonstration field assistants, run `provision_record_security_agents.py` after those native roles exist. It creates missing field-agent identities, preserves existing identity passwords and writes generated credentials only to the private runtime file `/opt/openg2p-lab/registration/field-agent-accounts.json`. `NSIPA_FIELD_CREDENTIAL_EXPORT` can select a separate private export path. Do not commit that file.
4. If using your own five field identities instead, create them through the destination identity administration tools and assign the native Field Agent role. `release/registry-field-accounts.example.json` shows the nine-account mapping. Replace its placeholder reviewer/Officer/Admin logins and establish every identity before applying it with the integration utility. The integration utility assigns roles to existing identities; it is not an identity-creation utility. Skip the standard demonstration provisioner when those default five logins are not wanted.
5. Install the database/API/AWE enforcement in the order documented in [RECORD-SECURITY.md](RECORD-SECURITY.md). Install the updated ODK worker and authenticated offline setup module, then build/deploy the Registry frontend. Refresh the field identity directory with `deploy_awe_record_security.py` after membership changes. A role selector or frontend build alone does not enforce ownership.

Reviewers configured in a newly versioned policy apply to new requests. Existing pending requests retain their policy/task history and must be reconciled explicitly during a reviewer migration. Do not rewrite task assignees or approval states directly in the database.

## Online demonstration: field assistant

The example below uses fictional information and stops at the mobile setup QR before any phone interviews are performed. Replace the service hostnames for another installation.

### Open the field workspace

1. Open `https://g2p.wverve.in/` and choose **Master Registry → Open Master Registry**.
2. Sign in as Field Agent 01 using the privately issued credential.
3. Confirm the displayed account name and the **Your records only** notice. Counts and searches apply to that account's accessible records. An existing demo draft may already be present; an empty workspace is not required.
4. Choose **Register your household**. Open **View submissions** instead when resuming an existing draft; do not create a second household to recover a saved interview.

### Survey consent and location

1. In **Survey Consent & Enumeration**, select **NSIPA** as sponsor.
2. For this fictional example select **Yes — informed consent given**. In a real interview, record the respondent's actual decision and stop if consent is refused.
3. Enter respondent **Ada Okafor – Demo** and community **Demo Community**.
4. Select **Lagos → Agege → Isale/idimangoro** from the State/LGA/ward catalogue. Enter a unique demo survey serial such as **DEMO-FA01-002** and the fictional address **Fictional demonstration household, Agege**.
5. Leave optional coordinates blank for this desktop example. GPS capture is a separate device action and does not verify residence. Click **Next**, then confirm that the section is marked **Saved**.

### Headship and household members

1. Enter household name **Okafor Household – Demo 002** and household head **Ada Okafor – Demo**.
2. Select **1** for the total household heads and **Yes** for the complete head list. Leave optional head reference/headship type blank if not part of the example. Click **Next**.
3. In **Household Member Details**, choose **Add Household Member**. Enter surname **Okafor – Demo**, first name **Ada**, relationship **Household head**, sex **Female**, and estimated age **35**. Use a known date of birth instead of age when appropriate.
4. Select **No** for NIN/tracking number for this fictional member. Leave contact/bank/BVN and other optional details blank rather than inventing identifiers. National ID authentication is not connected; identification details are self-reported.
5. Click **Save Member**, verify the member row, then **Next** to save the section. Add other actual household members in a real interview; the example is a one-member household.

### Other sections, draft and submission

1. Review **Household Living & Dwelling Characteristics**. An illustrative answer is **Permanent** dwelling and **10** minutes for water collection. Optional unanswered items remain blank.
2. Review **Household Income, Vulnerability to Shocks & Coping**, **Health Insurance Coverage**, **Household Assets & Possessions**, and **Crops Grown**. Enter applicable answers and save each changed section. Do not interpret a blank answer as a negative response.
3. Show **Additional asset records**, **Household programmes**, and **Household Roster**. These retained sections are not removed by the security update. Add rows only when relevant to the interview.
4. Use **Save Draft** to preserve work. To resume, open **View submissions → Draft**, select the same household and continue its editable sections. Record its application reference before switching accounts. If authentication refreshes the page, recover the saved draft rather than starting another form.
5. Check the final registration confirmation, review required-field feedback and choose **Submit**. Confirm that the record is pending Level 1. Submission is not approval and does not guarantee programme eligibility or payment.

## Level 1 authorizer

1. Sign out of the field account and sign in using the dedicated Level 1 identity. Confirm the Level 1 notice before making a decision.
2. Open **My tasks / Approvals → Registration reviews** and the matching household reference. Only field-origin records currently awaiting this level are accessible.
3. Review the consent, location, member details, survey information, duplicate indications and available history. Duplicate scores support review; they do not authenticate a person.
4. Choose **Approve** to pass the record to Level 2. After the accepted decision, the reviewer returns to the pending queue.
5. Confirm that the record is absent from Level 1 and, on refresh, from the creating field assistant's workspace. Direct URLs and API requests also lose access. Officer still cannot see a published record at this stage.

## Level 2 authorizer and publication

1. Sign out and sign in using the dedicated Level 2 identity.
2. Open **My tasks / Approvals → Registration reviews** and the same reference. It becomes accessible only after Level 1 approval.
3. Review the details and Level 1 decision/history, then choose **Approve**.
4. Confirm that the record disappears from Level 2's accessible queue. Wait for native background publication to finish; a brief delay does not justify forcing database status values.
5. Sign in as **MBR Officer**, open the household/individual Master Registry and verify the published household and member. Officer has read-only access to field-origin records approved by both levels. Admin can still inspect the record and its history.

## Revalidation at either level

Use a separate fictional record when demonstrating alternate outcomes.

1. While a record is awaiting the current authorizer, enter a clear correction reason and choose **Revalidate — return to field agent**.
2. The returned record disappears from that authorizer and becomes visible/editable only to the creating field assistant, with Admin retaining oversight. Other field assistants cannot open it.
3. The creator opens the returned submission, reads the reason, corrects the existing record and saves. Preserve its household/member identity and reference.
4. The creator resubmits. A new review attempt starts at **Level 1**, including when Level 2 requested the correction.
5. Complete both approvals again. Earlier attempts and correction reasons remain in history; old approvals do not authorize the new attempt.

## Permanent rejection at either level

1. Enter a rejection reason and choose **Reject permanently**. Use the revalidation action when correction is intended; a reject comment containing the word “revalidate” does not change the action.
2. The record is no longer available to the creator, other field assistants, either authorizer or Officer.
3. MBR Admin opens **Form submissions → Rejected archive** to inspect the record, reason and review history. Rejection preserves the record rather than deleting its audit trail.

## Phone setup: stop at the QR

1. Return to the creating field assistant's account and open **Offline field capture** from the Registry overview, or use the homepage's **Mobile field registration** block.
2. On the Android phone/tablet, install **ODK Collect**. The mobile collection app is ODK Collect, not Odoo.
3. In the browser choose **Show my private setup QR** and verify that it is assigned to the intended field assistant.
4. On the phone choose **Add project → Scan QR code**, then scan the browser's code. The setup belongs to that assistant; keep it private and outside public repositories.
5. **Stop the demonstration here** if the next session is reserved for mobile offline/online operations. Do not claim that physical-device capture or reconnection has been verified merely because a QR was displayed.

For the later mobile session, download the household form while online, capture and save/finalize an interview offline, reconnect and check the send receipt, then verify one native intake with the same field owner. The private synchronization worker uses Central's authenticated submitter ID, not editable enumerator text. Both authorizers must still approve before Officer can see the published record. Unknown submitter mappings are quarantined for reconciliation.

## Acceptance checklist

- Each of the five field assistants can create/read their own draft and cannot list, count, read, edit or retrieve another assistant's record by direct ID.
- Level 1 cannot view drafts or Level 2 work; Level 2 cannot view unapproved Level 1 work. Completed queues do not restore handed-off access.
- Officer sees only published field-origin records approved at both levels, and cannot capture, edit or decide reviews.
- Revalidation at both levels returns only to the creator; resubmission restarts both reviews. Permanent rejection at both levels leaves Admin-only archive access.
- Admin retains all records/history. Older records without trusted staff-subject provenance remain Admin-only until an audited migration establishes their owner.
- Online and later offline capture use the same ownership and review rules. Preserve backups and keep credentials, QR codes, signing keys, operational records and private test evidence outside public Git.
