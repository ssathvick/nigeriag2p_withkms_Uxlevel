import json,sqlite3,datetime,shutil
from pathlib import Path
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab/registration');now=datetime.datetime.now().isoformat()
guides={
'Payment account details':{
 'purpose':'View and manage the payment-account mapping for your approved NSIPA household using the existing account service. Linking an account does not approve benefits or initiate payment.',
 'requirements':'Sign in as the beneficiary whose household is approved and synchronisation is complete. This installation supports fictional Example Bank Simulator accounts only.',
 'steps':'Review the currently linked account, or confirm that no account is linked.\nEnter a fictional account number starting LAB- followed by 4–32 letters, digits or hyphens. Select Link account or Update account and wait for the saved mapping.\nTo unlink a mapping, select Remove account, review the effect on future routing, then select Confirm removal. Cancel leaves the mapping unchanged.\nRefresh the screen to verify the result. Both NSIPA domains display the same household mapping.',
 'next_step':'Return to Benefits to review recorded benefits, or Complaints to report an account issue. An account mapping is not evidence of a completed payment.',
 'issues':'If registration is not approved and synchronised, use Registries to check its status. If another session changed the account, refresh before trying again. If a request times out, refresh and inspect the saved mapping before retrying. Never enter real bank details in this sandbox.'},
'Complaints and enquiries':{
 'purpose':'Submit a structured complaint for your own registered household and follow the case through the existing NSIPA staff review process.',
 'requirements':'Sign in with a beneficiary account that has a household registration. Use fictional information in this demonstration environment.',
 'steps':'Select the complaint reason: payment delay, account issue, registration correction or service quality.\nSelect Submit complaint once and wait for the case to appear in My cases. A retry of the same submission does not create a duplicate case.\nOpen the case to read its reference, current status, submission date, response deadline and resolution deadline.\nReturn to this screen or Notifications to check for staff acknowledgement, escalation or resolution.',
 'next_step':'Keep the case reference for follow-up. NSIPA staff handle the case through their existing grievance workspace; a beneficiary cannot acknowledge or resolve their own case.',
 'issues':'Register a household first if submission is unavailable. This installed workflow accepts a structured reason and does not accept attachments or free-text descriptions. After a network error, refresh My cases before starting a new submission.'},
'Notifications':{
 'purpose':'Read activity recorded for your NSIPA household registration, programme applications and complaint cases. These are in-portal records, not email or SMS delivery confirmations.',
 'requirements':'Sign in to the beneficiary portal. Only records associated with your own account appear.',
 'steps':'Review the unread count and open the relevant service if an activity needs follow-up.\nRead the complete message and timestamp. Application messages show the current status and the application creation time.\nSelect Mark as read for one item, or Mark all as read for the displayed unread items.\nReload the screen to confirm read status. The same account shares read status across both NSIPA domains.',
 'next_step':'Use Registries, Applications or Complaints to act on the underlying record. Marking a notification as read does not change the record or approve a payment.',
 'issues':'An empty list means there is no recorded activity available for this account. Refresh after a staff action. If the session expires, sign in again. Read state applies only to your own notifications.'},
'News and announcements':{
 'purpose':'Read news published through the existing NSIPA content review process. Draft and archived content is not shown.',
 'requirements':'Sign in to the beneficiary portal. Available article languages are English, Hausa, Yoruba and Igbo; language content remains subject to the existing editorial review process.',
 'steps':'Browse the published news titles and publication version numbers.\nSelect a title to expand the full announcement; select it again to collapse the article.\nEnter a search term to filter titles and full article text. Clear the search to show all available articles.\nChoose an article language to load the published text in that language.',
 'next_step':'Follow the guidance in the published article. Demonstration announcements describe sandbox activity and are not official benefit eligibility or payment decisions.',
 'issues':'If no result appears, clear the search or choose another article language. Only published news is available. Refresh after staff publish an update; do not treat an unavailable draft as a missing public announcement.'},
'Register household':{
 'purpose':'View the household registration linked to your NSIPA account and open the existing household registration service for submission or permitted corrections.',
 'requirements':'Sign in as the beneficiary. Use fictional household and member information in this demonstration environment.',
 'steps':'Open Registries to review the household reference, review status, synchronisation status and registered member names.\nIf no household exists, select Register household. Otherwise select Open household registration. The link opens the NSIPA registration service in the same domain family.\nSign in as the same beneficiary if prompted, complete the required household and member fields, confirm that the data is fictional, and submit through the existing registration form.\nFor returned records, correct the requested details and resubmit. Approved records remain subject to staff controls.\nReturn to Registries and refresh to verify the saved review and synchronisation status.',
 'next_step':'Wait for independent staff review. Once registration is approved and synchronisation is complete, manage a fictional payment account or apply to an available programme. Registration approval alone does not establish entitlement.',
 'issues':'The screen shows the installed household register, not a catalogue of unconfigured registries. If a record is pending review or synchronisation, allow the existing staff process to complete. If the linked registration service asks for sign-in, use the same beneficiary identity.'}}
db=sqlite3.connect(root/'intake.sqlite');db.row_factory=sqlite3.Row;updates={}
with db:
 for row in db.execute("SELECT * FROM km_articles WHERE module='beneficiary'").fetchall():
  a=json.loads(row['published']) if row['published'] else None
  if not a or a['stage'] not in guides:continue
  if row['draft']!=row['published']:raise RuntimeError('Unpublished guide changes require reconciliation: '+row['slug'])
  a.update(guides[a['stage']],scope='installed');version=row['version']+1;content=json.dumps(a);actor='system:nsipa-beneficiary-enablement';note='Enabled existing-backend beneficiary screens on both domain families.'
  db.execute('UPDATE km_articles SET draft=?,published=?,version=?,published_version=?,author=?,reviewer=NULL,review_note=?,updated=? WHERE id=?',(content,content,version,version,actor,note,now,row['id']))
  db.execute('INSERT INTO km_history(article,version,action,actor,at,content,note) VALUES(?,?,?,?,?,?,?)',(row['id'],version,'maintenance_publication',actor,now,content,note));updates[row['slug']]=a
for p in [src/'knowledge-seed.json',src/'knowledge/seed.json',root/'knowledge-seed.json']:
 d=json.loads(p.read_text());d['articles']=[{**a,**updates.get(a['slug'],{})} for a in d['articles']];p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
for p in [src/'phase1_cms.py',root/'phase1_cms.py']:
 if p.exists():p.write_text(p.read_text().replace('NigeriaG2P','NSIPA'))
print('Updated',len(updates),'published guidance records, including citizen guidance.')
