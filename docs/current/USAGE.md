# Use the Master Registry, personas and PBMS workflow

Use the URLs configured for your destination. The original demonstration used `g2p.wverve.in`, its **PBMS / programme operations** block, the native Master Registry service, and `/pbms-ui/#programme-flow`. Source access is public; application access still requires an authenticated account with the correct permissions.

## Registry staff and persona roles

| Screen responsibility | Native role | What to demonstrate |
| --- | --- | --- |
| Registration Officer | Registry Officer | Capture household/individual drafts, submit and correct returned work |
| Field Agent | Registry Field Agent | Field capture, own authenticated Collect setup and submission |
| Approver 1 | Registry First Reviewer | First independent native AWE review |
| Approver 2 | Registry Second Reviewer | Second independent review before native publication |
| Registry Admin | Registry Administrator | Registry configuration, staff and permissions; no capture/approval duty |

Use separate accounts for the reviews. The older registration workspace also has citizen/officer/verifier/supervisor personas; these are separate application roles, not substitutes for the current Registry or PBMS permissions. The service launcher provides navigation, not an authority to approve records. A screenshot or persona selector is not authentication.

### Household and individual journey

1. Sign in as Registration Officer. The new registry overview shows the work queues and links available to that role. Open the native household or individual intake and create a draft.
2. Complete the reviewed sections. For households, capture sponsor, informed consent, respondent, community, household details, members, dwelling/services and applicable income/health information. The current survey does **not** show an enumerator selector. Previously stored values remain in the database/history.
3. For members, enter date of birth when known or the estimated age where supported, and relationship to head. Review required fields, readable geography labels and validation feedback. Do not invent missing historical values.
4. Save the draft, review duplicate indications and submit. Duplicate scores support human review; they do not establish identity or automatically prove eligibility for a benefit.
5. Sign out and sign in as Approver 1. Open the assigned pending item, review its details and history, and approve, return for correction or reject. Give a clear reason for a return or rejection.
6. Approver 2 completes the next independent review. The creator cannot approve their own submission, and the first-stage reviewer cannot substitute for the second reviewer.
7. A returned attempt is retained in history and becomes editable for correction through the supported native process. Correct and resubmit, then follow the newly assigned review stages. A permanent rejection remains a rejection; do not edit database status fields to reopen it.
8. After final approval and native background processing, verify the resulting master record and version/history in Master Registry. For changes to an existing master, inspect before/after values and the retained earlier attempts. Household and individual journeys must both be tested.

Native Registry and AWE own these decisions. The retired supplemental `/registration/mbr` write API and import timer must not be enabled to create a parallel approval path.

### Staff administration and field capture

Registry Admin opens **Staff and roles** at `/en/configuration/registry/users`. New staff need a name, login/email, a temporary password of at least 12 characters and an assigned role. The native provisioning utility requires a password change at first sign-in; existing account conflicts preserve the original account rather than replacing its password.

Field Agent opens **Offline field capture** at `/en/offline`. When ODK has been configured, the service generates that user's private Collect setup QR. Scan it in ODK Collect, download `nsipa_registry_household`, complete a fictional interview offline, then reconnect and send. Verify one native intake arrives and the sent copy remains on the device. The import does not approve a record; the native review sequence still applies. Keep QR codes/App User URLs private. Physical-device acceptance is a separate check from desktop verification.

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
