import json,subprocess,requests,re,base64
doc=json.load(open('/opt/openg2p-lab/commons-services-iam-staff-portal-api-openapi.json'))
print('IAM auth paths', [p for p in doc['paths'] if any(t in p for t in ['auth','login','provider'])])
def sql(db,q):
 secret=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','secret','commons-postgresql','-o','json']))
 pw=base64.b64decode(secret['data']['postgres-password']).decode()
 return subprocess.check_output(['kubectl','-n','nigeria','exec','svc/commons-postgresql','--','env','PGPASSWORD='+pw,'psql','-U','postgres','-d',db,'-Atc',q],text=True)
print('Databases',sql('postgres','select datname from pg_database where datistemplate=false'))
for db in ['iamdb','iam','commonsdb']:
 try:print(db,sql(db,"select table_name,column_name from information_schema.columns where column_name like '%url%' or column_name like '%endpoint%' or column_name like '%redirect%';"))
 except subprocess.CalledProcessError:pass
u='https://staff-portal.nigeriag2p.com'; r=requests.get(u+'/en')
for source in re.findall(r'<script[^>]+src="([^"]+)"',r.text):
 x=requests.get(u+source if source.startswith('/') else source)
 print('script',source,x.status_code,x.headers.get('content-type'),len(x.content))
