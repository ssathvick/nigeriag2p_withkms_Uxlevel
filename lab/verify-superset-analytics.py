from superset import create_app,db
app=create_app()
with app.app_context():
 from superset.models.dashboard import Dashboard
 from superset.models.core import Database
 from flask_login import login_user
 database=db.session.query(Database).filter_by(database_name='Nigeria G2P Analytics').one()
 assert not database.allow_dml and not database.expose_in_sqllab
 dashboard=db.session.query(Dashboard).filter_by(slug='nigeria-platform-analytics').one()
 assert len(dashboard.slices)==3
 with app.test_request_context('/superset/dashboard/nigeria-platform-analytics/'):
  sm=app.appbuilder.sm
  admins=[u for u in sm.get_all_users() if any(role.name=='Admin' for role in u.roles)]
  assert admins
  login_user(admins[0])
  from flask import g
  g.user=admins[0]
  import json
  from superset.common.query_context_factory import QueryContextFactory
  from superset.commands.chart.data.get_data_command import ChartDataCommand
  for chart in dashboard.slices:
   context=QueryContextFactory().create(**json.loads(chart.query_context))
   command=ChartDataCommand(context);command.validate();payload=command.run()
   assert all(not result.get('error') for result in payload['queries']), 'Chart query failed'
   print(chart.slice_name,'query successful')
 print('Dashboard and read only reporting connection verified.')
