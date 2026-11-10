from pathlib import Path
p=Path('test-territory-data.py');s=p.read_text();needle="if __name__=='__main__':unittest.main()"
tests=''' def test_representative_provenance_and_mapping(self):
  directory=d['representatives'];members=directory['members']
  self.assertEqual(len(members),493);self.assertEqual(len({r['id'] for r in members}),493)
  self.assertEqual(collections.Counter(r['chamber'] for r in members),{'Senate':109,'House of Representatives':358,'State House of Assembly':26})
  districts={x['id']:x for x in d['districts']}
  for r in members:
   self.assertEqual(r['classification'],'published');self.assertEqual(r['as_of'],'2026-11-04');self.assertTrue(r['source_url'].startswith('https://'))
   if r['district_id']:
    self.assertEqual(r['chamber'],'Senate');self.assertEqual(districts[r['district_id']]['state_id'],r['state_id'])
   self.assertNotIn('score',r);self.assertNotIn('attendance',r);self.assertNotIn('project_delivery',r)
  self.assertEqual(sum('Conflicting' in r['status'] for r in members),2)
 def test_bills_do_not_transfer_between_people_or_chambers(self):
  from territory_representatives import person
  directory=d['representatives'];seen=set()
  for r in directory['members']:
   for b in r['bills']:
    self.assertEqual(person(r['name']),person(b['sponsor']))
    self.assertGreaterEqual(b['first_reading'],'2023-06-13');self.assertLessEqual(b['first_reading'],directory['as_of'])
    self.assertNotIn((r['chamber'],b['number']),seen);seen.add((r['chamber'],b['number']))
    self.assertEqual(b['reference_year'],int(b['first_reading'][:4]));self.assertEqual(b['classification'],'published')
    self.assertEqual(b['level'],r['level']);self.assertTrue(b['source_url'].startswith('https://billtracker.naltf.gov.ng/bill/'))
    self.assertNotIn('trackedBy',b);self.assertNotIn('deletedBy',b)
  self.assertEqual(len(seen),directory['coverage']['attributed_bill_records'])
  for r in directory['members']:
   if r['chamber']=='State House of Assembly':self.assertEqual(r['bills'],[])
 def test_representative_source_reference_values(self):
  r=next(r for r in d['representatives']['members'] if r['name']=='Hon. Benjamin Okezie Kalu')
  self.assertEqual(r['constituency'],'Bende constituency');self.assertEqual(len(r['bills']),140)
  r=next(r for r in d['representatives']['members'] if r['name']=='Sen. Dayo Faduyile')
  self.assertEqual(r['constituency'],'Ondo South');self.assertNotIn('Ibrahim Jimoh',[b['sponsor'] for b in r['bills']])
'''
s=s.replace(needle,tests+needle);p.write_text(s)
