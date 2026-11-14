from pathlib import Path
import json
pack=json.loads(Path('knowledge/documentation-pack.json').read_text(encoding='utf-8'))['articles']
# Existing operational stages associated with each new article, plus specific visible labels.
rows=[
(['Find a record','Service overview'],'registry and register|register concepts'),
(['Submit for approval','Individual details','Household details'],'proposed.*approved|change request|edit details'),
(['Submit for approval','Individual details','Household details'],'workflow audit|audit trail'),
(['Individual details','Household details','Submit for approval'],'supporting documents|attached documents|record documents|document upload'),
(['Service overview','Submit for approval'],'incoming messages|ingestion|imported submissions'),
(['Individual details','Household details'],'version history|committed record history'),
(['Submit for approval','Service overview'],'intake form|intake submission|registry intake'),
(['Review consent','Service overview'],'consent.aware sharing'),
(['Find a record','Individual details','Household details','Service overview'],'duplicate candidates|deduplication|duplicate review'),
(['Role assignment','Account management','Service overview'],'operations.*configuration roles'),
(['Find a record','Individual details','Household details'],'export records|export history'),
(['Eligibility','Benefit calculation','Programme setup'],'eligibility.*entitlement rules|rule definitions'),
(['Enrollment','Disbursement','Programme setup'],'enrolment.*disbursement cycles|dual cycle'),
(['Enrollment','Disbursement','Eligibility'],'list verification|verify list|verification list'),
(['Enrollment','Programme setup'],'beneficiary list|controlled list|source.*list correction'),
(['Reconciliation','Disbursement'],'bank reconciliation|sponsor bank'),
(['Choose dashboard','Apply filters','Service overview'],'programme reports|program reports'),
(['Programme setup','Disbursement'],'program funds|programme funds|fund allocation'),
(['Programme setup','Enrollment'],'cycle manager'),
(['Record maintenance','Service overview'],'create individual|new individual|individual registrant'),
(['Household membership','Record maintenance'],'members|group membership'),
(['Record maintenance','Service overview'],'id types|identifier types'),
(['Household membership','Service overview'],'relationship types|relationships configuration'),
(['Record maintenance','Service overview'],'csv|import records|import a file'),
(['Eligibility','Programme setup'],'proxy means|pmt'),
(['Eligibility','Enrollment'],'verify eligibility|reassess eligibility|eligibility reassessment'),
(['Eligibility','Enrollment','Programme setup'],'deduplicate|duplicated|duplicate check'),
(['Enrollment','Eligibility'],'enrolment results|enrollment results|enrolled.*not eligible'),
(['Benefit calculation','Programme setup'],'prepare assessment|entitlement assessment|multi.stage approval'),
(['Programme configuration','Application administration'],'notification manager|programme notifications|program notifications'),
(['Prepare collection form','Submit and quality check','Collect field data','Service overview'],'odk import|json formatter|field mapping'),
(['Programme configuration','Application administration'],'data source|registry import'),
(['Service overview','Account management','Role assignment'],'applications|login providers'),
(['Maintain shared attributes','Service overview'],'reference code|code lists|datasets|attributes|values'),
(['Location reference data','Service overview'],'boundary change|geography changes|crosswalk'),
(['Maintain shared attributes','Location reference data'],'reference data.*review|change control|reference.*approval'),
(['Service overview','Maintain shared attributes','Location reference data'],'catalogue overview|reference.data navigation'),
(['Assigned tasks','Review evidence','Record decision','Service overview'],'quorum|approval patterns|stage modes'),
(['Service overview','Assigned tasks','Review evidence'],'policy version|approval policy|policies'),
(['Assigned tasks','Review evidence'],'overdue|sla|escalation'),
(['Record decision','Review evidence'],'self.approval|separation of duties|independent approver'),
(['Assigned tasks','Review evidence'],'reassign|reassignment|blocked task'),
(['Partner onboarding','Service overview'],'onboarding|partner lifecycle|public keys|rotate keys|key update'),
(['Integration access','Partner onboarding'],'signature verification|key integration|signing keys'),
(['Review consent','Service overview'],'effective scope|consent decision|validation result'),
(['Review consent','Service overview'],'partner policy|policy binding|data.share policy'),
(['Consent withdrawal','Review consent'],'revocation|withdrawal|expiry|consent lifecycle'),
(['Choose dashboard','Service overview'],'import dashboard|dashboard import'),
(['Find your service','Service overview'],'service journey|registration.*review.*application'),
(['Find your service','Service overview'],'persona.*permission|persona selector'),
(['Household details','Household members','Submit registration'],'registration readiness|prepare.*registration'),
(['Correct returned details'],'returned registration|reviewer feedback'),
(['Verification checks','Approve or return','Review queue'],'verification readiness|independent registration review'),
(['Recorded activity','Review queue','Verification checks'],'registration audit|status question'),
(['Programme application','Register household'],'application preparation|prepare.*application'),
(['Application status','Programme application'],'status meaning|application status'),
(['State record map','Location coverage'],'map intensity|state colours|state colors|records by state'),
(['Household location points','Location coverage'],'coordinate quality|coordinate provenance|synthetic coordinates'),
(['Choose service','Service overview'],'staff service|staff navigation'),
(['Sign-in troubleshooting','Choose service'],'access problem|access troubleshooting|session expired'),
(['Browse guidance'],'source.linked|source.aware|references'),
(['Edit guidance','Review and publication','Version history'],'content maintenance|maintain.*guidance'),
(['Ask local AI'],'ai source|check.*ai answer'),
(['Draft with local AI','Edit guidance'],'ai.suggested|drafting review'),
]
assert len(rows)==len(pack)==64
mapping=[]
for article,(contexts,topic) in zip(pack,rows):
 mapping.append(dict(slug=article['slug'],module=article['module'],stage=article['stage'],contexts=contexts,topic=topic,scope=article['scope']))
Path('knowledge/screen-guide-mappings.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
p=Path('knowledge/context.js');s=p.read_text(encoding='utf-8')
start=s.index(' const guideMappings=');end=s.index('\n function relatedGuides',start)
s=s[:start]+' const guideMappings='+json.dumps(mapping,ensure_ascii=False,separators=(',',':'))+';'+s[end:]
p.write_text(s,encoding='utf-8')
print('Mapped all',len(mapping),'added guides')
