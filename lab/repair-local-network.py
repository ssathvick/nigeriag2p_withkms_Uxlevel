import subprocess, json, socket, re

def get(kind):
    return json.loads(subprocess.check_output(['kubectl','get',kind,'-n','nigeria','-o','json']))['items']
def patch(kind,name,payload):
    subprocess.run(['kubectl','patch',kind,name,'-n','nigeria','--type=merge','-p',json.dumps(payload)],check=True,stdout=subprocess.DEVNULL)
def localize(value):
    if not isinstance(value,str): return value
    for old in ['.nigeria.openg2p.org','.trial.openg2p.org','.dev.openg2p.org','.sandbox.openg2p.net','.openg2p.sandbox.net']:
        value=value.replace(old,'.openg2p.localhost')
    return value

hostnames={'openg2p.localhost','nigeriag2p.com'}
for resource in get('virtualservices'):
    spec=resource['spec']; spec=json.loads(localize(json.dumps(spec)))
    name=resource['metadata']['name']
    if name=='commons-services-pm-staff-portal-api': spec['hosts']=list(dict.fromkeys(spec['hosts']+['partner-management-api.openg2p.localhost']))
    if name=='bridge-bene-portal-api': spec['hosts']=list(dict.fromkeys(spec['hosts']+['bridge-beneficiary-api.openg2p.localhost']))
    patch('virtualservice',name,{'spec':spec})
    hostnames.update(spec['hosts'])

ip=subprocess.check_output(['hostname','-I'],text=True).split()[0]
for kind in ['deployment','statefulset']:
    for resource in get(kind):
        spec=resource['spec']['template']['spec']
        spec['hostAliases']=[{'ip':ip,'hostnames':[host]} for host in sorted(hostnames)]
        volumes=spec.setdefault('volumes',[])
        if not any(v['name']=='lab-trust' for v in volumes): volumes.append({'name':'lab-trust','configMap':{'name':'lab-trust'}})
        for container in spec.get('containers',[])+spec.get('initContainers',[]):
            mounts=container.setdefault('volumeMounts',[])
            if not any(m['name']=='lab-trust' for m in mounts): mounts.append({'name':'lab-trust','mountPath':'/etc/openg2p-lab-trust','readOnly':True})
            env=container.setdefault('env',[])
            for variable in env:
                if 'value' in variable: variable['value']=localize(variable['value'])
            trust={'REQUESTS_CA_BUNDLE':'/etc/openg2p-lab-trust/ca-bundle.crt','SSL_CERT_FILE':'/etc/openg2p-lab-trust/ca-bundle.crt','NODE_EXTRA_CA_CERTS':'/etc/openg2p-lab-trust/ca-bundle.crt','JAVA_TOOL_OPTIONS':'-Djavax.net.ssl.trustStore=/etc/openg2p-lab-trust/java-cacerts -Djavax.net.ssl.trustStorePassword=changeit'}
            for key,value in trust.items():
                old=next((e for e in env if e['name']==key),None)
                if old is None: env.append({'name':key,'value':value})
        patch(kind,resource['metadata']['name'],{'spec':{'template':{'spec':spec}}})

core=json.loads(subprocess.check_output(['kubectl','get','cm','coredns','-n','kube-system','-o','json']))
lines=core['data'].get('NodeHosts','').splitlines()
lines=[line for line in lines if 'openg2p.localhost' not in line and 'openg2p-ux.localhost' not in line and 'nigeriag2p.com' not in line]
lines.extend(ip+' '+host for host in sorted(hostnames))
subprocess.run(['kubectl','patch','cm','coredns','-n','kube-system','--type=merge','-p',json.dumps({'data':{'NodeHosts':'\n'.join(lines)+'\n'}})],check=True)
print('Local DNS, hostnames and certificate trust repaired for', len(hostnames), 'hosts.')
