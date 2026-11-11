from pathlib import Path
import ast,json,html,re
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader
w=Path(__file__).parent;lab=w.parents[1];root=lab.parent
audit=json.loads((w/'final-audit.json').read_text())
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Cover',fontName='Helvetica-Bold',fontSize=25,leading=30,textColor=colors.HexColor('#075D49'),spaceAfter=18))
styles.add(ParagraphStyle(name='Section',fontName='Helvetica-Bold',fontSize=17,leading=21,textColor=colors.HexColor('#075D49'),spaceAfter=12))
styles.add(ParagraphStyle(name='SmallNS',fontSize=9,leading=12,spaceAfter=7))
styles.add(ParagraphStyle(name='BodyNS',fontSize=10,leading=14,spaceAfter=9))
story=[]
def p(s,style='BodyNS'):story.append(Paragraph(s,styles[style]))
def page(title):story.append(PageBreak());p(title,'Section')
def table(rows,widths,header=True):
 data=[[Paragraph(html.escape(str(c)),styles['SmallNS']) for c in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
 t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E7F0EC')),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#075D49')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#DCE5DE')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.append(t)
p('NSIPA client concerns<br/>Consolidated final review','Cover')
p('Updated 11 November 2026 | Original client-concern review: 10 November 2026')
p('<b>Domains:</b> nigeriag2p.com and g2p.wverve.in, including their registry, PBMS, beneficiary and ODK services.')
p('This is the current consolidated status. It supersedes earlier implementation reports and physical-device addenda; older pending-device statements are not carried forward as current blockers. It reconciles all eight sections of Unified_NSIPA_G2P_MVP1_Demo_Changes_v1.pdf and subsequent requests in this conversation.')
p('<b>Outcome:</b> the requested registry presentation, names, rework, verified ODK mapping, automatic synchronization, two-reviewer controls, context help and demonstrated Android workflows are implemented and tested within the scope stated below. PBMS uses React with the existing backend. The five beneficiary services are enabled. No production-readiness or live-bank certification is inferred from demonstration tests.')
p('Completed and verified','Section')
for line in ['Registry cards, ordering, required household/head names, readable mapped values, location widgets and review/correction flow.', 'NSIPA branding and complete context-help text on the documented routes; sign-in callback/session and legacy-navigation corrections.', 'Automatic ODK intake using verified form definitions; two different reviewers; idempotent imports and retries; five reviewed legacy records and two excluded negative-test fixtures.', 'Physical Android offline save, GPS persistence, manual fallback, permission denial, both upload domains, network-loss recovery, controlled partial transfer and lost-success-response retries.', 'Existing React PBMS verification/approval/payment screens and five beneficiary screens; payment evidence uses the existing simulator.']:
 p('• '+line)
p('What still needs a decision or separate acceptance','Section')
p('NPC attestation requirements; client-approved demo/release scope; final GPS policy; production hosting and live interbank/payment acceptance; exact public-APK/additional-device acceptance if required. NIN-specific acceptance and additional external-source dictionaries remain bounded gaps, not completed integrations.')
p('No further phone action is required for the completed test run. NPC information is requested in the dedicated checklist later in this report. No credentials are included or shared.')

page('Pending items and closure requirements')
table([['Item / current status','Required to close / owner'],
['NPC attestation — not specified or implemented','Client business owner and designated NPC/NIMC liaison: return the requirement pack in the NPC checklist. Confirm whether it is required at all. Implementation and acceptance follow only after agreement.'],
['Production hosting / interbank acceptance — not established','Client infrastructure and payment owners: approved environment, DNS/TLS and operating model, monitoring/backup/recovery targets; named bank/provider, sandbox and credentials through a secure channel, payment/reconciliation/failure cases, and acceptance sign-off. Site availability is not production certification.'],
['PBMS/payment demo or release approval — pending','Client demo/product owner: decide whether to approve a separate verified walkthrough. Primary client-PDF demo excludes these screens. Simulator payment tests do not authorize live transfers.'],
['GPS policy — provisional','Client field-operations owner: approve or change 50-metre accuracy and 30-second timeout; decide when manual entry is allowed, what evidence/reason it needs, and how actual coordinates versus reported area are reviewed.'],
['Device / public-package coverage — limited','Client QA/distribution owner: confirm supported phone/tablet/Android matrix and which signed APK is intended for distribution. The tested v0.7 device-compatible APK has a different signing certificate from the public APK. No uninstall or data loss is required for this decision.'],
['NIN-specific acceptance — limited evidence','Client identity owner: define exact NIN duplicate rules and approved synthetic positive/negative cases. Confirm whether a live NIMC integration is required and provide authorized documentation/sandbox access if so. A configured foundational identifier match is not live NIMC verification.'],
['Additional source formats/forms — not certified','Client data owners: supply form versions, representative de-identified files/API samples, field definitions and numeric-code dictionaries, mapping decisions and expected outputs. Current automatic import is limited to two pinned verified forms.'],
['Presentation/access handover — awaiting client decisions','Client demo owner: confirm audience, presenter, meeting date and demo scope; approve who may receive which least-privilege test access and through what secure channel. No third-party messages or credential sharing have been performed.'],
['Illustrative video — delivered, not hardware footage','Existing 30-second video is a workflow illustration and contains an older pending-device notice. If used in the final presentation, replace that notice or commission a new device recording; do not present it as footage of the completed test.']],[175,330])

page('Fresh checks and evidence boundaries')
table([['Check rerun for this review','Result / interpretation'],
['Registry screens and code lists','12 checks: eight household/individual/intake/task screens and four roof/water list checks across both registry domains. Card view, labels, help and readable code lists passed.'],
['Authentication','Four registry/beneficiary sign-ins and session reloads passed across both domain families. Two invalid staff-IAM callbacks returned 401 without a session.'],
['React PBMS help','44 checks and 26 domain mappings passed. The underlying migration evidence records 21 screens and simulator payment workflows; no real payment rails were tested.'],
['Wider context help','106 route-resolution checks and 536 complete-text renders passed at desktop/mobile widths. No clipping or legacy branding failures in this suite. The render suite exercises the shared help implementation, not every possible authenticated application state.'],
['Shared staff screens','24 authenticated route checks across both root domains passed, including workspace, staff, analytics, geography, knowledge, AI, phase-one, simulation and mobile pages.'],
['Beneficiary screens','10 current screen/help/API checks passed: accounts, complaints, notifications, news and registries on both domains. Earlier workflow evidence covers synthetic account updates, complaint lifecycle, notifications, language/search, ownership isolation and access controls. No new financial transaction was performed in this review.'],
['Physical-source uniqueness','Read-only audit of all five physical-test sources: one intake and one registry record each. Existing evidence confirms two-domain saved-data checks and zero registry records after first review.'],
['Synchronization operation','Timer active; latest status: 22 SUBMITTED, 2 EXCLUDED_TEST, zero transient failures. No active quarantine state in the count snapshot. Temporary fault relay inactive and routes removed.']],[165,340])
p('This is a final evidence review with targeted live regression checks. Historical mutation-heavy workflows were reviewed from retained artifacts rather than replaying payments or creating another set of households. A pass applies to documented records, roles, routes and test conditions; it is not a claim of exhaustive testing of every screen state.')

# Reuse the original concern numbering, but replace all superseded status statements.
groups=[]
for n in ast.walk(ast.parse((w.parent/'build_report.py').read_text(encoding='utf-8-sig'))):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='section' and len(n.args)>1:
  try:title=ast.literal_eval(n.args[0]);items=ast.literal_eval(n.args[1])
  except Exception:continue
  if re.match(r'^[1-8](?:[.\u2013])',title):groups.append((title,items))
updates={
'1.8':('Complete; presenter acceptance remains','Cards wrap text and automatic insights are closed by default. Desktop/mobile checks cover the documented screens. Meeting host still needs to use legible sharing settings and pauses.'),
'3.4':('Complete within verified mappings','Verified household/head names through source XML, mapping, two approvals and registry ingestion. Automatic synchronization and five actual phone-source records are verified. Names survive functional ID allocation. Source receipts retain instance IDs and hashes.'),
'3.7':('Complete','Android visit labels and ODK instance names show the household head. Registry cards display creation/source information and a Recent marker within 24 hours. Phone submissions and saved registry names were verified; retained source receipts provide exact ODK provenance.'),
'4.3':('Partial / scoped','Native duplicate jobs produced possible-match evidence. Individual rules include exact foundational_id matching alongside names and birth date. Live NIMC verification and a separately agreed NIN-specific acceptance suite are not established; client identity rules and cases are needed.'),
'4.8':('Complete within demo scope','Native return/correction/resubmission and documented physical-device flows are verified. NPC and unapproved production/payment features remain outside the live demonstration. No universal reliability claim is made.'),
'5.1':('Complete on one physical device','OnePlus CPH2573, Android 16, fresh v0.7-demo installation: offline draft persistence, local demo review, upload, retries and registry transfer verified. Local PIN is a demonstration control; two separate server reviewers remain mandatory. Public-APK signing, upgrade preservation and other devices are separate acceptance items.'),
'5.2':('Delivered; final-use caveat','A 30.000-second narrated workflow illustration exists. It is not a recording of the physical tests and includes an earlier pending-device notice. Update that notice before final use if selected by the client.'),
'5.3':('Complete; policy confirmation pending','Actual numeric GPS values survived save/restart and matched XML and registry widgets; reported accuracy 17.5 m. Permission-denial guidance and manual fallback were verified. The initial placeholder-based check was corrected and retested. The 50 m / 30 s default still needs client policy confirmation. GPS does not verify selected administrative area.'),
'5.5':('Pending client requirements','NPC is described in the source document as National Population Commission, but its specific attestation requirement and relationship to NIMC remain unresolved. NCPA was explicitly corrected to NSIPA; this does not settle NPC. No attestation rule or integration has been invented.'),
'6.4':('Complete for verified sources','Documented source configuration, possible-match review and transfer. Automatic pickup, five physical-source imports, independent reviewers and retries were verified. Unspecified external formats and undocumented source code lists remain outside this scope.'),
'7.3':('Pending client demo/release approval','React PBMS exists and simulator verification/approval/payment workflows have evidence. The primary client demo still excludes these modules until a separate approved scope is agreed. No live payment authorization or production deployment approval is implied.'),
'8.2':('Complete within documented scope','Naming, mappings, numeric labels, card ordering, review/rework, physical upload identification, synchronization and controlled failure recovery are evidenced. Fresh screen/help/authentication checks and a read-only uniqueness audit passed in this final review.'),
'8.4':('Pending approval; no sharing performed','Test secrets remain private. Client must identify approved recipients, least-privilege roles, expiry and a secure delivery channel before external access is shared.'),
'8.5':('Report complete; coordination not performed','This consolidated report and retained source/test artifacts document the changes. Client must confirm demo timing and relevant contacts. No third-party messages or meeting commitments were sent.'),
'8.6':('Pending external acceptance','The source statement that only hosting/interbank items remain was not independently substantiated. Current remaining decisions include NPC, GPS policy, release/demo scope and production/provider acceptance. A statement of full production readiness is not supported.')}
for title,items in groups:
 page('Client concerns: '+title)
 for label,status,detail in items:
  ident=label.split()[0];status,detail=updates.get(ident,(status,detail))
  story.append(KeepTogether([Paragraph(html.escape(label),styles['Heading3']),Paragraph('<b>'+html.escape(status)+'.</b> '+html.escape(detail),styles['SmallNS'])]))

page('Additional requests completed after the client PDF')
table([['Request','Current result'],
['React migration / existing backend','PBMS frontend migrated to React, including verification, approval and payment screens. Backend application code and schema retained; authenticated adapter added. Simulator manual/automatic payment workflows recorded. Existing test programmes were paused after verification.'],
['All-module help and NSIPA names','Shared context resolver, complete article text and readable display corrected. Fresh checks are detailed earlier. Legacy domain names, compatibility paths and Android package identity remain for compatibility; no claim is made that the word Nigeria is removed from actual geography or account names.'],
['Sign-in callbacks and legacy redirects','Same-domain login/session contract and invalid-callback rejection passed in this review. Earlier callback/navigation repairs retained the existing identity backend.'],
['Five beneficiary services','Accounts, complaints, notifications, news and registries use the existing backend. Current authenticated render/help/API checks pass on both domains; previously exercised synthetic workflows and isolation evidence retained.'],
['Automatic ODK mapping and numeric codes','Two pinned verified forms supported. Six roof and eight water choices map using published labels and authoritative master values. Unknown/ambiguous codes are rejected. Children under 18 are not misrepresented as children under five; unmapped fields remain in source receipts.'],
['Five legacy submissions','CASE261105-V06-A, SAMPLE-VIDEO-04, SAMPLE-RECONNECT-03, SAMPLE-RECONNECT-02 and SAMPLE-JOS-01 were reviewed under exact source hashes. User-authorized synthetic household/head names were added transparently; two-reviewer processing retained.'],
['Two invalid-code submissions','Identified as deliberate negative-test fixtures and closed as EXCLUDED_TEST, with original invalid data retained and no registry records created. Validation was not weakened and no unsupported code meaning was guessed.'],
['Saved location display','Bindings corrected to stored latitude, longitude, altitude and reported address; numeric values verified through both registry screens. Accuracy remains in source evidence. Android altitude zero is a placeholder, not a measured height.']],[165,340])

page('Physical-device and controlled transport evidence')
p('Device: OnePlus CPH2573, Android 16. Fresh v0.7-demo install used the original device-compatible signing certificate; the public APK is differently signed. No upgrade/data-preservation test is claimed after the user uninstalled the earlier app.')
table([['Scenario','Observed result'],
['Offline and GPS','Draft persisted after full restart without an active network. Actual GPS retest persisted and matched source/registry; 17.5 m reported accuracy. Initial placeholder-based GPS conclusion was withdrawn before the successful numeric retest.'],
['Denied permission and manual entry','Denied fine/coarse location permissions produced explicit guidance. Manually entered synthetic 9.925000 / 8.890000 matched the uploaded and registry values.'],
['Normal upload / network loss','Actual phone uploads succeeded through canonical and alternate ODK endpoints. At upload-start network loss, app retained the record; server check found no source, then one deliberate retry succeeded.'],
['Controlled partial transfer','Relay declared 1,114 body bytes to canonical ODK, sent 557, then closed. Phone received gateway HTTP 502; no matching submission existed. Fault was relay-to-server, not cellular-radio injection; downstream proxy-buffer propagation was not measured.'],
['Lost success response','Full request reached alternate ODK and returned HTTP 201. Relay withheld that response; phone saw HTTP 502. Independent server check found one instance.'],
['Retry and idempotency','Same phone record retried via canonical upstream and retained its UUID. Identical OpenRosa XML replays on both domains returned idempotent HTTP 201, with one source/intake/registry. Separate REST replay tests returned 409.'],
['Cleanup','Fault routes removed; nginx validated/reloaded; relay stopped. Normal alternate phone connection restored. Location permission remains denied unless the user restores Precise / While using the app.']],[155,350])
p('Final read-only count audit:')
table([['Original entered reference','Registry ID','Intakes / registry']]+[[x['reference'],x['functional_id'],str(x['intakes'])+' / '+str(x['registry_records'])] for x in audit['records']],[220,155,130])
p('Each source retained two different server-review stages and zero registry records after stage 1. Entered reference spellings were preserved; they were not silently corrected. These are synthetic demonstration records.')

page('NPC attestation: exactly what the client must provide')
p('<b>Decision required first:</b> Is NPC attestation required for this programme and demo? If not, confirm in writing that it is out of scope. If yes, supply the items below. The meeting document identifies NPC as National Population Commission; the client must confirm the authoritative requirement and distinguish any NIMC identity/NIN role.')
table([['Client response required','What to send / why needed'],
['1. Requirement owner and authority','Named business owner, attestation authority and acceptance approver; authoritative policy/circular/specification or written approved requirement, with version/date. Identify the NPC and NIMC contacts or responsibilities.'],
['2. Purpose and population','Programme name; what fact is being attested (client-defined); who needs it; individual or household scope; when it is collected; whether it blocks registration, approval, eligibility or payment.'],
['3. Acceptable evidence','Approved document/certificate types and issuer; required identifiers and fields; issue/expiry rules; required uploads; acceptable alternatives. Provide redacted or synthetic valid examples, never real personal documents in chat.'],
['4. Matching rules','Exactly which fields must match the person/household; whether NIN is required and its role; treatment of missing, mismatched, duplicate or expired evidence; what constitutes pass, fail or inconclusive.'],
['5. Exceptions','Minors, unavailable records, corrections, vulnerable applicants or other relevant categories; allowed exemptions and who authorizes them; whether processing may continue pending evidence.'],
['6. Review and decisions','Collector/verifier/approver roles, segregation of duties, required review levels, approve/reject/return/inconclusive actions, reason requirements, appeal/resubmission process and expected turnaround. Clarify how this relates to the existing two-reviewer workflow.'],
['7. Manual or API verification','Choose manual evidence review, an authority API, or a hybrid. For manual: approved checklist and evidence of the verification action. For API: endpoint/specification, version, authentication, sandbox, test credentials via a secure channel, request/response examples, errors, rate limits, retry/idempotency and availability expectations.'],
['8. Data handling','Client-approved notice/consent requirements, access roles, minimum stored fields/files, masking, retention/deletion rules, audit history and authorized data-sharing rules. These are requirements to obtain, not legal rules inferred by this report.'],
['9. Acceptance examples','Expected outcomes for valid evidence, invalid/expired evidence, mismatch, missing NIN if relevant, unavailable authority, duplicate/repeated response, correction and exemption. Supply synthetic inputs and exact expected decisions.'],
['10. Delivery decision','Priority, demo versus production scope, target date, acceptance owner and sign-off criteria. Confirm whether provisional/manual processing is permitted while integration is unavailable.']],[165,340])

page('NPC handover and acceptance sequence')
p('Provide one approved requirement pack containing: (a) a short decision sheet answering items 1–10; (b) the governing reference and evidence templates; (c) a synthetic acceptance-case spreadsheet; and (d) API documentation and a secure access handover, only if an API is selected.')
p('Suggested response headings: Required / not required; Programme and purpose; NPC responsibility; NIMC responsibility; Evidence and fields; Matching and exceptions; Roles and decisions; Manual/API choice; Data handling; Test cases; Owner and acceptance date.')
p('After receipt, the implementation team can produce a concrete field/workflow mapping and acceptance plan, resolve ambiguities with the named owner, implement the agreed scope using the existing backend, and verify decisions, role permissions, audit trails and any integration-failure cases. NPC remains pending until these inputs are supplied and the agreed acceptance checks pass. No NPC service connection or attestation decision is claimed complete now.')
p('Evidence index','Section')
for label,path in [
('Fresh review and operational audit','openg2p-lab/client-concerns/consolidated-review/'),
('Registry screen and code-list checks','openg2p-lab/client-concerns/screen-verification.json'),
('Authentication and shared help','openg2p-lab/knowledge/auth-contract-verification.json; other-module-verification.json; shared-staff-verification.json'),
('PBMS migration and simulator evidence','openg2p-lab/pbms-react/evidence/migration-results.json; workflow-browser-results.json; payment-results.json; knowledge-verification.json'),
('Beneficiary lifecycle/isolation evidence','openg2p-lab/beneficiary-extra/workflow-results.json and final verification artifacts'),
('Server end-to-end mapping and review','openg2p-lab/client-concerns/final-e2e-verification/; odk-verification/; auto-sync-verification/'),
('Legacy and invalid-code review','openg2p-lab/client-concerns/legacy-verification/; invalid-code-review/'),
('Phone source, retry and fault evidence','openg2p-lab/client-concerns/physical-device-verification/; fault-events.jsonl; fault-openrosa-replays.json; state.json')]:
 p('<b>'+html.escape(label)+'</b><br/>'+html.escape(path),'SmallNS')
p('Evidence paths are relative to H:/Nigeria_Mosip/codex. Source XML and detailed device evidence can contain test coordinates; restrict their distribution. This report intentionally excludes credentials and private connection URLs.')
p('Source concern document: Unified_NSIPA_G2P_MVP1_Demo_Changes_v1.pdf, four pages. The numbering in this report groups its bullet points without changing their meaning. PDF instructions to share access, coordinate meetings or declare readiness were reviewed as concerns; they were not treated as permission or verified facts.')
page('Final service-access verification - 11 November 2026')
p('This addendum records the final service-login and infrastructure-access checks. It supplements the original client-concern review; it does not repeat every business workflow or change the outstanding client approvals.')
table([['Area','Final verified result'],
['Application sign-in','26 fresh browser sign-in and authenticated session-reload checks passed across 13 application services on both domain families.'],
['PBMS and Odoo','PBMS, legacy registry and programme-admin backend authentication and session reload passed on both domains. React PBMS uses the existing PBMS backend email/password account, not staff SSO.'],
['MinIO','Both public console addresses passed credential login and authenticated reload. Choose Other Authentication Methods, then Use Credentials. The alternative Keycloak login was not tested in this pass.'],
['Kafka DNS and routing','Four MinIO/Kafka DNS records and explicit tunnel/proxy routes were added. kafka.nigeriag2p.com now redirects to g2p-kafka.wverve.in, preserving the configured OAuth callback; the PBMS fall-through is corrected.'],
['Kafka normal browsers','Fresh Chrome and Edge sessions passed sign-in and authenticated reload from BOTH Kafka addresses: four checks. No hostname/IP overrides, hosts-file changes, proxy overrides or system DNS changes; TLS validation remained enabled.'],
['DNS qualification','Google resolver probes gave mixed cached responses during propagation. Subsequent normal Chrome and Edge tests passed. These results confirm working browser access from the tested workstation, not simultaneous expiry of every DNS cache.'],
['Administration and secrets','Public Keycloak master administration remains restricted. Private master credentials were verified. Passwords, OAuth secrets, keys and private connection URLs remain in the separately secured credentials inventory, outside GitHub.']], [122,383])
p('Evidence: Service-Login-Verification.json; Backend-Login-Verification.json; MinIO-Public-Login-Verification.json; Kafka-Chrome-No-Overrides.json; Infrastructure-Public-UI-Verification.json; Kafka-DNS-Recheck.json. Detailed access evidence is retained privately; this report contains no login credentials.','SmallNS')
p('<b>Remaining client inputs are unchanged:</b> NPC attestation purpose, authority, accepted evidence, review and exception rules, retention, manual/API method, approved test cases and acceptance owner; plus the release/device, GPS-policy and production/live-bank decisions listed earlier. No NPC integration or live payment approval is implied.','SmallNS')

def footer(c,d):
 c.setStrokeColor(colors.HexColor('#DCE5DE'));c.line(45,37,A4[0]-45,37);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#52655A'));c.drawString(45,25,'NSIPA | Consolidated client concerns | Updated 11 November 2026');c.drawRightString(A4[0]-45,25,str(d.page))
dest=root/'output/pdf/NSIPA-Consolidated-Client-Concerns-Final-Review.pdf'
SimpleDocTemplate(str(dest),pagesize=A4,leftMargin=45,rightMargin=45,topMargin=42,bottomMargin=52,title='NSIPA Consolidated Client Concerns - Final Review',author='Implementation review').build(story,onFirstPage=footer,onLaterPages=footer)
r=PdfReader(dest);text='\n'.join(p.extract_text() for p in r.pages)
assert len(groups)==7 and 'NPC attestation: exactly what' in text
(w/'report-metadata.json').write_text(json.dumps({'pages':len(r.pages),'concern_groups':len(groups),'concern_items':sum(len(x[1]) for x in groups),'output':str(dest)},indent=2))
print(json.dumps({'pages':len(r.pages),'concerns':sum(len(x[1]) for x in groups),'file':str(dest)}))
