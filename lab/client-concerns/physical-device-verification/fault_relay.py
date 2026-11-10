import sys,json,time,socket,http.client,threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
ROOT=Path('/opt/openg2p-lab/phone-fault-test')
cfg=json.loads((ROOT/'private.json').read_text())
token=query('odkdb', '''select s.token from sessions s join actors a on a.id=s."actorId" join field_keys f on f."actorId"=a.id where a."displayName"='OnePlus sample-only upload' and a."deletedAt" is null and f."projectId"=1 order by s."createdAt" desc limit 1;''').strip()
lock=threading.Lock()
def event(data):
 data['utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
 with (ROOT/'events.jsonl').open('a') as f:f.write(json.dumps(data)+'\n')
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path!=cfg['prefix']+'/formList':self.send_error(404);return
  c=http.client.HTTPConnection('127.0.0.1',18080,timeout=20)
  c.request('GET','/v1/key/'+token+'/projects/1/formList',headers={'Host':'g2p-odk.wverve.in','X-OpenRosa-Version':'1.0'})
  r=c.getresponse();data=r.read();self.send_response(r.status);self.send_header('Content-Type','text/xml');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);c.close()
 def do_POST(self):
  if self.path!=cfg['prefix']+'/submission':self.send_error(404);return
  length=int(self.headers.get('Content-Length','0'))
  if not 0<length<20000:self.send_error(400);return
  body=self.rfile.read(length)
  if b'PHONE-FAULT-05' not in body or b'nsipa_field_household_demo' not in body:self.send_error(403);return
  with lock:
   control=json.loads((ROOT/'control.json').read_text());mode=control['mode']
   (ROOT/'control.json').write_text(json.dumps(dict(control,mode='hold')))
  if mode not in ['mid','lost','pass']:self.send_error(503);return
  domain=control['domain'];assert domain in ['odk.nigeriag2p.com','g2p-odk.wverve.in']
  conn=http.client.HTTPConnection('127.0.0.1',18083 if domain.startswith('odk.') else 18080,timeout=20)
  conn.putrequest('POST','/v1/key/'+token+'/projects/1/submission',skip_host=True)
  for k,v in {'Host':domain,'Content-Type':self.headers['Content-Type'],'Content-Length':str(length),'X-OpenRosa-Version':'1.0'}.items():conn.putheader(k,v)
  conn.endheaders()
  if mode=='mid':
   partial=length//2;conn.send(body[:partial]);time.sleep(1);conn.close()
   event({'mode':mode,'domain':domain,'declared_bytes':length,'forwarded_bytes':partial,'upstream_body_completed':False})
   self.close_connection=True;self.connection.shutdown(socket.SHUT_RDWR);self.connection.close();return
  conn.send(body);resp=conn.getresponse();data=resp.read();status=resp.status;conn.close()
  event({'mode':mode,'domain':domain,'declared_bytes':length,'forwarded_bytes':length,'upstream_status':status,'response_delivered':mode=='pass'})
  if mode=='lost':
   self.close_connection=True;self.connection.shutdown(socket.SHUT_RDWR);self.connection.close();return
  self.send_response(status);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
ThreadingHTTPServer(('127.0.0.1',18891),Handler).serve_forever()
