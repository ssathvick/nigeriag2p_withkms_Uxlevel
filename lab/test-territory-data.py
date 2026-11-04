"""Public release contracts: geography, provenance, missingness and aggregate privacy."""
from pathlib import Path
import json,unittest,collections
R=Path(__file__).parent/'territory-data/public';d=json.loads((R/'data.json').read_text())
class TerritoryData(unittest.TestCase):
 def test_geographic_coverage(self):
  self.assertEqual((len(d['states']),len(d['lgas']),len(d['districts'])),(37,774,109))
  for kind in ['states','lgas','districts']:self.assertEqual(len({a['id'] for a in d[kind]}),len(d[kind]))
  for kind,file in [('states','states.geojson'),('lgas','lgas.geojson')]:
   geo=json.loads((R/file).read_text());self.assertEqual({f['properties']['id'] for f in geo['features']},{a['id'] for a in d[kind]})
 def test_provenance_every_measure(self):
  for a in d['states']+d['lgas']+d['districts']:
   for m in a['metrics'].values():
    self.assertIn(m['source'],d['sources']);self.assertEqual(m['level'],a['level']);self.assertIn(m['classification'],['published','modelled','synthetic']);self.assertIsInstance(m['year'],int);self.assertGreaterEqual(m['value'],0)
    if 'ci' in m:self.assertLessEqual(m['ci'][0],m['value']);self.assertGreaterEqual(m['ci'][1],m['value'])
 def test_no_geographic_inheritance(self):
  for a in d['districts']:self.assertEqual(set(a['metrics']),{'poverty','mpi','poor_people'})
  for a in d['lgas']:self.assertLessEqual(set(a['metrics']),{'health','population'})
  self.assertEqual(d['coverage']['district_boundary_mappings'],0)
  for x in d['crosswalk']:
   if x['from'].startswith('NBS-SD'):self.assertFalse(x['can_allocate']);self.assertEqual(x['relation'],'state association only')
 def test_district_codebook_crosswalk(self):
  for a in d['districts']:self.assertEqual(a['state_id'],'NG'+str(int(a['code'])//10).zfill(2))
  c=collections.Counter(a['state_id'] for a in d['districts']);self.assertEqual(c.pop('NG37'),1);self.assertEqual(set(c.values()),{3})
  self.assertEqual(len([a for a in d['districts'] if a['name']=='Osun West']),1)
 def test_population_not_duplicated(self):
  c=d['coverage']['population'];self.assertAlmostEqual(c['assigned']+c['unassigned'],c['raster_total'],delta=1)
  self.assertAlmostEqual(sum(a['metrics']['population']['value'] for a in d['lgas']),c['assigned'],delta=388)
  self.assertEqual(sum(a['metrics']['population']['value'] for a in d['lgas']),sum(a['metrics']['population']['value'] for a in d['states']))
 def test_health_missing_not_zero(self):
  missing=[a for a in d['lgas'] if 'health' not in a['metrics']];self.assertEqual(len(missing),5)
  self.assertEqual(sum(s['metrics']['health']['value'] for s in d['states']),sum(a['metrics']['health']['value'] for a in d['lgas'] if 'health' in a['metrics'])+sum(a['count'] for a in d['coverage']['health_unmatched_lgas']))
 def test_borno_qualification(self):
  areas=[a for a in d['states']+d['districts'] if a['id']=='NG08' or a.get('state_id')=='NG08'];self.assertEqual(len(areas),4)
  for a in areas:self.assertIn('not representative',a['caveat'])
 def test_reference_values(self):
  abia=next(a for a in d['districts'] if a['name']=='Abia Central');self.assertEqual(abia['metrics']['poverty']['value'],26.4);self.assertEqual(abia['metrics']['poor_people']['value'],467000)
  lagos=next(a for a in d['states'] if a['name']=='Lagos');self.assertEqual(lagos['metrics']['project_budget']['value'],5420000000);self.assertEqual(lagos['metrics']['projects']['value'],47)
  self.assertEqual(d['projects'][0]['allocation']['value'],100000000)
 def test_public_programme_allowlist(self):
  self.assertTrue(d['programmes'])
  for p in d['programmes']:self.assertEqual(set(p),{'name','metric'});self.assertEqual(p['metric']['classification'],'synthetic');self.assertEqual(p['metric']['level'],'installation-wide')
  raw=(R/'data.json').read_text().lower()
  for forbidden in ['given_name','family_name','bank_account','national_id','latitude','longitude','household_ref','password','client_secret','access_token','email','phone']:
   self.assertNotIn('"'+forbidden+'"',raw)
 def test_no_invented_economy(self):
  for a in d['lgas']+d['districts']:self.assertFalse({'gdp','gdp_share','gdp_per_capita','crop_share','gva','income','jobs'} & set(a['metrics']))
  for a in d['states']:self.assertFalse({'gva','income','jobs'} & set(a['metrics']))
 def test_economic_coverage_and_values(self):
  for key,count in [('gdp',3),('gdp_share',6),('gdp_per_capita',6)]:self.assertEqual(sum(key in a['metrics'] for a in d['states']),count)
  lagos=next(a for a in d['states'] if a['name']=='Lagos')
  self.assertEqual(lagos['metrics']['gdp']['value'],33100000000000)
  self.assertEqual(lagos['metrics']['gdp_per_capita']['value'],2100000)
  self.assertNotIn('crop_share',lagos['metrics'])
  self.assertEqual(lagos['metrics']['trade_share']['value'],70.9)
  for a in d['states']:
   self.assertEqual(len(a['economic_sectors']),3)
   self.assertLessEqual(sum(a['metrics'][s['key']]['value'] for s in a['economic_sectors']),100.1)
   for s in a['economic_sectors']:
    m=a['metrics'][s['key']];self.assertEqual(m['source'],'state_sectors');self.assertEqual(m['year'],2023);self.assertEqual(m['classification'],'published')
 def test_independent_report_coverage_and_reconciliation(self):
  reports=d['economic_reports'];self.assertEqual(len(reports),61)
  self.assertEqual(len({r['state_id'] for r in reports}),37)
  for r in reports:
   if r['id']=='lagos-ledu-2024-forecast':
    self.assertEqual(r['gdp_per_capita']['value'],5043);self.assertEqual(r['gdp_per_capita']['classification'],'modelled');self.assertEqual(r['gdp_per_capita']['unit'],'PPP US$ per person');self.assertEqual(r['gdp']['value'],54770000000000);continue
   if r['id'].startswith('ngf-'):
    self.assertEqual(r['sectors'],[]);self.assertNotIn('gdp_per_capita',r);self.assertNotIn('population',r);self.assertIn('unspecified',r['basis']);continue
   self.assertEqual(len(r['sectors']),52);self.assertEqual(sum(s['group'] for s in r['sectors']),19)
   self.assertEqual(r['gdp']['year'],r['year']);self.assertIn(r['source'],d['sources'])
   for s in r['sectors']:
    if s['metric']:
     self.assertEqual(s['metric']['source'],r['source']);self.assertEqual(s['metric']['year'],r['year']);self.assertEqual(s['metric']['level'],'state');self.assertGreaterEqual(s['metric']['value'],0)
    else:self.assertTrue(s['missing_reason'])
   if r['sector_unit']=='NGN':self.assertLessEqual(abs(r['reconciliation_difference_ngn']),100000)
 def test_delta_same_year_per_capita(self):
  r=next(r for r in d['economic_reports'] if r['id']=='delta-2022')
  self.assertEqual(r['gdp']['value'],4871008780000)
  self.assertEqual(r['gdp_per_capita']['value'],777637.4)
  self.assertEqual(r['population']['value'],6374321)
  self.assertAlmostEqual(r['gdp_market']['value']/r['population']['value'],r['gdp_per_capita']['value'],delta=.02)
  self.assertEqual({r[k]['year'] for k in ['gdp_market','population','gdp_per_capita']},{2022})
 def test_source_conflicts_kept_separate(self):
  jigawa=next(s for s in d['states'] if s['name']=='Jigawa')
  self.assertNotIn('gdp',jigawa['metrics'])
  r=next(r for r in d['economic_reports'] if r['id']=='jigawa-2023')
  self.assertEqual(r['gdp']['value'],5650421320000)
  self.assertEqual(next(s['metric']['value'] for s in r['sectors'] if s['name']=='Agriculture'),36.6)
  self.assertEqual(next(s['metric']['value'] for s in r['sectors'] if s['name']=='Crop Production'),25.94)
  self.assertEqual(jigawa['metrics']['crop_share']['value'],48.8)
  self.assertTrue(any('33.60%' in n for n in r['notes']))
  self.assertIsNone(next(s['metric'] for s in r['sectors'] if s['name']=='Electricity, Gas, Steam And Air Conditioning Supply'))
  self.assertEqual(next(s['metric']['value'] for s in r['sectors'] if s['name']=='Mining And Quarrying'),0)
 def test_representative_provenance_and_mapping(self):
  directory=d['representatives'];members=directory['members']
  self.assertGreater(len(members),739);self.assertEqual(len({r['id'] for r in members}),len(members))
  offices=collections.Counter(r['chamber'] for r in members)
  self.assertEqual(offices['Senate'],109);self.assertEqual(offices['House of Representatives'],358)
  self.assertEqual(offices['Governor'],36);self.assertEqual(offices['FCT Minister (appointed)'],1)
  self.assertEqual(offices['State House of Assembly'],506)
  districts={x['id']:x for x in d['districts']}
  for r in members:
   self.assertEqual(r['classification'],'published');self.assertEqual(r['as_of'],'2026-11-04');self.assertTrue(r['source_url'].startswith('https://'))
   if r['district_id']:
    self.assertEqual(r['chamber'],'Senate');self.assertEqual(districts[r['district_id']]['state_id'],r['state_id'])
   self.assertNotIn('score',r);self.assertNotIn('attendance',r);self.assertNotIn('project_delivery',r)
  self.assertGreaterEqual(sum('Conflicting' in r['status'] for r in members),6)
  self.assertEqual(len(directory['state_coverage']),37)
  self.assertEqual(directory['coverage']['assembly_states'],36)
  for r in members:
   for e in r['evidence']:
    self.assertLessEqual(e['date'],directory['as_of']);self.assertEqual(e['classification'],'published')
    self.assertTrue(e['source_url'].startswith('https://'));self.assertTrue(e['qualification'])
    self.assertEqual(e['reference_year'],int(e['date'][:4]));self.assertTrue(e['attribution'])
 def test_expanded_sources_and_activity(self):
  members=d['representatives']['members'];assembly=[r for r in members if r['chamber']=='State House of Assembly']
  self.assertEqual(sum(r['state_name']=='Lagos' for r in assembly),40)
  self.assertEqual(sum(r['state_name']=='Jigawa' for r in assembly),30)
  self.assertFalse(any('Kundila' in r['name'] for r in assembly))
  for r in assembly:
   if r.get('source_date'):
    self.assertLessEqual(r['source_date'],d['representatives']['as_of'])
    self.assertEqual(r['reference_year'],int(r['source_date'][:4]))
  saheed=next(r for r in assembly if r['state_name']=='Lagos' and 'FEMI SAHEED' in r['name'])
  self.assertEqual(saheed['constituency'],'Kosofe II')
  e=next(e for e in saheed['evidence'] if e['id']=='lagos-wealth-review-20260604')
  self.assertIn('not proof of assent',e['summary']);self.assertEqual(e['category'],'Legislative review')
  unique={e['id'] for r in members for e in r['evidence']}
  self.assertEqual(len(unique),d['representatives']['coverage']['activity_records'])
 def test_bills_do_not_transfer_between_people_or_chambers(self):
  from territory_representatives import person
  directory=d['representatives'];seen=set()
  for r in directory['members']:
   for b in r['bills']:
    self.assertEqual(person(r['name']),person(b['sponsor']))
    if b['number'].upper().startswith('SB'):self.assertEqual(r['chamber'],'Senate')
    if b['number'].upper().startswith('HB'):self.assertEqual(r['chamber'],'House of Representatives')
    self.assertGreaterEqual(b['first_reading'],'2023-06-13');self.assertLessEqual(b['first_reading'],directory['as_of'])
    self.assertNotIn((r['chamber'],b['number']),seen);seen.add((r['chamber'],b['number']))
    self.assertEqual(b['reference_year'],int(b['first_reading'][:4]));self.assertEqual(b['classification'],'published')
    self.assertEqual(b['level'],r['level']);self.assertTrue(b['source_url'].startswith('https://billtracker.naltf.gov.ng/bill/'))
    for key in ['second_reading','third_reading']:
     if b[key]:self.assertTrue(b['first_reading']<=b[key]<=directory['as_of'])
    self.assertNotIn('trackedBy',b);self.assertNotIn('deletedBy',b)
  self.assertEqual(len(seen),directory['coverage']['attributed_bill_records'])
  for r in directory['members']:
   if r['chamber']=='State House of Assembly':self.assertEqual(r['bills'],[])
 def test_representative_source_reference_values(self):
  r=next(r for r in d['representatives']['members'] if r['name']=='Hon. Benjamin Okezie Kalu')
  self.assertEqual(r['constituency'],'Bende constituency');self.assertEqual(len(r['bills']),139)
  r=next(r for r in d['representatives']['members'] if r['name']=='Sen. Dayo Faduyile')
  self.assertEqual(r['constituency'],'Ondo South');self.assertNotIn('Ibrahim Jimoh',[b['sponsor'] for b in r['bills']])
 def test_constituency_reviews_and_successor_isolation(self):
  directory=d['representatives'];members=directory['members']
  assembly=[r for r in members if r['chamber']=='State House of Assembly']
  self.assertEqual(sum(not r['constituency'] for r in assembly),25)
  reviewed=[r for r in members if r.get('constituency_evidence')]
  self.assertEqual(len(reviewed),49)
  for r in reviewed:
   e=r['constituency_evidence'];self.assertEqual(e['classification'],'published')
   self.assertTrue(e['source_url'].startswith('https://'));self.assertLessEqual(e['reference_year'],2026)
   if e.get('source_date'):self.assertLessEqual(e['source_date'],directory['as_of'])
  self.assertTrue(any(r['constituency_evidence']['reference_year']==2023 for r in reviewed))
  for state in ['Imo','Oyo']:
   self.assertFalse(any(not r['constituency'] for r in assembly if r['state_name']==state))
  self.assertEqual(sum(r['state_name']=='Rivers' for r in assembly),32)
  old=next(r for r in directory['archived_members'] if r['id']=='office-79207b99ffa3')
  self.assertNotIn(old['id'],{r['id'] for r in members});self.assertTrue(old['evidence'])
  successor=next(r for r in assembly if r['state_name']=='Kano' and 'Datti' in r['name'])
  self.assertFalse({e['id'] for e in old['evidence']} & {e['id'] for e in successor['evidence']})
if __name__=='__main__':unittest.main()
