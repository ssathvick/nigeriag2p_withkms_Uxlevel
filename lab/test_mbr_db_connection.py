import base64,json,subprocess
import psycopg2
def connect(database='register'):
    def kube(*args):return subprocess.check_output(['kubectl','-n','nigeria',*args],text=True).strip()
    secret=json.loads(kube('get','secret','commons-postgresql','-o','json'))
    return psycopg2.connect(host=kube('get','svc','commons-postgresql','-o','jsonpath={.spec.clusterIP}'),dbname=database,user='postgres',password=base64.b64decode(secret['data']['postgres-password']).decode())
