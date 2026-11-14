# Use the Master Registry, personas and PBMS workflow

Use the URLs configured for your destination. The original demonstration used `g2p.wverve.in`, its **PBMS / programme operations** block, the native Master Registry service, and `/pbms-ui/#programme-flow`. Source access is public; application access still requires an authenticated account with the correct permissions.

## Registry staff and persona roles

The complete [Field assistant and Level 1/Level 2 walkthrough](FIELD-ASSISTANT-FLOW.md) covers destination setup, five field accounts, browser capture, both authorizers, approved-only Officer access, revalidation, rejection and the ODK Collect QR stopping point. The [security guide](RECORD-SECURITY.md) describes backend/database enforcement.

| Screen responsibility | Native role | What to demonstrate |
| --- | --- | --- |
| Field assistants 01–05 | Registry Field Agent | Capture and submit only their own records; correct their own returned records; use their own Collect setup |
| Level 1 authorizer | Registry First Reviewer | Review field-origin submissions awaiting Level 1; hand off or return/reject |
| Level 2 authorizer | Registry Second Reviewer | Review Level 1-approved submissions; approve publication or return/reject |
| MBR Officer | Registry Officer | Read-only access to published field-origin records approved at both levels |
| MBR Admin | Registry Administrator | All records, rejected archives, staff/configuration and retained history; no substitute reviewer |

“Field assistant” and “Field Agent” refer to the same native Registry persona. Use separate accounts for each duty. Older citizen/officer/verifier/supervisor workspaces have separate application roles and do not replace these permissions. The service launcher provides navigation, not authority to approve records.

### Household and individual journey

1. From the service homepage, open **Master Registry** and sign in as a **field assistant**, not MBR Officer. Confirm the displayed identity and **Your records only** notice.
2. Choose **Register your household** or the supported individual intake. Capture sponsor, actual informed consent, respondent, community, location and required details. The current household survey has no enumerator selector.
3. Add household members, including relationship to the head and a known date of birth or estimated age. Identification details are self-reported; national ID authentication is not connected. Leave unknown optional values blank.
4. Save the draft and verify its reference. Resume an existing interview through **View submissions → Draft** rather than creating a duplicate. Review applicable dwelling/services, income/shocks, insurance, asset, crop and retained sections. Check validation and submit for Level 1.
5. Sign in separately as **Level 1**, open the assigned pending registration task, inspect details/history and approve. The record leaves the creator and Level 1 and becomes available only to Level 2, with Admin retaining oversight.
6. **Level 2** independently reviews and approves. The record leaves that reviewer's access. After native publication finishes, **MBR Officer** can read the approved master record; Officer cannot capture, edit or approve it. Admin retains access and history.
7. At either review level, **Revalidate — return to field agent**, with a reason, returns the record only to its creator. The creator corrects and resubmits the same record; review restarts at Level 1 and proceeds through both levels again. Earlier attempts remain in history.
8. **Reject permanently**, with a reason, archives the record for **MBR Admin only**. The creator, other field assistants, both authorizers and Officer lose access. Admin uses **Form submissions → Rejected archive**.

The native Registry API, PostgreSQL policies and AWE enforce these rules for direct IDs, lists/counts, histories and task queues. A completed queue or old URL does not restore access. Registration approval is separate from programme eligibility/payment. Test both household and individual journeys on the destination.

### Staff administration and field capture

Admin uses **Staff and roles** at `/en/configuration/registry/users`. The normal staff utility creates new staff with a name, login/email, native role and a temporary password of at least 12 characters, requiring a password change at first login. The separate demonstration field-agent provisioner writes generated credentials privately; existing identity passwords are preserved. Follow the destination setup sequence in the detailed field-flow guide, then refresh the private field/admin identity directories.

The field assistant opens **Offline field capture** at `/en/offline` and chooses **Show my private setup QR**. Install **ODK Collect** on Android, choose **Add project → Scan QR code**, verify the assigned account and scan. Stop there when phone offline/online capture is reserved for a later session.

In that later session, download `nsipa_registry_household` while online, save/finalize an interview offline, reconnect and confirm delivery and retained sent copies. Verify exactly one native intake attributed to the authenticated field owner. The worker uses Central's submitter identity, never editable enumerator text, and never approves records. Both authorizers still review before Officer receives the published record. Physical-device acceptance is separate from desktop verification. Keep QR codes/App User URLs private.

Native Registry/AWE remain the workflow owners. Do not enable the retired supplemental `/registration/mbr` writer/import timer as a parallel approval path.

## Five-account PBMS approval journey

| Account | Responsibility |
| --- | --- |
| Programme Admin | Create/configure the programme, manage monthly cycles, review/correct lists and export after final verification |
| Payment | Review the prepared disbursement list and initiate or resubmit approval |
| Finance | First approval: beneficiary count, amounts, programme maximum and total |
| Audit | Second approval: eligibility/evidence and the prior review trail |
| CEO | Final independent approval |

A staff access administrator separately grants programme membership to these accounts. General staff administration is not implicitly given to Programme Admin. Do not combine these five duties into one account for the recorded end-to-end demonstration.

### A. Programme setup

1. Start from the destination service portal and open the PBMS block / programme operations. Sign in to PBMS as **Programme Admin**, then choose **Programme approval flow**.
2. Create a programme with name, description and the correct base registry: Household, Farmer or Student. Confirm the new programme is Active.
3. Create or select a digital cash Benefit Code with currency **NGN**. Map it to the programme.
4. Set the monthly entitlement, up to **NGN 25,000 per beneficiary per cycle** for this policy. Select the actual Finance, Audit and CEO approval groups. Enrolment uses zero verifications with automatic approval; disbursement uses all three approval levels with automatic disbursement approval off.
5. Enter and save the eligibility criteria for the programme's native PBMS registry. An example income rule is `[('annual_income', '<=', 300000)]`; confirm fields/types and the intended population before use. To reproduce the small recorded example, first create or synchronize two clearly fictional PBMS registry records and deliberately restrict the criteria to those records. The original `NSIPA-PRESENTATION-*` records are not supplied by a source clone.
6. Save programme configuration before creating cycles. Rules lock once lists exist. A staff access administrator now assigns each dedicated account to the newly created programme through **Staff access**, or the provisioning utility with the destination programme ID.

Master Registry and PBMS retain distinct native models/databases. Confirm the configured registration/household adapter synchronization and the destination PBMS registry contents; do not assume every native Registry approval automatically appears in every PBMS programme without that integration.

### B. Enrolment and disbursement lists

7. Under **Monthly cycles**, create the enrolment cycle with a registration start/end and disbursement start/end. Registration must have closed before list generation. Use suitable destination dates; the original November 1–12 / November 20–28 example becomes unsuitable when replayed in another month. Duplicate cycles for the same programme/month are prevented.
8. Choose **Create enrolment list**. It appears Pending while the scheduled worker evaluates actual registry records. Refresh after processing. Complete/auto-approved enrolment and its beneficiary count should become visible. Investigate processing errors before proceeding.
9. Create a disbursement cycle linked to that **approved enrolment cycle**, give it a clear name and schedule it within the disbursement window.
10. Create its disbursement list. Wait for the scheduled eligibility and entitlement calculation to finish, then open **Beneficiary lists**. Review the number of beneficiaries, every included record, each entitlement and the total. Complete calculation alone is not final approval.

### C. Payment, Finance, Audit and CEO

11. Sign out of Programme Admin and sign in as **Payment**. Select the same programme/list, add a review comment and choose **Initiate approval**. Status becomes **Awaiting Finance**.
12. Sign in separately as **Finance**. Open the item from the approval queue or the same programme's list, inspect the beneficiaries and amounts, enter a reasoned comment, optionally attach supporting evidence, then **Approve and save**. Status becomes **Awaiting Audit**.
13. Sign in as **Audit**. Review the list and prior Finance decision, enter the audit comment/evidence and approve. Status becomes **Awaiting CEO**.
14. Sign in as **CEO**. Review both prior decisions and the proposed total, add the final comment and approve. Status becomes **Fully verified**. The history records the authenticated actor, comment, UTC time and revision for every decision.

The sequence is server-enforced; React cannot authorize its own status changes. Programme membership, configured group and independent identity checks apply even to direct backend calls.

### D. Rejection and correction

If any reviewer rejects the list, Programme Admin reviews the rejection and corrects existing beneficiary entries with a mandatory reason. Supported corrections include an entitlement change and exclusion/reinclusion of an existing beneficiary. Amount limits still apply. Payment then resubmits. This creates a new revision and restarts Finance, Audit and CEO review from the beginning; earlier decisions and correction before/after values remain in history.

Do not count an old revision's approvals toward the new revision. Do not alter approved data directly in PostgreSQL or bypass the correction actions.

### E. Final XLS export

15. Return to **Programme Admin** and open the Fully verified list. Confirm the revision, count, included rows and total.
16. Choose **Export Beneficiaries (.xls)**. The backend verifies the three independent approvals against the current list content/hash and creates native binary BIFF XLS, not a renamed CSV. The export event is retained in the history.
17. Open the downloaded file in Excel or another XLS-compatible application. Verify beneficiary ID, name, state, amount NGN, programme, disbursement cycle and revision. Larger exports can span worksheets. For a two-household example at NGN 25,000 each, the total must be **NGN 50,000**.

The final XLS is the endpoint of this approval policy. It **does not invoke Bridge, bank transfers or reconciliation**. Historical programmes retain their separate legacy payment workflow and are not retroactively converted by installing the addon.

## Branding, retained sections and contextual help

The current sidebar/login retains the established `branding/nsipa-logo.svg` with its wording. Sections marked for future removal remain available: Households, Farmers, Students, Priority rules, Agencies, Warehouses & banks, States & regions, Local administrative areas, Agency benefit assignments, Bank & warehouse assignments and Verification queue. Do not remove them as an installation cleanup step.

The application includes contextual help and shared knowledge sources. Publish new guidance through the configured knowledge review/publication process. Local Ollama and analytics services are optional integrations with separate setup requirements. The standalone Experience Kit is useful for a quick preview but is not the full connected application described above.

## Registry record ownership and authorizers

See the [record-security access matrix, deployment steps and operational guide](RECORD-SECURITY.md). Install the security layer after the native Registry/AWE baseline. Field agents own only their records; Officer reads only field-origin records approved at both levels. Return for revalidation and permanent rejection have distinct visibility rules. Legacy records without trusted subject provenance remain Admin-only.
