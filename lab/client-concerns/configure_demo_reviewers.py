from pathlib import Path
import secrets,json,sys,uuid
root=Path(__file__).parent
exec((root/'inspect_demo_roles.py').read_text().split("user=s.get")[0])
client=s.get(base+'/clients',params={'clientId':'register-staff-portal'}).json()[0]['id'];role_list=s.get(base+'/clients/'+client+'/roles').json()
secret_path=Path('/opt/openg2p-lab/registration/client-demo-accounts.json');accounts=json.loads(secret_path.read_text()) if secret_path.exists() else {}
for username,label,role in [('nsipa-demo-intake','NSIPA Intake Officer','Intake Officer'),('nsipa-demo-reviewer-one','NSIPA First Reviewer','Intake Validator'),('nsipa-demo-reviewer-two','NSIPA Second Reviewer','Intake Validator')]:
 found=s.get(base+'/users',params={'username':username,'exact':'true'}).json()
 if not found:
  password=secrets.token_urlsafe(28);res=s.post(base+'/users',json={'username':username,'enabled':True,'firstName':label,'lastName':'Demo','email':username+'@demo.invalid','emailVerified':True,'credentials':[{'type':'password','value':password,'temporary':False}]});res.raise_for_status();accounts[username]={'username':username,'password':password};secret_path.write_text(json.dumps(accounts));secret_path.chmod(0o600)
  found=s.get(base+'/users',params={'username':username,'exact':'true'}).json()
 user_id=found[0]['id'];res=s.put(base+'/users/'+user_id,json={'firstName':label,'lastName':'Demo','requiredActions':[]});res.raise_for_status();selected=next(x for x in role_list if x['name']==role);res=s.post(base+'/users/'+user_id+'/role-mappings/clients/'+client,json=[selected]);res.raise_for_status()
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as app
with app.pg('awe') as c:
 with c.cursor() as q:
  key='registry.intake_form.household'
  q.execute('SELECT id,version FROM approval_policy WHERE policy_key=%s ORDER BY version DESC LIMIT 1',(key,));pid,version=q.fetchone()
  if version==1:
   fresh=str(uuid.uuid4());q.execute("INSERT INTO approval_policy(id,policy_key,version,name,description,status,artifact_type,created_by,forbid_self_approval,forbid_repeat_approvers,created_at,updated_at) SELECT %s,policy_key,2,'NSIPA Household Intake: Independent Review','First review checks completeness and possible duplicates; second review confirms the decision.','active',artifact_type,'client-feedback-maintenance',true,true,now(),now() FROM approval_policy WHERE id=%s",(fresh,pid))
   q.execute('SELECT id,stage_order FROM approval_stage WHERE policy_id=%s ORDER BY stage_order',(pid,));stages=q.fetchall()
   for old,order in stages:
    sid=str(uuid.uuid4());q.execute("INSERT INTO approval_stage(id,policy_id,stage_order,name,mode,mode_value,sla_hours,parallel_group,skip_if,on_empty,on_breach,escalation_rules_json,created_at,updated_at) SELECT %s,%s,stage_order,%s,mode,mode_value,sla_hours,parallel_group,skip_if,on_empty,on_breach,escalation_rules_json,now(),now() FROM approval_stage WHERE id=%s",(sid,fresh,'Completeness and duplicate assessment' if order==1 else 'Independent final review',old))
    q.execute("INSERT INTO approver_rule(id,stage_id,rule_type,rule_value,kind,required,created_at,updated_at) VALUES(%s,%s,'user',%s::jsonb,'approver',false,now(),now())",(str(uuid.uuid4()),sid,json.dumps({'user_id':'nsipa-demo-reviewer-one' if order==1 else 'nsipa-demo-reviewer-two'})))
   q.execute("UPDATE approval_policy SET status='retired',updated_at=now() WHERE id=%s",(pid,))
 c.commit()
print('Provisioned separate limited demo identities; household intake policy version 2 uses two independent reviewers. Credentials remain private.')
