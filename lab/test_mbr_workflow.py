"""Integration tests against disposable tables; never modify existing registry records."""
import base64
import datetime
import json
import os
import subprocess
import sys
import types
import uuid
import psycopg2
from flask import Flask, g, abort, request
from werkzeug.exceptions import HTTPException
import mbr_workflow as mbr

def kube(*args):
    return subprocess.check_output(['kubectl','-n','nigeria',*args],text=True).strip()
secret=json.loads(kube('get','secret','commons-postgresql','-o','json'))
config=dict(host=kube('get','svc','commons-postgresql','-o','jsonpath={.spec.clusterIP}'),dbname='register',user='postgres',
            password=base64.b64decode(secret['data']['postgres-password']).decode())
schema='mbr_test_'+uuid.uuid4().hex[:12]
def conn(isolated=True):return psycopg2.connect(**config,options='-c search_path='+schema if isolated else '')
with conn(False) as c:
    with c.cursor() as cur:
        cur.execute('CREATE SCHEMA '+schema)
        for table in ['g2p_register_households','g2p_register_individuals']:
            cur.execute('CREATE TABLE '+schema+'.'+table+' (LIKE public.'+table+' INCLUDING ALL)')
app=Flask(__name__)
@app.before_request
def context():
    g.user={'sub':request.headers.get('X-Actor','officer'),'roles':[request.headers.get('X-Role','mbr-officer')],'name':'Synthetic test'}
    g.session={'mode':'staff'}
@app.errorhandler(HTTPException)
def error(e):return {'error':e.description},e.code
def require_user():
    if not g.user:abort(401)
r=types.SimpleNamespace(app=app,PREFIX='/registration',pg=lambda _:conn(),require_user=require_user,
                       stamp=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat(),redirect=lambda x:x,page=lambda *a,**kw:'MBR')
mbr.install(r)
client=app.test_client();checks=0
def call(path,data=None,role='mbr-officer',actor='officer',expected=200):
    global checks
    method=client.post if data is not None else client.get
    response=method('/registration/mbr/api'+path,data={'payload':json.dumps(data)} if data is not None else None,
                    headers={'X-Role':role,'X-Actor':actor})
    assert response.status_code==expected,(path,response.status_code,response.get_json())
    checks+=1;return response.get_json()
def payload():
    return dict(consent='Yes',sponsor='NG CARES',enumerator='Aarin',state='Kano',zone='North West',community='Test Community',
                serial_number='SYNTHETIC-MBR-TEST',address='Synthetic test address',number_heads=1,complete_members='Yes',
                members=[dict(id=str(uuid.uuid4()),first_name='Synthetic',surname='Workflow',relationship='Head of Household',sex='Female',
                              age=36,valid_nin='Yes',nin='00000000001',bank_account='0000000001')],
                roof='Metal sheets',floor='Cement',rooms=2,water='Borehole',lighting='Solar',cooking_fuel='Gas',income_source='Trading',
                monthly_income=10000,shocks=[],health_insurance='No',assets={a:'No' for a in mbr.ASSETS},grows_crops='No',crops=[])
try:
    p=payload()
    call('/submissions',{'data':p,'submit':True},role='mbr-admin',actor='admin',expected=403)
    call('/submissions',{'data':p,'submit':True},role='mbr-level1',actor='l1',expected=403)
    call('/bootstrap',role='unassigned',expected=403)
    call('/submissions',{'data':{**p,'consent':'No'},'submit':True},expected=422)
    bad=json.loads(json.dumps(p));bad['members'][0]['nin']='123'
    call('/submissions',{'data':bad,'submit':True},expected=422)
    s=call('/submissions',{'data':p},expected=201);sid=s['id']
    assert s['state']=='DRAFT' and len(s['reference'])==16
    call('/submissions/'+sid,actor='other',expected=403)
    s=call('/submissions/'+sid+'/save',{'data':p,'submit':True,'version':s['version']})
    assert s['state']=='PENDING'
    call('/submissions/'+sid+'/decision',{'action':'approve','version':s['version']},role='mbr-admin',expected=403)
    call('/submissions/'+sid+'/decision',{'action':'approve','version':s['version']},role='mbr-level2',actor='l2',expected=403)
    call('/submissions/'+sid+'/decision',{'action':'return','version':s['version']},role='mbr-level1',actor='l1',expected=422)
    s=call('/submissions/'+sid+'/decision',{'action':'return','comment':'Confirm survey details','version':s['version']},role='mbr-level1',actor='l1')
    assert s['state']=='RETURNED'
    s=call('/submissions/'+sid+'/save',{'data':p,'submit':True,'version':s['version']})
    s=call('/submissions/'+sid+'/decision',{'action':'approve','version':s['version']},role='mbr-level1',actor='l1')
    assert s['stage']==2
    call('/submissions/'+sid+'/decision',{'action':'approve','version':s['version']},role='mbr-level2',actor='l1',expected=403)
    stale=s['version']
    s=call('/submissions/'+sid+'/decision',{'action':'approve','version':s['version']},role='mbr-level2',actor='l2')
    assert s['state']=='APPROVED'
    call('/submissions/'+sid+'/decision',{'action':'approve','version':stale},role='mbr-level2',actor='l2',expected=409)
    boot=call('/bootstrap');master=boot['masters'][0]
    assert master['household_id'].startswith('HH-') and len(master['household_id'])==13 and len(master['payload']['members'])==1
    new=master['payload'];new['community']='Updated synthetic community'
    change=call('/submissions',{'kind':'change','master_id':master['id'],'base_revision':master['revision'],'data':new,'submit':True},expected=201)
    assert call('/submissions/'+change['id'])['diff']
    change=call('/submissions/'+change['id']+'/decision',{'action':'approve','version':change['version']},role='mbr-level1',actor='l1')
    with conn() as c:
        with c.cursor() as cur:cur.execute("UPDATE g2p_register_households SET last_approved_at=now() WHERE internal_record_id=%s",(master['id'],))
    call('/submissions/'+change['id']+'/decision',{'action':'approve','version':change['version']},role='mbr-level2',actor='l2',expected=409)
    change=call('/submissions/'+change['id']+'/decision',{'action':'return','comment':'Refresh changed baseline','version':change['version']},role='mbr-level2',actor='l2')
    change=call('/submissions/'+change['id']+'/save',{'data':new,'submit':True,'version':change['version'],'refresh_baseline':True})
    change=call('/submissions/'+change['id']+'/decision',{'action':'approve','version':change['version']},role='mbr-level1',actor='l1')
    change=call('/submissions/'+change['id']+'/decision',{'action':'approve','version':change['version']},role='mbr-level2',actor='l2')
    assert call('/bootstrap')['masters'][0]['payload']['community']=='Updated synthetic community'
    field=payload();batch={'batch':[{'client_id':'same-sync','data':field}]}
    first=call('/sync',batch,role='mbr-field-agent',actor='field')
    again=call('/sync',batch,role='mbr-field-agent',actor='field')
    assert first['synced'][0]['id']==again['synced'][0]['id'] and first['synced'][0]['source']=='Offline Data Collection'
    duplicate=call('/submissions/'+first['synced'][0]['id'],role='mbr-level1',actor='l1')
    assert duplicate['duplicates']['existing'][0]['exact_nin']
    fs=first['synced'][0]
    call('/submissions/'+fs['id']+'/decision',{'action':'reject','comment':'Confirmed synthetic duplicate','version':fs['version']},role='mbr-level1',actor='l1')
    call('/submissions/'+fs['id']+'/save',{'data':field,'version':fs['version']},role='mbr-field-agent',actor='field',expected=409)
    call('/sync',{'batch':[{'client_id':'rolled-back','data':payload()},{'client_id':'invalid','data':{}}]},role='mbr-field-agent',actor='field',expected=422)
    with conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM g2p_mbr_submissions WHERE client_id='rolled-back'");assert cur.fetchone()[0]==0
    call('/analytics',expected=403)
    analytics=call('/analytics',role='mbr-admin',actor='admin');assert analytics['households']==1 and analytics['individuals']==1
    print(json.dumps({'checks':checks,'result':'passed','coverage':['RBAC','validation','return/resubmit','stage separation','atomic native promotion','stale decisions','change diffs','baseline conflict','change application','duplicate scoring','offline idempotency','permanent lock','batch rollback','admin analytics']}))
finally:
    with conn(False) as c:
        with c.cursor() as cur:cur.execute('DROP SCHEMA '+schema+' CASCADE')
