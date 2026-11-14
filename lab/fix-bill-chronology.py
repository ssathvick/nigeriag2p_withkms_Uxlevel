from pathlib import Path
p=Path('territory_representatives.py');s=p.read_text();s=s.replace("    for r in reps:r['bills'].sort(key=lambda b:b['first_reading'],reverse=True)","""    for r in reps:
        for b in r['bills']:
            qualifications=[]
            for key in ['second_reading','third_reading']:
                if b[key] and not b['first_reading']<=b[key]<=AS_OF:
                    qualifications.append(key.replace('_',' ')+' date '+b[key]+' is outside the valid chronology and is excluded from date-based counts.')
                    b[key]=None
            if qualifications:b['date_qualification']=' '.join(qualifications)
        r['bills'].sort(key=lambda b:b['first_reading'],reverse=True)""")
p.write_text(s)
p=Path('persona-ui/src/representatives.jsx');s=p.read_text().replace('<small>Source sponsor: {b.sponsor}</small>','<small>Source sponsor: {b.sponsor}</small>{b.date_qualification&&<small>{b.date_qualification}</small>}');p.write_text(s)
p=Path('test-territory-data.py');s=p.read_text().replace("    self.assertNotIn('trackedBy',b);", "    for key in ['second_reading','third_reading']:\n     if b[key]:self.assertTrue(b['first_reading']<=b[key]<=directory['as_of'])\n    self.assertNotIn('trackedBy',b);");p.write_text(s)
