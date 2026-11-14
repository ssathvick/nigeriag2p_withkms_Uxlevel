"""Resolve reported names only by unique, parent-scoped master-data matches."""
def normalized(value):
 return ' '.join(str(value).casefold().split())

def resolve_geography(state,lga,values):
 def unique(level,name,parent):
  matches=[v for v in values if v['level_id']==level and normalized(v['level_value_mnemonic'])==normalized(name) and v['parent_level_value_id']==parent]
  if len(matches)!=1:raise ValueError('Missing or ambiguous geography: '+level+' '+name)
  return matches[0]
 country=unique('country','Nigeria',None)
 province=unique('state',state,country['level_value_id'])
 local=unique('lga',lga,province['level_value_id'])
 return {'geo_lowest_level_value_id':local['level_value_id'],'geo_code_hierarchy_json':{'hierarchy':[
  {'level_mnemonic':label,'level_value_mnemonic':v['level_value_mnemonic'],'level_value_id':v['level_value_id']}
  for label,v in [('Country',country),('State / FCT',province),('Local Government Area',local)]]}}

def load_geography():
 # The worker already uses this connection for deterministic-ID reconciliation.
 import sys
 sys.path.insert(0,'/opt/openg2p-lab/registration')
 import registration_app as r
 with r.pg('master_data') as c:
  c.set_session(readonly=True)
  with c.cursor() as q:
   q.execute('SELECT row_to_json(v) FROM g2p_geo_level_values v')
   return [row[0] for row in q.fetchall()]
