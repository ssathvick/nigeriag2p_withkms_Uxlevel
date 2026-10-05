import json,subprocess
for deployment,module,extra in [('pbms-celery-beat-producer','openg2p_bg_task_celery_beat_producers.main.celery_app',['--beat','--schedule=/tmp/celery-beat-schedule.db']),('pbms-celery-worker','openg2p_bg_task_celery_workers.main.celery_app',['-Q','bg_task_worker_queue'])]:
 d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',deployment,'-o','json']))
 c=d['spec']['template']['spec']['containers'][0]
 c['command']=['celery'];c['args']=['-A',module,'worker','--concurrency=2','--loglevel=info']+extra
 if deployment=='pbms-celery-worker':
  replacements={'BG_TASK_CELERY_WORKERS_G2P_BRIDGE_BASE_URL':'http://bridge-openg2p-g2p-bridge-api','BG_TASK_CELERY_WORKERS_KEYMANAGER_API_BASE_URL':'http://commons-services-keymanager/v1/keymanager','BG_TASK_CELERY_WORKERS_SIGN_KEY_KEYMANAGER_APP_ID':'OPENG2P_PBMS'}
  for k,v in replacements.items():
   c['env']=[e for e in c['env'] if e['name']!=k]+[{'name':k,'value':v}]
 subprocess.run(['kubectl','-n','nigeria','patch','deploy',deployment,'--type=merge','-p',json.dumps({'spec':{'template':d['spec']['template']}})],check=True,stderr=subprocess.DEVNULL)
