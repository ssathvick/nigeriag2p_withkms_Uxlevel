"""Generate the actual local simulator API contract (not an agency contract)."""
import json
from pathlib import Path
from partner_simulation import SCENARIOS

def obj(properties, required=None):
    return {'type':'object','properties':properties,'required':required or list(properties)}
string={'type':'string'}
boolean={'type':'boolean'}
integer={'type':'integer'}
synthetic={'type':'boolean','enum':[True]}
responses={
 'identity':obj({'verified':boolean,'identity_reference':string,'consent_reference':string,'synthetic':synthetic}),
 'social-register':obj({'household_reference':string,'state':string,'members':integer,'eligible':boolean,'synthetic':synthetic}),
 'programme':obj({'programme_reference':string,'amount_minor':integer,'currency':{'type':'string','enum':['NGN']},'eligible':boolean,'synthetic':synthetic}),
 'treasury':obj({'funding_reference':string,'approved':boolean,'amount_minor':integer,'currency':string,'synthetic':synthetic}),
 'account':obj({'account_reference':string,'valid':boolean,'account_name':string,'synthetic':synthetic}),
 'payment':obj({'status':{'type':'string','enum':['accepted','failed']},'reason_code':{'type':['string','null']},'synthetic':synthetic}),
 'notification':obj({'delivery_status':string,'channel':string,'synthetic':synthetic}),
 'grievance':obj({'case_reference':string,'status':string,'synthetic':synthetic}),
 'reconciliation':obj({'settled_amount_minor':integer,'currency':string,'reversed':boolean,'synthetic':synthetic})}
def post(fields, schema):
    return {'security':[{'staffSession':[]}], 'requestBody':{'required':True,'content':{'application/x-www-form-urlencoded':{'schema':obj({'csrf':string,**fields})}}},
            'responses':{'200':{'description':'Synthetic result','content':{'application/json':{'schema':schema}}},
                         **{str(n):{'description':d} for n,d in [(400,'Invalid input'),(401,'Staff login required'),(403,'Role or CSRF rejected'),(409,'State or idempotency conflict')]}}}
scenario={'type':'string','enum':list(SCENARIOS)}
paths={}
for name,response in responses.items():
    paths['/api/simulation/partners/'+name]={'post':post({'scenario':scenario},response)}
paths['/api/simulation/runs']={'post':post({'scenario':scenario,'request_key':{'type':'string','format':'uuid'}},obj({'run_id':{'type':'string','format':'uuid'},'synthetic':synthetic}))}
paths['/api/simulation/callback']={'post':post({'run_id':{'type':'string','format':'uuid'},'event_id':{'type':'string','format':'uuid'},'status':{'type':'string','enum':['successful','reversed']}},obj({'accepted':boolean,'synthetic':synthetic}))}
paths['/api/simulation/report']={'get':{'security':[{'staffSession':[]}],'responses':{'200':{'description':'Current isolated simulation counts, runs and settled total','content':{'application/json':{'schema':obj({'synthetic':synthetic,'scope':string,'counts':{'type':'object','additionalProperties':integer},'settled_amount_minor':integer,'currency':string,'runs':{'type':'array','items':{'type':'object'}}})}}}}}}
paths['/api/simulation/reset']={'post':{'security':[{'staffSession':[]}],'requestBody':{'required':True,'content':{'application/x-www-form-urlencoded':{'schema':obj({'csrf':string,'confirmation':{'type':'string','enum':['RESET SYNTHETIC RUNS']}})}}},'responses':{'302':{'description':'Simulation cleared; redirect to console'},'400':{'description':'Confirmation missing'},'403':{'description':'CSRF or role rejected'}}}}
doc={'openapi':'3.1.0','info':{'title':'Nigeria G2P Local Partner Simulation','version':'1.0.0','description':'Simulation contracts only. NOT official NIMC, NASSCO, NIBSS, bank or treasury schemas. Fixed synthetic fixtures. Uses platform staff sessions and form CSRF. Amounts are integer kobo; settlement and payment acceptance are separate.'},'servers':[{'url':'/registration'}],'paths':paths,'components':{'securitySchemes':{'staffSession':{'type':'apiKey','in':'cookie','name':'IQS-INTAKE','description':'Existing staff login; supervisor or intake reviewer role. CSRF token required on every POST.'}},'schemas':responses}}
Path(__file__).with_name('simulation-openapi.json').write_text(json.dumps(doc,indent=2))
