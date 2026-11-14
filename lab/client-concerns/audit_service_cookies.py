"""Read-only sign-in/session audit. Never retain credential or cookie values."""
import sys,json,datetime,concurrent.futures,secrets,hashlib,base64
from pathlib import Path
from urllib.parse import urlparse,urljoin,quote,urlencode,parse_qs
from http.cookies import SimpleCookie
import requests,yaml
from bs4 import BeautifulSoup
ROOT=Path('/opt/openg2p-lab');OUT=Path(__file__).parent
PASSWORD=yaml.safe_load((ROOT/'credentials.yaml').read_text())['admin_password']
SERVICES={
 'register':('next','/api/login'), 'awe':('pkce','/api/v1/policies'),
 'master-data-ui':('next','/api/login'),'partner-management':('next','/api/login'),
 'consent-manager':('pkce','/api/v1/partners'),'staff-portal':('next','/api/login'),
 'iam-staff-ui':('next','/api/login'),
 'odk':('oidc','/v1/oidc/login'),'superset':('oidc','/login/keycloak'),
 'registry':('odoo','socialregistrydb'),'portal-admin':('odoo','portalpbmsdb'),
 'beneficiary':('beneficiary','/selfservice'),
 'registration':('workspace','/registration/login?mode=staff'),
 'pbms':('odoo','pbmsdb'),
}
def audit(name):
 kind,path=SERVICES[name];host='g2p.wverve.in' if name=='registration' else 'g2p-'+name+'.wverve.in';base='https://'+host
 row={'service':name,'host':host,'cookies':[],'invalid_cookie_domains':[],'redirects':[]}
 s=requests.Session();s.verify=str(ROOT/'registration/ca-bundle.crt')
 def observe(response,*args,**kwargs):
  url=urlparse(response.url);row['redirects'].append({'host':url.hostname,'path':url.path,'http':response.status_code})
  for raw in response.raw.headers.getlist('Set-Cookie'):
   jar=SimpleCookie()
   try:jar.load(raw)
   except Exception:continue
   for key,value in jar.items():
    domain=value['domain'].lstrip('.').lower();valid=not domain or url.hostname==domain or url.hostname.endswith('.'+domain)
    info={'name':key,'source_host':url.hostname,'domain':value['domain'] or '(host-only)','secure':bool(value['secure']),'http_only':bool(value['httponly']),'same_site':value['samesite'],'valid_domain':valid}
    if info not in row['cookies']:row['cookies'].append(info)
    if not valid and info not in row['invalid_cookie_domains']:row['invalid_cookie_domains'].append(info)
 s.hooks['response'].append(observe)
 try:
  if kind=='pkce':
   cfg=s.get(base+'/config.json',timeout=30).json()['keycloak']
   issuer=cfg['url']+'/realms/'+cfg['realm']+'/protocol/openid-connect'
   verifier=secrets.token_urlsafe(48);state=secrets.token_urlsafe(24)
   challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
   params={'client_id':cfg['clientId'],'redirect_uri':base+'/','response_type':'code','scope':'openid','state':state,'code_challenge':challenge,'code_challenge_method':'S256'}
   response=s.get(issuer+'/auth',params=params,timeout=30)
   form=BeautifulSoup(response.text,'html.parser').select_one('form#kc-form-login');assert form,'Keycloak form missing'
   data={i['name']:i.get('value','') for i in form.select('input[name]')};data.update(username='admin',password=PASSWORD)
   response=s.post(urljoin(response.url,form['action']),data=data,allow_redirects=False,timeout=30)
   callback=urlparse(response.headers.get('Location',''));qs=parse_qs(callback.query or callback.fragment)
   assert callback.hostname==host and qs.get('state')==[state] and qs.get('code'),'OIDC callback failed'
   response=s.post(issuer+'/token',data={'grant_type':'authorization_code','client_id':cfg['clientId'],'redirect_uri':base+'/','code':qs['code'][0],'code_verifier':verifier},timeout=30)
   assert response.status_code==200 and response.json().get('access_token'),'PKCE token exchange failed'
   tokens=response.json()
   for repeat in range(2):
    response=s.get(issuer+'/userinfo',headers={'Authorization':'Bearer '+tokens['access_token']},timeout=30)
    assert response.status_code==200 and response.json().get('sub'),'OIDC identity check failed'
   response=s.post(issuer+'/token',data={'grant_type':'refresh_token','client_id':cfg['clientId'],'refresh_token':tokens['refresh_token']},timeout=30)
   assert response.status_code==200 and response.json().get('access_token'),'Session refresh failed'
   row['session_verification_endpoint']='OIDC userinfo (twice) and refresh_token'
   row['auth_type']='Authorization code with S256 PKCE; host-only Keycloak cookies'
  elif kind=='odoo':
   response=s.post(base+'/web/session/authenticate',json={'jsonrpc':'2.0','params':{'db':path,'login':'admin@nigeria.openg2p.localhost','password':PASSWORD},'id':1},timeout=35)
   assert response.status_code==200 and response.json().get('result',{}).get('uid'),'Odoo authentication failed'
   response=s.post(base+'/web/session/get_session_info',json={'jsonrpc':'2.0','params':{},'id':2},timeout=30)
   assert response.json().get('result',{}).get('uid'),'Odoo session not retained'
  elif kind=='discover':
   response=s.get(base+path,timeout=30)
   soup=BeautifulSoup(response.text,'html.parser')
   row['links']=[{'label':a.get_text(' ',strip=True)[:80],'href':a.get('href','').split('?')[0]} for a in soup.select('a[href]') if 'login' in a.get('href','') or 'sign' in a.get_text().lower()]
   row['status']='NEEDS_LOGIN_ROUTE';return row
  else:
   response=s.get(base+path+('?redirect_uri='+quote(base+('/' if name=='partner-management' else '/en'),safe='') if kind=='next' else ''),timeout=35)
   if kind=='beneficiary':
    providers=s.get(base+'/v1/selfservice/auth/getLoginProviders',timeout=30).json()['loginProviders']
    provider=next(p['id'] for p in providers if p['name']=='Local UX Demo Login')
    link={'href':base+'/v1/selfservice/auth/getLoginProviderRedirect/'+str(provider)+'?redirect_uri=/selfservice/'}
    assert link,'Beneficiary login provider link missing'
    response=s.get(urljoin(response.url,link['href']),timeout=30)
   soup=BeautifulSoup(response.text,'html.parser');form=soup.select_one('form#kc-form-login')
   if not form:
    row['status']='NEEDS_LOGIN_ROUTE';row['response_type']=response.headers.get('content-type');row['title']=soup.title.get_text() if soup.title else '';return row
   data={i['name']:i.get('value','') for i in form.select('input[name]')}
   account=json.loads((ROOT/'registration/test-account.json').read_text()) if kind=='beneficiary' else {'username':'admin','password':PASSWORD}
   data.update(username=account['username'],password=account['password'])
   response=s.post(urljoin(response.url,form['action']),data=data,timeout=45)
   assert response.status_code<400,'Callback HTTP '+str(response.status_code)
   assert not BeautifulSoup(response.text,'html.parser').select_one('form#kc-form-login'),'Login form still present'
   endpoint={'next':'/api/me','workspace':'/registration/api/workspace','beneficiary':'/v1/selfservice/applicationdetails','oidc':'/v1/users/current' if name=='odk' else '/api/v1/me/'}[kind]
   for repeat in range(2):
    response=s.get(base+endpoint,timeout=30)
    assert response.status_code==200,'Session verification HTTP '+str(response.status_code)
    assert '/login' not in urlparse(response.url).path,'Session redirected to login'
    if kind!='beneficiary':assert 'json' in response.headers.get('content-type',''),'Authenticated JSON endpoint returned HTML'
   row['session_verification_endpoint']=endpoint
  row['status']='PASS' if not row['invalid_cookie_domains'] else 'COOKIE_DOMAIN_MISMATCH'
 except Exception as e:
  row['status']='COOKIE_DOMAIN_MISMATCH' if row['invalid_cookie_domains'] else 'FAIL'
  row['error']=str(e)[:140] if isinstance(e,AssertionError) else type(e).__name__
 finally:s.close()
 return row
def main():
 selected=sys.argv[1:] or list(SERVICES)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(audit,selected))
 output={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'local-resolution','services':rows}
 dest=OUT/'service-cookie-audit.json';dest.write_text(json.dumps(output,indent=2))
 print(json.dumps([{k:v for k,v in x.items() if k not in ['cookies','redirects']} for x in rows],indent=2))
if __name__=='__main__':main()
