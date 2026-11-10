"""Run inside Superset with a private temporary connection file."""
import json
from pathlib import Path
from sqlalchemy.engine.url import URL
from superset import create_app,db
app=create_app()
with app.app_context():
 from superset.models.core import Database
 from superset.connectors.sqla.models import SqlaTable,SqlMetric
 from superset.models.slice import Slice
 from superset.models.dashboard import Dashboard
 cfg=json.loads(Path('/tmp/iqs-analytics-connection.json').read_text())['superset']
 database=db.session.query(Database).filter_by(database_name='Nigeria G2P Analytics').one_or_none()
 if not database:
  database=Database(database_name='Nigeria G2P Analytics');db.session.add(database)
 database.sqlalchemy_uri=str(URL.create('postgresql+psycopg2',username=cfg['user'],password=cfg['password'],host=cfg['host'],port=5432,database=cfg['dbname']))
 database.expose_in_sqllab=False;database.allow_dml=False;database.allow_ctas=False;database.allow_cvas=False;database.allow_file_upload=False
 db.session.commit()
 datasets={}
 for name,metric,expr in [('aggregate_metrics','total','SUM(value)'),('knowledge_daily_usage','events','SUM(events)'),('knowledge_governance','articles','SUM(articles)')]:
  table=db.session.query(SqlaTable).filter_by(database_id=database.id,table_name=name,schema='public').one_or_none()
  if not table:
   table=SqlaTable(table_name=name,schema='public',database=database);db.session.add(table);db.session.flush()
  table.fetch_metadata();table.cache_timeout=0
  if name=='aggregate_metrics':
   table.sql="SELECT source,metric,label,value,refreshed_at,(stale OR refreshed_at IS NULL OR refreshed_at < CURRENT_TIMESTAMP - INTERVAL '30 minutes') AS stale FROM public.aggregate_metrics"
  if not any(m.metric_name==metric for m in table.metrics):table.metrics.append(SqlMetric(metric_name=metric,expression=expr))
  datasets[name]=table
 db.session.commit()
 charts=[]
 definitions=[
  ('OpenG2P source measures','aggregate_metrics',['source','metric','label','value','refreshed_at','stale']),
  ('Knowledge publishing status','knowledge_governance',['module','status','articles','live','refreshed_at']),
  ('Knowledge daily usage and feedback','knowledge_daily_usage',['day','module','article','version','event_name','helpful','events','zero_results'])]
 for title,name,columns in definitions:
  chart=db.session.query(Slice).filter_by(slice_name=title,datasource_id=datasets[name].id).one_or_none()
  if not chart:chart=Slice(slice_name=title,datasource_id=datasets[name].id,datasource_type='table');db.session.add(chart)
  chart.viz_type='table';chart.cache_timeout=0
  chart.description='Aggregate sandbox data. Backend status is not confirmed settlement. UTC dates; 15 minute refresh. Intake filters apply only in the native Analytics workspace.'
  chart.params=json.dumps({'viz_type':'table','datasource':str(datasets[name].id)+'__table','query_mode':'raw','all_columns':columns,'row_limit':10000,'time_range':'No filter','order_by_cols':[],'adhoc_filters':[],'server_pagination':False})
  chart.query_context=json.dumps({'datasource':{'id':datasets[name].id,'type':'table'},'force':False,'queries':[{'columns':columns,'metrics':[],'filters':[],'time_range':'No filter','row_limit':10000,'order_desc':True,'extras':{'having':'','where':''}}],'form_data':json.loads(chart.params),'result_format':'json','result_type':'full'})
  charts.append(chart)
 db.session.commit()
 dashboard=db.session.query(Dashboard).filter_by(slug='nigeria-platform-analytics').one_or_none()
 if not dashboard:dashboard=Dashboard(slug='nigeria-platform-analytics',dashboard_title='Nigeria G2P Operations and Knowledge Analytics');db.session.add(dashboard)
 dashboard.slices=charts;dashboard.published=True
 dashboard.description='Operational source summaries and knowledge governance and library usage. Data is synthetic. Settlement remains unvalidated.'
 pos={'DASHBOARD_VERSION_KEY':'v2','ROOT_ID':{'id':'ROOT_ID','type':'ROOT','children':['GRID_ID']},'GRID_ID':{'id':'GRID_ID','type':'GRID','children':[],'parents':['ROOT_ID']},'HEADER_ID':{'id':'HEADER_ID','type':'HEADER','meta':{'text':dashboard.dashboard_title}}}
 for i,chart in enumerate(charts):
  row='ROW-'+str(i);cid='CHART-'+str(chart.id);pos['GRID_ID']['children'].append(row)
  pos[row]={'id':row,'type':'ROW','children':[cid],'parents':['ROOT_ID','GRID_ID'],'meta':{'background':'BACKGROUND_TRANSPARENT'}}
  pos[cid]={'id':cid,'type':'CHART','children':[],'parents':['ROOT_ID','GRID_ID',row],'meta':{'chartId':chart.id,'sliceName':chart.slice_name,'width':12,'height':65}}
 dashboard.position_json=json.dumps(pos);dashboard.json_metadata=json.dumps({'refresh_frequency':900,'timed_refresh_immune_slices':[],'expanded_slices':{},'default_filters':'{}','color_scheme':'supersetColors'})
 db.session.commit()
 # Existing Superset permissions remain authoritative; no Public or user roles are expanded.
 print('Superset analytics dashboard configured:',dashboard.slug,'datasets:',len(datasets),'charts:',len(charts))
