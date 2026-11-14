import requests,concurrent.futures
hosts=['pbms','register','registry','staff-portal','beneficiary','awe','master-data-ui','partner-management','consent-manager','odk','superset','portal-admin','iam-staff-ui','staff-iam','staff-register','partner-register']
def inspect(h):
 try:
  path='/web/login' if h in ['pbms','registry','portal-admin'] else '/login/' if h=='superset' else '/'
  r=requests.get('http://127.0.0.1:18080'+path,headers={'Host':h+'.nigeriag2p.com'},timeout=20,allow_redirects=False)
  return (h,r.status_code,r.headers.get('Content-Type',''),'brand-injected' if '/iqs-brand/iqs-brand.js' in r.text else 'no-brand-on-response')
 except Exception as e:return(h,type(e).__name__)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for v in pool.map(inspect,hosts):print(v)
