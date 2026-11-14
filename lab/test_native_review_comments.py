import json
import test_meeting_native_workflow as t
path=t.OUT/'browser-draft-state.json';sid=json.loads(path.read_text())['submission_ids'][0];case={'id':sid}
d=t.detail(case)
if d['draft_status']=='DRAFT' and not d.get('awe_request_id'):
 row=next(s['records'][0] for s in d['section_payloads'] if s['section_id']=='hh_composition_headship');row.update(sponsor_name='NSIPA',consent_status='YES',respondent_name='Fictional Browser Head',enumerator_name='aarin@gmail.com',edit_action='UPDATE')
 t.call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':sid,'register_id':t.REG,'form_id':t.FORM,'section_id':'hh_composition_headship','section_register_id':t.REG,'section_payload':[row]});t.finalize(case,'aarin@gmail.com')
events=t.detail(case).get('review_history',[])
if not any(e['event_type']=='decision_approve' for e in events):
 t.decide(case,'abutu@gmail.com','approve','Fictional review comment preserved in native history.')
 t.wait_for(lambda:any(e['event_type']=='decision_approve' and e.get('reason')=='Fictional review comment preserved in native history.' for e in t.detail(case).get('review_history',[])),'Native first review comment')
t.check('Native approval history retains decision comments and actors')
original=t.call('aarin@gmail.com','intake-form/get-intake-form-submission',{'submission_id':'718cc3ad-7f81-46cb-aea0-2696bb15e732','register_id':t.REG})[0]
t.check('Historical decisions and comments remain visible inside native registry',any(e['event_type'].startswith('decision_') for e in original.get('review_history',[])))
