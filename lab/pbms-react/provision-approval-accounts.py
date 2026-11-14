"""Provision actual staff accounts for the isolated NSIPA presentation programme."""
import pathlib,json,secrets,os
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
private=pathlib.Path('/opt/openg2p-lab/pbms-react/nsipa-presentation-credentials.json')
creds=json.loads(private.read_text()) if private.exists() else {}
base=call('ir.model.data','search_read',[[['module','=','base'],['name','=','group_user']]],{'fields':['res_id']})[0]['res_id']
for role,key in [('Programme Admin','admin'),('Payment','payment'),('Finance','finance'),('Audit','audit'),('CEO','ceo')]:
 login='nsipa.'+key+'@example.invalid';entry=creds.get(key) or {'login':login,'password':secrets.token_urlsafe(20)}
 group=call('ir.model.data','search_read',[[['module','=','nsipa_approval'],['name','=','group_'+key]]],{'fields':['res_id']})[0]['res_id']
 found=call('res.users','search',[[['login','=',login]]],{'context':{'active_test':False}})
 if found:account_id=found[0];call('res.users','write',[[account_id],{'active':True,'password':entry['password'],'groups_id':[[4,group]]}])
 else:account_id=call('res.users','create',[{'name':'NSIPA '+role,'login':login,'password':entry['password'],'groups_id':[[6,0,[base,group]]]}])
 entry['uid']=account_id;creds[key]=entry
private.write_text(json.dumps(creds,indent=2));private.chmod(0o600)
copy=pathlib.Path('/mnt/h/Nigeria_Mosip/Credentials/NSIPA-PBMS-Approval-Accounts.json');copy.parent.mkdir(exist_ok=True);copy.write_text(private.read_text())
print('Five role-specific staff accounts available. Credentials saved privately; no passwords printed.')
