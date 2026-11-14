"""Use the existing NSIPA green palette in native Registry theme metadata."""
import datetime,json,uuid
from pathlib import Path
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
theme=str(uuid.uuid5(uuid.NAMESPACE_URL,'https://g2p-register.wverve.in/nsipa-native-theme'))
colors={'primary_color_1':'#d4e7d3','primary_color_2':'#205f51','secondary_color_1':'#e9f1e8','secondary_color_2':'#ffffff','secondary_color_3':'#597e72','neutral_color_1':'#155e50','neutral_color_2':'#ffffff'}
backup=Path('/opt/openg2p-lab/registration/native-meeting-backups')/('theme-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,mode=0o700)
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute('SELECT * FROM g2p_registry_configuration FOR UPDATE');configs=q.fetchall();(backup/'configuration.json').write_text(json.dumps(configs,default=str))
  old=configs[0]['registry_theme_id'];q.execute('INSERT INTO registry_themes(theme_id,theme_mnemonic,is_factory_shipped) VALUES(%s,%s,false) ON CONFLICT DO NOTHING',(theme,'NSIPA Master Registry'))
  q.execute('SELECT * FROM registry_theme_values WHERE theme_id=%s',(old,));values=q.fetchall()
  for item in values:
   name=item['attribute_name'];value=colors.get(name,item['attribute_value']);q.execute('SELECT theme_value_id FROM registry_theme_values WHERE theme_id=%s AND attribute_name=%s',(theme,name));existing=q.fetchone()
   if existing:q.execute('UPDATE registry_theme_values SET attribute_value=%s WHERE theme_value_id=%s',(value,existing['theme_value_id']))
   else:q.execute('INSERT INTO registry_theme_values(theme_value_id,theme_id,attribute_name,attribute_value) VALUES(%s,%s,%s,%s)',(str(uuid.uuid4()),theme,name,value))
  q.execute('UPDATE g2p_registry_configuration SET registry_theme_id=%s',(theme,))
 c.commit()
print('Aligned the native registry theme with the existing NSIPA palette; factory themes retained.')
