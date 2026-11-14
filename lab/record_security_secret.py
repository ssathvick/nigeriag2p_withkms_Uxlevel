"""Provision an internal signing key without printing or publishing it."""
import json,secrets,subprocess
def signing_environment(container):
 name='nsipa-record-security'
 exists=subprocess.run(['kubectl','-n','nigeria','get','secret',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
 if not exists:
  secret={'apiVersion':'v1','kind':'Secret','metadata':{'name':name,'namespace':'nigeria'},'type':'Opaque','stringData':{'request-signing-key':secrets.token_urlsafe(48)}}
  subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(secret),text=True,check=True,stdout=subprocess.DEVNULL)
 container['env']=[e for e in container.get('env',[]) if e['name']!='NSIPA_REGISTRY_REQUEST_KEY']+[{'name':'NSIPA_REGISTRY_REQUEST_KEY','valueFrom':{'secretKeyRef':{'name':name,'key':'request-signing-key'}}}]
