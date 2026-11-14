import test_meeting_native_workflow as t
sid='718cc3ad-7f81-46cb-aea0-2696bb15e732'
for target in ['register','intake-form']:
 value,_=t.call('aarin@gmail.com','intake-form/get-deduplication-intake-form-'+target+'-results',{'submission_id':sid})
 rows=value if isinstance(value,list) else value.get('results',[])
 if target=='register':assert rows and any(row.get('field_matches') for row in rows)
 t.check('Native '+target+' duplicate comparisons return readable field-level evidence')
