from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
from pathlib import Path
root=Path(__file__).parent
wb=Workbook();ws=wb.active;ws.title='survey'
cols=['type','name','label','hint','required','relevant','constraint','constraint_message','appearance','calculation']
rows=[
['start','start'],['end','end'],['deviceid','deviceid'],['username','collector_username'],
['begin_group','visit','1. Visit and consent','','','','','','field-list'],
['note','demo_notice','DEMONSTRATION ONLY: enter fictional sample information. Do not collect national identity numbers, financial account numbers, medical details or real personal data.'],
['text','enumerator_id','Enumerator ID','Use your assigned field ID.','yes'],
['date','visit_date','Visit date','','yes','','. <= today()','Visit date cannot be in the future.'],
['select_one consent','consent','Has the household agreed to this interview?','Explain the purpose and voluntary nature before proceeding.','yes'],
['note','no_consent','Consent was not given. Do not collect household details; end this interview.','','','${consent} = "no"'],['end_group'],
['begin_group','location','2. Location','','','${consent} = "yes"','','','field-list'],
['text','state','State or FCT','Enter the state name.','yes'],['text','lga','Local government area','Enter the LGA name.','yes'],['text','ward','Ward or community','Enter the locally used name.','yes'],
['geopoint','coordinates','Location (optional)','Capture only when appropriate and with permission.'],['end_group'],
['begin_group','household','3. Household','','','${consent} = "yes"','','','field-list'],
['text','household_name','Household name','Enter a fictional household name for this demonstration.','yes'],
['text','household_head_name','Household head name','Enter a fictional head name for this demonstration.','yes'],
['text','sample_reference','Sample household reference','Use a non-identifying sample code.','yes'],
['integer','household_size','Number of household members','','yes','','. >= 1 and . <= 40','Enter a number from 1 to 40.'],
['integer','children','Number of children under 18','','yes','','. >= 0 and . <= ${household_size}','Enter a number no greater than household size.'],
['select_one shelter','shelter','Main shelter type','','yes'],['end_group'],
['begin_group','livelihood','4. Livelihood and needs','','','${consent} = "yes"','','','field-list'],
['select_one livelihood','livelihood_type','Main livelihood','','yes'],['select_multiple needs','priority_needs','Priority support needs','Choose all that apply.','yes'],
['text','notes','Additional non-sensitive notes (optional)','Do not include names, identity numbers or medical details.'],['end_group'],
['begin_group','review','5. Review and confirmation','','','${consent} = "yes"','','','field-list'],
['note','summary','Review: ${household_name}, head ${household_head_name}, reference ${sample_reference} in ${ward}, ${lga}, ${state}. Household members: ${household_size}; children: ${children}.'],
['select_one confirm','review_confirmation','Has the completed sample form been reviewed and confirmed?','This is an on-device confirmation, not verified independent supervisor approval.','yes','','. = "yes"','Review the completed draft before confirming.'],
['end_group'],['note','next_steps','To pause, save as draft. After review, finalize to keep the form on the device. Send finalized forms when online. Server review is separate.']]
for r in [cols]+rows:ws.append(r+['']*(len(cols)-len(r)))
c=wb.create_sheet('choices'); c.append(['list_name','name','label']);
for row in [('consent','yes','Yes'),('consent','no','No'),('shelter','owned','Owned'),('shelter','rented','Rented'),('shelter','shared','Shared or hosted'),('shelter','other','Other'),('livelihood','agriculture','Agriculture'),('livelihood','wage','Wage work'),('livelihood','self_employed','Self-employment'),('livelihood','none','No current livelihood'),('livelihood','other','Other'),('needs','food','Food support'),('needs','education','Education'),('needs','livelihood','Livelihoods'),('needs','housing','Housing'),('needs','other','Other'),('confirm','yes','Reviewed and confirmed'),('confirm','no','Not yet')]:c.append(row)
s=wb.create_sheet('settings');s.append(['form_title','form_id','version','instance_name']);s.append(['Household Intake Form','nsipa_field_household_demo','2026111001',"concat(${household_head_name}, ' - ', ${sample_reference})"])
for sh in wb:
 sh.freeze_panes='A2';sh.auto_filter.ref=sh.dimensions
 for cell in sh[1]:cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='075D49');cell.alignment=Alignment(wrap_text=True)
 for col in sh.columns:
  length=min(55,max(14,max(len(str(x.value or '')) for x in col)+2));sh.column_dimensions[get_column_letter(col[0].column)].width=length
wb.save(root/'nsipa-field-demo.xlsx')
