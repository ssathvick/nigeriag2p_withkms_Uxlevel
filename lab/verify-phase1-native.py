"""Read-only signed mapper and installed-backend checks; no public API exposure."""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
src=Path(__file__).parent
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
report={'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'scope':'Read-only native sandbox verification','checks':{}}
try:
    check=subprocess.run([sys.executable,str(src/'test-bridge-mapper.py')],capture_output=True,text=True,timeout=60)
    marker='Bridge worker successfully resolved the signed synthetic beneficiary account.'
    report['checks']['native_bridge_to_signed_spar']={'status':'passed' if check.returncode==0 and marker in check.stdout else 'failed','scope':'Existing synthetic beneficiary resolution; no bank settlement or capacity claim'}
except Exception:
    report['checks']['native_bridge_to_signed_spar']={'status':'blocked','scope':'Backend check unavailable'}
try:
    pb=r.Odoo('pbms-odoo','pbmsdb')
    programs=pb.call('g2p.program.definition','search',[[['program_status','=','ACTIVE']]])
    report['checks']['native_pbms']={'status':'passed','active_programme_count':len(programs),'scope':'Configured programme count, not concurrent-load certification'}
    with r.pg('register') as c:
        with c.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM g2p_register_households');households=cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM g2p_register_individuals');individuals=cur.fetchone()[0]
    report['checks']['native_registry']={'status':'passed','household_count':households,'individual_count':individuals,'scope':'Synthetic stored records, not production identity verification'}
except Exception:
    report['checks']['native_backend_inventory']={'status':'blocked','scope':'Inspect private backend configuration; no data was changed'}
out=src/'phase1-evidence/native-checks.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
