from pathlib import Path
import json
import zipfile,hashlib
root=Path(__file__).parent
evidence=root/'phase1-evidence'
latest=sorted(evidence.glob('*-results.json'))[-1]
report=json.loads(latest.read_text())
target=root.parent/'outputs/phase1_client_review/NigeriaG2P_Phase1_Sandbox_UAT_Pack.zip'
files=[latest,evidence/'native-checks.json',evidence/'browser-checks.json',evidence/'field-sync-browser.png',evidence/'portal-igbo-browser.png',root/'Phase1-Sandbox-Operations.md']
for name in ['native-registration-uat','native-reconciliation-uat','native-household-payment','native-mapper-guard-tests','native-bank-replay','native-statement-recovery','native-statement-backlog','native-programme-concurrency','native-payment-contract-capacity','capacity-agents','capacity-native-registry','public-security-performance','browser-readiness','sqlite-restore','release-manifest']:
 files.append(evidence/(name+'.json'))
files.extend(evidence/name for name in ['portal-release-browser.png','portal-viewport-browser.png','readiness-viewport-browser.png','portal-mobile-browser.png'])
files.extend(evidence/x['evidence_file'] for x in report['suites'])
files.extend(root/name for name in ['run-phase1-checks.py','verify-phase1-native.py','phase1_sandbox.py','phase1_cms.py','phase1_observability.py','phase1-worker.py','test-phase1-sandbox.py','test-phase1-readiness.py','test-phase1-capacity.py','test-native-registry-capacity.py','test-native-programme-concurrency.py','test-native-bank-replay.py','test-native-statement-recovery.py','test-phase1-sqlite-restore.py','verify-native-household-payment.py','check-public-readiness.py','publish-readiness-evidence.py','install-phase1-sandbox.py','repair-native-worker-readiness.py','repair-native-statement-idempotency.py','repair-bank-api-redis.py','configure-native-reconciliation.py','prepare-native-payment-uat.py','refresh-readiness-navigation.py'])
files.extend(root/'registration-ui'/name for name in ['base.html','phase1.html','phase1-field.html','phase1-public.html','phase1-cms.html','phase1-grievances.html','phase1-readiness.html'])
files.extend(root/'knowledge'/name for name in ['phase1-field.js','phase1-sw.js','phase1-portal.css'])
files.append(root/'compatibility/bank-api-redis-6.2.0.zip')
files.extend(root/name for name in ['test-native-payment-contracts.py','record-phase1-release.py'])
files.extend([root/'phase1_conditionality.py',root/'registration-ui/phase1-conditionality.html'])
files.append(evidence/'conditionality-browser.png')
files.extend([root/'test-native-statement-lock.py',evidence/'native-statement-lock.json'])
files.extend(root/name for name in ['registration_app.py','persona-ui/dist/site.js','persona-ui/dist/site-shell.js','persona-ui/src/site.jsx','persona-ui/src/shell.js','sitewide-ui/index.html','knowledge/help.js'])
uat=root.parent/'outputs/phase1_client_review/NSIPA_Phase_1_UAT_Plan_and_Test_Cases.docx'
files.append(uat)
update=root.parent/'outputs/phase1_client_review/NSIPA_Phase_1_Sandbox_Readiness_Update.docx';files.append(update)
manifest=[]
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:
        if not p.is_file():raise RuntimeError('Missing evidence '+str(p))
        relative=str(p.parent.relative_to(root)).replace('\\','/') if p.parent!=evidence and p not in (uat,update) else ''
        folder='UAT' if p==uat else 'client' if p==update else 'evidence' if p.parent==evidence else 'reference'+('/'+relative if relative!='.' else '')
        arc=folder+'/'+p.name;z.write(p,arc);manifest.append({'file':arc,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    z.writestr('manifest.json',json.dumps({'scope':'Sandbox technical evidence; formal client acceptance remains pending','files':manifest},indent=2))
    z.writestr('README.txt','Read client/NSIPA_Phase_1_Sandbox_Readiness_Update.docx first. The original UAT plan must be executed and filled by the test team. JSON evidence is actual engineering verification, not client sign off. SQL and demonstration agent capacity benchmarks are separate from full native application acceptance. No credentials, private runtime configuration or diagnostic logs are included. Native compatibility fixes must be retained during upgrades. Reference changes target the existing openg2p-lab installation; this is not a standalone new deployment. Never run payment seed or approval scripts as routine verification.\n')
print(target)
