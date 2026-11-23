# Master Beneficiary Registry contextual help audit

23 November 2026 · NSIPA sandbox · English interface

## What changed

The **Form submissions** information button now opens **Registration review queues** wherever that card is visible. Under **Approvals**, the registration task queue opens **My registration reviews**. A user can read queue guidance even when the queue is empty.

Dashboard cards, registration and review screens, individual record change-request lists, offline collection and configuration now select guidance for the current task. Restricted, missing and failed screens explain how to proceed. Each public contextual Registry guide opens its matching documentation page.

## Verification

- Five sandbox roles were used. The table covers 44 desktop and 16 mobile role and screen combinations, with 174 help openings checked against expected guide titles.
- An additional 28 mobile field and section checks verified the guide title, documentation link and drawer width at 390 pixels. These covered the household questionnaire and the data policy form.
- A browser fixture checked all 44 native route templates found in the application source and ten additional states. These included first- and second-level approval, disabled decisions, both duplicate tabs, returned intake, and errors.
- Data Imports passed 62 checks across 57 topics. Of these, 24 used live views, 33 used simulated workflow states in the browser, and 5 used the guide browser.
- Some configuration and messaging pages showed **Access restricted** for the available accounts. The restricted view was verified live. The underlying page’s help selection was verified with the browser fixture. This audit exercised the sandbox and the English interface.

## Live results

| View | Role | Screen or route | Help openings | Guides shown |
|---|---|---|---:|---|
| Desktop | Second Reviewer | dashboard | 5 | Assigned Registry reviews, Start or track household registration, Registration review queues |
| Desktop | MBR Officer | dashboard | 4 | Published Registry records for MBR officers, Start or track household registration, Published Registry records |
| Desktop | Field Agent | dashboard | 4 | Registration and field work, Start or track household registration, Registration review queues |
| Desktop | Registry Administrator | change-request | 1 | Change requests |
| Desktop | First Reviewer | dashboard | 5 | Assigned Registry reviews, Start or track household registration, Registration review queues |
| Desktop | Second Reviewer | tasks/intake-form | 1 | My registration reviews |
| Desktop | MBR Officer | tasks/intake-form | 2 | Access to this Registry screen |
| Desktop | Field Agent | tasks/intake-form | 2 | Access to this Registry screen |
| Desktop | First Reviewer | tasks/intake-form | 1 | My registration reviews |
| Desktop | Registry Administrator | configuration/awe-policy-config | 5 | Registry approval policy configuration, Choose a configuration section |
| Desktop | Second Reviewer | data-imports | 2 | Access to Data Imports |
| Desktop | MBR Officer | data-imports | 2 | Access to Data Imports |
| Desktop | Field Agent | data-imports | 2 | My Data Imports batches, Data Imports transfer history |
| Desktop | Registry Administrator | configuration/data-models | 2 | Access to this Registry screen |
| Desktop | First Reviewer | data-imports | 2 | Data Imports approval queue, Data Imports transfer history |
| Desktop | Field Agent | intake-form/household/new/{record} | 1 | Register a household |
| Desktop | Registry Administrator | configuration/data-policies/new | 8 | Create a register data policy, Choose a configuration section, Check data policy filters |
| Desktop | Registry Administrator | configuration/data-policies | 5 | Register data policies, Choose a configuration section |
| Desktop | Registry Administrator | configuration/ingest-configurations/key-paths | 2 | Access to this Registry screen |
| Desktop | Registry Administrator | configuration/ingest-configurations/manage-subscription | 2 | Access to this Registry screen |
| Desktop | Registry Administrator | configuration/ingest-configurations/semantic-patterns | 2 | Access to this Registry screen |
| Desktop | Registry Administrator | configuration/ingest-configurations/templates | 2 | Access to this Registry screen |
| Desktop | Registry Administrator | configuration/intake-forms | 5 | Registration form definitions, Choose a configuration section |
| Desktop | Registry Administrator | configuration/outgest-configurations/templates | 2 | Access to this Registry screen |
| Desktop | Registry Administrator | configuration/outgest-configurations/topics | 2 | Access to this Registry screen |
| Desktop | Registry Administrator | configuration/registers | 5 | Register definitions, Choose a configuration section |
| Desktop | Registry Administrator | configuration/registry/details | 5 | Registry name and default settings, Choose a configuration section |
| Desktop | Registry Administrator | configuration/registry/languages | 5 | Registry languages, Choose a configuration section |
| Desktop | Registry Administrator | configuration/registry/themes/create | 7 | Create a Registry theme, Choose a configuration section |
| Desktop | Registry Administrator | configuration/registry/themes | 7 | Registry themes and colours, Choose a configuration section |
| Desktop | Registry Administrator | configuration/registry/users | 5 | Registry staff and roles, Onboard a Registry staff member, Independent Registry responsibilities |
| Desktop | Registry Administrator | incoming-messages | 2 | Access to this Registry screen |
| Desktop | Registry Administrator | myprofile | 2 | Registry page not found |
| Desktop | Registry Administrator | offline | 10 | Offline field capture, Prepare an offline collection device, Send an offline household interview, From capture to master record, Correct and resubmit a returned registration |
| Desktop | Registry Administrator | outgoing-messages | 2 | Access to this Registry screen |
| Desktop | Registry Administrator | dashboard | 6 | Registry overview, Start or track household registration, Published Registry records, Registration review queues, Change requests |
| Desktop | Registry Administrator | tasks/change-request | 2 | Access to this Registry screen |
| Desktop | Registry Administrator | tasks/intake-form | 2 | Access to this Registry screen |
| Desktop | Registry Administrator | intake-form/household | 1 | Registration review queues |
| Desktop | Registry Administrator | intake-form/individual | 1 | Registration review queues |
| Desktop | Registry Administrator | register/household | 1 | Household registry |
| Desktop | Registry Administrator | register/individual | 1 | Individual registry |
| Desktop | Registry Administrator | data-imports | 2 | Data Imports administration, Data Imports transfer history |
| Desktop | Registry Administrator | register/household-list | 2 | Registry page not found |
| 390 px mobile | First Reviewer | dashboard | 5 | Assigned Registry reviews, Start or track household registration, Registration review queues |
| 390 px mobile | MBR Officer | dashboard | 4 | Published Registry records for MBR officers, Start or track household registration, Published Registry records |
| 390 px mobile | Field Agent | dashboard | 4 | Registration and field work, Start or track household registration, Registration review queues |
| 390 px mobile | Second Reviewer | dashboard | 5 | Assigned Registry reviews, Start or track household registration, Registration review queues |
| 390 px mobile | First Reviewer | tasks/intake-form/household/{record} | 1 | Review a registration task |
| 390 px mobile | Second Reviewer | tasks/intake-form/household/{record} | 1 | Review a registration task |
| 390 px mobile | First Reviewer | tasks/change-request | 1 | My change request reviews |
| 390 px mobile | Second Reviewer | tasks/change-request | 1 | My change request reviews |
| 390 px mobile | Registry Administrator | dashboard | 6 | Registry overview, Start or track household registration, Published Registry records, Registration review queues, Change requests |
| 390 px mobile | Registry Administrator | register/household/{record} | 1 | Published household details |
| 390 px mobile | Registry Administrator | register/household/{record}/version-history | 1 | Record version history |
| 390 px mobile | Registry Administrator | register/household/{record}/change-request | 1 | Change requests for this record |
| 390 px mobile | Registry Administrator | register/individual/{record} | 1 | Published individual details |
| 390 px mobile | Registry Administrator | register/individual/{record}/version-history | 1 | Record version history |
| 390 px mobile | Registry Administrator | register/individual/{record}/change-request | 1 | Change requests for this record |
| 390 px mobile | Registry Administrator | intake-form/household/submission/{record} | 1 | Registration submission details |

## Mobile form and filter checks

| Help beside | Verified guide |
|---|---|
| Survey Consent & Enumeration | Survey consent and enumeration |
| Headship & Household Composition | Household headship and composition |
| Household Member Details | Household members and roster |
| Household Living & Dwelling Characteristics | Household living conditions |
| Household Income, Vulnerability to Shocks & Coping | Household income |
| Health Insurance Coverage | Health and vulnerability information |
| Household Assets & Possessions | Household assets and crops |
| Crops Grown | Household assets and crops |
| Additional asset records | Household assets and crops |
| Household programmes | Household programme information |
| Household Roster | Household members and roster |
| Survey sponsor | Survey sponsor |
| Consent to share data | Consent to share data |
| Respondent name | Survey respondent |
| State / FCT | State or Federal Capital Territory |
| Policy details | Create a register data policy |
| Local Government Area | Local Government Area |
| Filter rules | Check data policy filters |
| Latitude | Latitude and longitude |
| Filter preview | Check data policy filters |
| Location accuracy (metres) | Location accuracy in metres |
| Device capture time (UTC) | Device capture time |
| Location source | Location source |
| Nigeria administrative location | Household location |
| Household location | Household location |
| Ward | Ward |
| Longitude | Latitude and longitude |
| Locality / EA Code | Enumeration area |

## New guides

All 34 titles below link to their published documentation.

- [Access to this Registry screen](https://docs.g2p.wverve.in/topics/register/state-restricted/)
- [Registry page not found](https://docs.g2p.wverve.in/topics/register/state-missing/)
- [Registry page could not load](https://docs.g2p.wverve.in/topics/register/state-error/)
- [Start or track household registration](https://docs.g2p.wverve.in/topics/register/registration-start/)
- [Published Registry records](https://docs.g2p.wverve.in/topics/register/published-registers/)
- [Registry name and default settings](https://docs.g2p.wverve.in/topics/register/registry-details/)
- [Registry languages](https://docs.g2p.wverve.in/topics/register/registry-languages/)
- [Registry themes and colours](https://docs.g2p.wverve.in/topics/register/registry-themes/)
- [Create a Registry theme](https://docs.g2p.wverve.in/topics/register/theme-create/)
- [Register definitions](https://docs.g2p.wverve.in/topics/register/register-definitions/)
- [Configure a selected register](https://docs.g2p.wverve.in/topics/register/register-structure/)
- [Register section configuration](https://docs.g2p.wverve.in/topics/register/register-section/)
- [Sections on a register tab](https://docs.g2p.wverve.in/topics/register/register-tab/)
- [Register score definition](https://docs.g2p.wverve.in/topics/register/register-score/)
- [Registration form definitions](https://docs.g2p.wverve.in/topics/register/form-definitions/)
- [Tabs on a registration form](https://docs.g2p.wverve.in/topics/register/form-tabs/)
- [Sections on a registration form tab](https://docs.g2p.wverve.in/topics/register/form-sections/)
- [Registry data models](https://docs.g2p.wverve.in/topics/register/data-models/)
- [Register data policies](https://docs.g2p.wverve.in/topics/register/data-policies/)
- [Create a register data policy](https://docs.g2p.wverve.in/topics/register/policy-create/)
- [Registry approval policy configuration](https://docs.g2p.wverve.in/topics/register/approval-policies/)
- [Incoming data key paths](https://docs.g2p.wverve.in/topics/register/ingest-paths/)
- [Incoming subscription logs](https://docs.g2p.wverve.in/topics/register/ingest-subscriptions/)
- [Incoming semantic patterns](https://docs.g2p.wverve.in/topics/register/ingest-patterns/)
- [Incoming data templates](https://docs.g2p.wverve.in/topics/register/ingest-templates/)
- [Outgoing data templates](https://docs.g2p.wverve.in/topics/register/outgoing-templates/)
- [Outgoing Registry topics](https://docs.g2p.wverve.in/topics/register/outgoing-topics/)
- [Choose a configuration section](https://docs.g2p.wverve.in/topics/register/configuration-navigation/)
- [Onboard a Registry staff member](https://docs.g2p.wverve.in/topics/register/staff-onboarding/)
- [Independent Registry responsibilities](https://docs.g2p.wverve.in/topics/register/staff-responsibilities/)
- [Prepare an offline collection device](https://docs.g2p.wverve.in/topics/register/offline-device/)
- [Send an offline household interview](https://docs.g2p.wverve.in/topics/register/offline-delivery/)
- [Check data policy filters](https://docs.g2p.wverve.in/topics/register/policy-filters/)
- [Change requests for this record](https://docs.g2p.wverve.in/topics/register/record-change-list/)
