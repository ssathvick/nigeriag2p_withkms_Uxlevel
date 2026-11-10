from pathlib import Path
p=Path('test-territory-data.py')
s=p.read_text().replace("offices['State House of Assembly'],446", "offices['State House of Assembly'],506")
insert=''' def test_constituency_reviews_and_successor_isolation(self):
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
'''
s=s.replace("if __name__=='__main__':unittest.main()",insert+"if __name__=='__main__':unittest.main()")
p.write_text(s)
