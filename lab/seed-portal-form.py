import json
exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/bootstrap-portal.py').read().split("call('ir.module.module','update_list'")[0])
schema={'display':'form','components':[{'type':'htmlelement','tag':'p','content':'Local UX demonstration only. Do not enter real personal information.','key':'notice','input':False},{'type':'textfield','label':'Preferred contact name','key':'contactName','input':True,'validate':{'required':True}},{'type':'textarea','label':'What assistance do you need? (demo only)','key':'supportRequest','input':True},{'type':'checkbox','label':'I understand this is a synthetic local demonstration','key':'demoConsent','input':True,'validate':{'required':True}},{'type':'button','label':'Submit application','key':'submit','action':'submit','input':True}]}
ids=call('formio.builder','search',[[['name','=','nigeria_lab_application']]])
if ids:builder=ids[0]
else:builder=call('formio.builder','create',[{'name':'nigeria_lab_application','title':'Nigeria Household Support — UX Demo','schema':json.dumps(schema),'portal':True,'state':'CURRENT','formio_version_id':call('formio.version','search',[[]])[0]}])
program=call('g2p.program','search',[[['name','=','Nigeria Household Support — Portal UX Demo']]])[0]
call('g2p.program','write',[[program],{'portal_form_builder_id':builder}])
print('Portal demo application form:',builder)
