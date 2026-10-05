exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/test-signed-mapper.py').read())
import copy
records=json.load(open('/opt/openg2p-lab/nigeria-fixtures.json'))
links=[]
for index in range(1,7):
 row=copy.deepcopy(link_payload['request_body']['request_payload']['link_request'][0]);row.update({'reference_id':'ng-lab-link-'+str(index),'id':'NG-LAB-'+str(index).zfill(4),'name':'Synthetic Nigeria Beneficiary '+str(index)})
 row['fa']['account_number']='LAB-'+str(index).zfill(6);links.append(row)
link_payload['request_body']['request_payload']['link_request']=links
signed_call('/mapper/link',link_payload)
