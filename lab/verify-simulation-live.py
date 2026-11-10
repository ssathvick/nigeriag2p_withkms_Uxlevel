"""Verify installed simulator; retain three clearly synthetic demo runs."""
import sys
import uuid
import json
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
from flask import g
import requests

base='http://127.0.0.1:18081/registration'
assert requests.get(base+'/health',timeout=5).status_code==200
assert requests.get(base+'/api/simulation/report',timeout=5).status_code==401
assert requests.post(base+'/api/simulation/runs',timeout=5).status_code==403
before=len(r.rows('SELECT sub FROM profiles'))
for scenario in ['success','identity_mismatch','reconciliation_mismatch']:
    key=str(uuid.uuid5(uuid.NAMESPACE_URL,'installed-simulation-demo:'+scenario))
    with r.app.test_request_context('/registration/api/simulation/runs',method='POST',data={'scenario':scenario,'request_key':key}):
        g.user={'sub':'simulation-install-verifier','name':'Simulation verification','roles':['iqs-programme-supervisor']}
        g.session={'mode':'staff','csrf':'internal-render-only'}
        result=r.app.view_functions['partner_simulation.start']()
        assert result[0]['synthetic']
assert len(r.rows('SELECT sub FROM profiles'))==before
print('Installed health, anonymous guards, synthetic runs and profile isolation verified.')
with r.app.test_request_context('/registration/simulation'):
    g.user={'sub':'simulation-preview','name':'Simulation preview','roles':['iqs-programme-supervisor']}
    g.session={'mode':'staff','csrf':'offline-preview-only'};g.staff=True
    html=r.app.view_functions['partner_simulation.console']()
    # Preview is static, contains synthetic data only and cannot submit to the live service.
    html=html.replace('href="/registration/static/style.css"','href="https://g2p.wverve.in/registration/static/style.css"')
    html=html.replace('src="/iqs-brand/iqs-logo.png"','src="https://g2p.wverve.in/iqs-brand/iqs-logo.png"')
    html=html.replace('<form method="post"','<form onsubmit="return false" method="post"')
    Path('/mnt/h/Nigeria_Mosip/codex/outputs/simulation-preview.html').write_text(html)
print(json.dumps({'counts':r.simulation_report()['counts'],'synthetic':True}))
