from pathlib import Path
import json
from openpyxl import load_workbook
root=Path(__file__).parent;wb=load_workbook(root.parent/'field-app/nsipa-field-demo.xlsx');s=wb['settings'];s.cell(2,1,'Household Mapping Verification (fictional)');s.cell(2,2,'nsipa_household_mapping_check');s.cell(2,3,'2026111001')
survey=wb['survey'];row=next(i for i in range(2,survey.max_row+1) if survey.cell(i,2).value=='shelter')+1
survey.insert_rows(row,2)
for offset,(field,attribute,label) in enumerate([('roof_material','ROOF_MATERIAL','Roof material'),('water_source_type','WATER_SOURCE_TYPE','Water source')]):
 for col,val in enumerate(['select_one '+field,field,label,'Controlled verification choice list.'],1):survey.cell(row+offset,col,val)
records=json.loads((root/'screen-verification.json').read_text());master={r['attribute_id']:r['values'] for r in records if 'attribute_id' in r};(root/'mapping-master-values.json').write_text(json.dumps(master,indent=2))
for field,attribute in [('roof_material','ROOF_MATERIAL'),('water_source_type','WATER_SOURCE_TYPE')]:
 for i,value in enumerate(master[attribute],1):wb['choices'].append([field,str(i),value['value_display']])
wb.save(root/'mapping-fixture.xlsx');print('Created isolated numeric-choice verification form; production mobile form unchanged')
