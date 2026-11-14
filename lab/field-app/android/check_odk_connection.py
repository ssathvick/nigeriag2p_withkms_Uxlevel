import sys,requests
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
q='''select s.token from sessions s join actors a on a.id=s."actorId" join field_keys f on f."actorId"=a.id where a."displayName"='OnePlus sample-only upload' and a."deletedAt" is null and f."projectId"=1 order by s."createdAt" desc limit 1;'''
token=query('odkdb',q).strip(); assert token and '\n' not in token
url='https://odk.nigeriag2p.com/v1/key/'+token+'/projects/1/formList'
r=requests.get(url,headers={'X-OpenRosa-Version':'1.0'},timeout=20,allow_redirects=False)
print('App User form-list response:',r.status_code,'sample form present:', 'nsipa_field_household_demo' in r.text)
