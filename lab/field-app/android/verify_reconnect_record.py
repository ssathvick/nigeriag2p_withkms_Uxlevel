import sys,xml.etree.ElementTree as ET
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
q='''select d.xml from submissions s join forms f on f.id=s."formId" join submission_defs d on d."submissionId"=s.id and d.current=true where f."projectId"=1 and f."xmlFormId"='nsipa_field_household_demo' and d."instanceName"='SAMPLE SAMPLE-RECONNECT-03' and s."deletedAt" is null and s.draft=false;'''
r=ET.fromstring(query('odkdb',q).strip());get=lambda p:r.findtext(p,default=''); expected={'./visit/enumerator_id':'SAMPLE003','./location/state':'Plateau','./location/lga':'Jos North','./location/ward':'Gangare','./household/sample_reference':'SAMPLE-RECONNECT-03','./household/household_size':'3','./household/children':'1','./review/review_confirmation':'yes'}
assert all(get(k)==v for k,v in expected.items());print('PASS: server received the expected fictional record, location, household counts and demo review confirmation.')
