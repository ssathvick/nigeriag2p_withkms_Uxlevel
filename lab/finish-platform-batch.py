"""Resume API fixtures after Odoo/registry stages have completed."""
path='/mnt/h/Nigeria_Mosip/codex/openg2p-lab/seed-platform-batch.py'
source=open(path).read()
exec(source.split("query('register','BEGIN;")[0])
programmes=[('HOUSEHOLD','Household Cash Support',25000,'ACTIVE'),('FARM','Smallholder Farming Grant',40000,'ACTIVE'),('SCHOOL','School Materials Support',15000,'ACTIVE'),('LIVELIHOOD','Livelihood Starter Grant',50000,'PAUSED'),('RELIEF','Emergency Relief Assistance',30000,'CLOSED')]
report={'modern_registry':{'individuals':200,'households':50,'states_and_fct':37},'socialregistrydb':{'individuals':200,'households':50,'memberships':200},'portalpbmsdb':{'individuals':200,'households':50,'memberships':200},'pbms':{'programmes':5,'benefit_codes':5,'enrollment_cycles':5,'fixture_registry_rows':200},'beneficiary_portal':{'programmes':5,'application_forms':200,'programme_memberships':205,'demo_login':'fatima','states':['draft','enrolled','paused','not_eligible','exited']}}
exec(source.split('# Reuse existing administrator access;')[1].split('\n',1)[1])
