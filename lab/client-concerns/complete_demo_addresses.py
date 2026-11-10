import sys,json
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
root=Path(__file__).parent;backup=Path((root/'backup-location.txt').read_text());samples=json.loads((backup/'synthetic-household-names.json').read_text());changes=[]
with r.pg('register') as c:
 with c.cursor() as q:
  for i,(ident,old,head) in enumerate(samples):
   area=old.split('—')[-1].strip() if '—' in old else 'Nigeria'
   street=['Unity Road','Market Road','School Road','Community Close'][i%4]
   q.execute("UPDATE g2p_register_households SET address_line_1=%s,address_line_2=%s WHERE internal_record_id=%s AND created_by='iqs-synthetic-batch' AND address_line_1 IS NULL",(f'{i+12} {street} (fictional)',area+', Nigeria — demonstration address',ident));changes.append(q.rowcount)
  for i,ident in enumerate(['e6cb6931-b0bb-43cf-9761-b3dda5828c50','b34a1aa0-27d4-4108-afbf-7d7a84371448']):
   q.execute('UPDATE g2p_register_households SET record_name=%s WHERE internal_record_id=%s AND household_head_name=%s',(f'Amina Bello Household (diagnostic sample {i+1})',ident,'Amina Bello'))
 c.commit()
print('Added explicitly fictional addresses to synthetic sample households:',sum(changes))
