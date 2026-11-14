import sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
q='''select count(*) from submissions s join forms f on f.id=s."formId" join submission_defs d on d."submissionId"=s.id and d.current=true where f."projectId"=1 and f."xmlFormId"='nsipa_field_household_demo' and d."instanceName"='SAMPLE SAMPLE-RECONNECT-03' and s."deletedAt" is null and s.draft=false;'''
print('Matching server submissions:',query('odkdb',q).strip())
