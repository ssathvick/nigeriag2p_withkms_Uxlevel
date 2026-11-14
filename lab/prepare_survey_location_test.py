from pathlib import Path
p=Path(__file__).parent;source=(p/'test_household_survey_parity.py').read_text();source=source.replace('household-parity-test.json','household-parity-location-test.json').replace("'record_name':'Meeting Verification Household Survey Parity'","'record_name':'Meeting Verification Household Location Parity'").replace("'registration_confirmed':'YES'","'registration_confirmed':'YES','latitude':9.0765,'longitude':7.3986,'location_accuracy_m':12,'location_captured_at':'2026-11-12T19:00:00Z','location_capture_source':'Fictional browser location verification','geo_lowest_level_value_id':'NG001001_eziama'")
anchor="check('Final approval publishes household, crops, assets and enriched member fields to native master records')"
extra='''with connect() as c:
 with c.cursor() as q:
  q.execute('SELECT latitude,longitude,location_accuracy_m,location_captured_at,geo_lowest_level_value_id FROM g2p_register_households WHERE internal_record_id=%s',(state['internal_id'],));row=q.fetchone();assert float(row[0])==9.0765 and float(row[1])==7.3986 and float(row[2])==12 and row[3]=='2026-11-12T19:00:00Z' and row[4]=='NG001001_eziama'
check('Final approval preserves GPS precision, accuracy, device time and selected ward in master registry')
'''
source=source.replace(anchor,anchor+'\n'+extra);(p/'test_household_survey_location_publication.py').write_text(source)
