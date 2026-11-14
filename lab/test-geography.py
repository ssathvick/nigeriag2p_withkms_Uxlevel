import unittest,math
from unittest.mock import patch
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('persona_tests',Path(__file__).with_name('test-persona-workspaces.py'));base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);Permissions,r=base.Permissions,base.r
import nigeria_geography as geo
class Geography(unittest.TestCase):
 def test_all_states_zones(self):
  states=[a for a in geo.AREAS.values() if a['level']=='state'];self.assertEqual(len(states),37);self.assertEqual(len({a['zone_id'] for a in states}),6);self.assertEqual(geo.AREAS['NG37']['zone_name'],'North Central')
 def test_unknown_location_remains_empty(self):
  g=geo.geography({'state':'NG19','community':'Dala'});self.assertEqual(g['zone_name'],'North West');self.assertIsNone(g['lga_id']);self.assertIsNone(g['latitude']);self.assertFalse(g['coordinate_verified'])
 def test_lga_parent_and_coordinate_validation(self):
  for form in [{'lga':'NG2401'},{'latitude':'12'},{'latitude':'nan','longitude':'8'},{'latitude':'91','longitude':'8'},{'accuracy_m':'10'}]:
   with self.subTest(form=form),self.assertRaises(ValueError):geo.capture(form,{'state':'NG19'})
 def test_wgs84_zero_and_reported_accuracy(self):
  g=geo.capture({'lga':'NG1901','latitude':'0','longitude':'0','accuracy_m':'0','ward':'Example ward'},{'state':'NG19'});self.assertEqual(g['latitude'],0);self.assertEqual(g['lga_name'],'Dala');self.assertEqual(g['coordinate_source'],'user_reported');self.assertFalse(g['coordinate_verified'])
 def test_household_geojson_coordinate_order(self):
  from unittest.mock import MagicMock
  fake=MagicMock();cur=fake.pg.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
  keys=['internal_record_id','record_status','zone_id','zone_name','state_id','state_name','lga_id','lga_name','latitude','longitude','coordinate_source'];cur.description=[(k,) for k in keys]
  cur.fetchall.return_value=[('test-household','ACTIVE','NG-NW','North West','NG19','Kano',None,None,12.0,8.5,'user_reported')];cur.fetchone.return_value=(3,);fake.stamp.return_value='test'
  result=geo.household_points(fake);self.assertEqual(result['features'][0]['geometry']['coordinates'],[8.5,12.0]);self.assertEqual(result['metadata']['households_missing_coordinates'],2);self.assertNotIn('name',result['features'][0]['properties'])
 def test_form_render_empty_coordinates(self):
  with r.app.test_request_context('/registration/profile'):
   r.g.user={'name':'Test'};r.g.session={'csrf':'x'}
   from flask import render_template
   html=render_template('profile.html',prefix=r.PREFIX,csrf='x',user=r.g.user,data={},states=[('NG19','Kano')],geocatalogue=geo.CATALOGUE,profile=None)
   self.assertIn('name="latitude"',html);self.assertNotIn('value="Undefined"',html)
class GeoPermissions(Permissions):
 def test_geo_anonymous(self):
  self.client.delete_cookie('IQS-INTAKE');self.assertEqual(self.client.get('/registration/api/geography/summary').status_code,401);self.assertEqual(self.client.get('/registration/api/geography/households.geojson').status_code,401)
 def test_geo_citizen_and_officer_denied(self):
  for mode,sub,roles in [('beneficiary','owner',[]),('staff','officer',['iqs-registration-officer'])]:
   self.login(mode,sub,roles);self.assertEqual(self.client.get('/registration/api/geography/summary').status_code,403);self.assertEqual(self.client.get('/registration/api/geography/households.geojson').status_code,403)
 def test_geo_supervisor_aggregate_only(self):
  self.login('staff','supervisor',['iqs-programme-supervisor'])
  with patch.object(geo,'summary',return_value={'counts':[],'totals':{'individual':0,'household':0}}):self.assertEqual(self.client.get('/registration/api/geography/summary').status_code,200)
if __name__=='__main__':unittest.main()
