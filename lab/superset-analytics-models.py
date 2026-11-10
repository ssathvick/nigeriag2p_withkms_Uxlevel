from superset import create_app
app=create_app()
with app.app_context():
 from superset.models.core import Database
 from superset.connectors.sqla.models import SqlaTable,TableColumn,SqlMetric
 from superset.models.slice import Slice
 from superset.models.dashboard import Dashboard
 for model in [Database,SqlaTable,TableColumn,SqlMetric,Slice,Dashboard]:
  print(model.__name__,[(c.name,str(c.type)) for c in model.__table__.columns])
