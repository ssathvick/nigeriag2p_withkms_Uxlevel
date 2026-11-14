from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter
root=Path(__file__).resolve().parents[3]
work=Path(__file__).parent
state=json.loads((work/'state.json').read_text())['PHON320261110-01']
assert state['approved'] and len(state['domains'])==2
out=root/'output/pdf'
styles=getSampleStyleSheet(); story=[]
def p(text,style='BodyText'):
 story.extend([Paragraph(text,styles[style]),Spacer(1,10)])
p('NSIPA physical-device test update','Title')
p('10 November 2026 | This update supersedes device-pending statements in the attached earlier report. The original report follows for historical implementation evidence.')
p('Completed checks','Heading2')
p('OnePlus CPH2573, Android 16: fresh installation of v0.7-demo using the original device-compatible signing certificate. This is not an upgrade/data-migration test or a test of the differently signed public APK. Offline draft persistence was observed after force-stop and relaunch. Local demo approval was saved with no active network.')
p('After reconnection, the device remained approved-demo. One deliberate foreground upload returned HTTP 201. ODK contains the phone submission with actual reference PHON320261110-01; the originally planned reference PHONE-20261110-01 was not entered exactly. The pre-upload exact-reference search therefore does not independently prove absence of this differently named source.')
p('Automatic synchronization created one intake. Two separate reviewer sessions approved stages 1 and 2 through opposite domain aliases. Registry count was zero before approval and after stage 1, then one after stage 2. Saved source-mapped fields and the resulting household screen were checked through register.nigeriag2p.com and g2p-register.wverve.in. No repeated device upload was attempted.')
p('Registry record: '+state['functionalId']+'. Source instance: '+state['instance']+'.')
p('GPS correction and remaining device tests','Heading2')
p('Historical correction: GPS was initially NOT passed. The earlier check mistakenly interpreted EditText placeholder labels as saved numeric values. The actual uploaded XML contains no coordinates, and both registry aliases correctly retain null coordinates. That first sample did not verify GPS. The new sample described below completes the numeric persistence and transfer checks.')
gps=json.loads((work/'state.json').read_text())['PHONE-GOS-02']
assert gps['approved'] and len(gps['domains'])==2
p('GPS retest passed','Heading2')
p('The new physical sample PHONE-GOS-02 (enumerator PHONE-GPS-02) contains real numeric latitude and longitude. They survived save and full restart and match the uploaded XML exactly. Source-reported accuracy is 17.5 metres; altitude is the app placeholder zero, not a measured altitude. GPS measures the phone location and does not validate its fictional selected Nigerian administrative area.')
p('The timer imported this sample automatically. Two distinct reviewers approved it; registry count remained zero after stage 1 and became one after stage 2. All mapped values and both coordinate widgets passed checks on both registry domains. Registry record: '+gps['functionalId']+'. Both phone visits retain sent status after restart.')
p('Four controlled REST replays of the actual two phone XML submissions, one per source per ODK domain, returned 409 duplicate responses. These are server replay tests of physical source data, not interrupted mobile-network tests. Each source retains one intake and one registry record.')
allstate=json.loads((work/'state.json').read_text())
manual=allstate['PhPHONE-FALLBACK-03']; retry=allstate['SYNTHETIC-RETRY-04']
assert all(x['approved'] and len(x['domains'])==2 for x in [manual,retry])
from reportlab.platypus import PageBreak
story.append(PageBreak())
p('Remaining device tests completed','Heading1')
p('Location permission denial: Android fine and coarse permissions were denied. Requesting location displayed Location permission denied and instructed manual entry or granting permission in settings. The message was observed directly and saved as evidence.')
p('Manual fallback: entered synthetic latitude 9.925000 and longitude 8.890000 with permission denied. These values survived saving and review and matched the uploaded XML and registry values on both domains. Source accuracy and altitude were zero placeholders, not measured GPS data. Original entered reference PhPHONE-FALLBACK-03 was preserved.')
p('Alternate-domain physical upload: provisioned the dedicated sample connection privately to g2p-odk.wverve.in, validated its form list, and uploaded from the actual Android app. HTTP 201 and a unique ODK receipt were observed. The attempted app-background interruption completed too quickly and was not counted as an interrupted test.')
p('Network-loss recovery: used the separate sample SYNTHETIC-RETRY-04, enumerator PHONE-RETRY-04. Disabled mobile-data failover and disconnected Wi-Fi concurrently with upload initiation. The app showed Upload interrupted or failed; server receipt may be unknown. Check the server before retrying. ODK had zero matching receipts, and the visit remained approved-demo. Restored Wi-Fi and mobile data, then made one deliberate retry. It returned HTTP 201 with one source instance.')
p('Scope: this proves handling of network loss at upload initiation and a checked successful retry. It does not establish precisely how many bytes were transmitted before disconnection, nor simulate a server commit with a lost response. Earlier server idempotency checks cover duplicate delivery independently.')
p('Both new sources were automatically imported. Independent reviewers completed stages 1 and 2; registry count stayed zero after stage 1 and became one after stage 2. Saved mapped fields, manual coordinate display, and NSIPA naming checks passed on both registry domains. Manual record: '+manual['functionalId']+'. Retry record: '+retry['functionalId']+'.')
p('Eight REST replays of the four physical-source XML records across both ODK aliases were rejected with HTTP 409. Each source retained one intake and one registry record. These controlled server replays are distinct from the physical network-loss test.')
p('No further phone input is needed for this test run. Location permission remains denied by the test; the user may restore While using the app and Precise before future GPS collection. Wi-Fi and mobile data were restored to enabled. The app remains configured to the alternate domain. Broader device coverage and the differently signed public APK remain outside this single-device run.')
story.append(PageBreak())
p('Controlled mid-transfer and lost-response tests','Heading1')
fault=allstate['PHONE-FAULT-05'];assert fault['approved'] and len(fault['domains'])==2
p('A temporary localhost relay, reachable only through a private test path, accepted only PHONE-FAULT-05. The unchanged Android app sent the actual synthetic sample over HTTPS. Normal submission routes were retained. These are controlled relay-to-ODK transport faults, not a radio-level cellular simulation.')
p('Mid-transfer: the relay declared a 1,114-byte request body to odk.nigeriag2p.com, sent 557 bytes, then closed before completing it. The phone received gateway HTTP 502 and retained the approved sample. A subsequent ODK query found no matching source instance. The relay log records exact sent-byte counts; it does not prove how far incomplete bytes propagated past downstream proxy buffering.')
p('Lost response: the next attempt sent the complete body through g2p-odk.wverve.in. ODK returned HTTP 201, then the relay discarded that success response. The phone saw HTTP 502 and remained retryable, while the independent server check found one source instance.')
p('Checked retry: after confirming the receipt, a deliberate retry from the same phone record through the canonical upstream returned HTTP 201. The UUID stayed identical. Further identical XML submissions through each domain using OpenRosa also returned HTTP 201 without creating another instance. OpenRosa idempotent acknowledgements differ from the REST duplicate-rejection HTTP 409 tests documented earlier.')
p('Automatic synchronization produced one intake. Independent stage-1 and stage-2 reviewers approved it; registry count remained zero after stage 1 and became one after stage 2. Both registry domains returned the same mapped data and record. Registry internal identifier: '+fault['mapping']['payload']['internal_record_id']+'. ODK instance: '+fault['instance']+'.')
p('The temporary routes were removed, nginx configuration validated and reloaded, and the relay stopped. The phone connection was restored to the normal alternate ODK endpoint. No additional phone action is needed. These results complete the requested controlled failure scenarios; they do not certify all carrier, operating-system, or public-APK combinations.')
p('NPC attestation remains awaiting client requirements','Heading2')
p('Provide the attestation purpose and program stage, confirmed issuer, required evidence and fields, exemptions, reviewer roles and decisions, retention rules, and approved valid/invalid examples. Confirm manual review versus API integration; if API-based, provide specifications and secure sandbox access. Confirm the acceptance owner and the provisional GPS accuracy policy. No NPC attestation implementation is claimed complete.')
add=work/'physical-update.pdf'; SimpleDocTemplate(str(add),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=40,bottomMargin=40).build(story)
w=PdfWriter()
for source in [add,out/'NSIPA-Client-Feedback-Report-Final-End-to-End.pdf']:
 for page in PdfReader(source).pages:w.add_page(page)
dest=out/'NSIPA-Client-Feedback-Report-Transfer-Faults-Verified.pdf'
with dest.open('wb') as f:w.write(f)
print(dest)
