"""Exact-source, explicitly authorized synthetic enrichment for five legacy demos."""
import hashlib,xml.etree.ElementTree as ET
from odk_household_mapping import parse_xml,map_submission
def map_legacy(xml,definition,master,review):
 data=parse_xml(xml);original=parse_xml(definition).find('./head/model/instance/data')
 if hashlib.sha256(xml).hexdigest()!=review['source_sha256']:raise ValueError('Legacy source hash changed')
 if hashlib.sha256(definition).hexdigest()!=review['definition_sha256']:raise ValueError('Legacy definition hash changed')
 if original is None or data.get('id')!=review['form_id'] or data.get('version')!=review['form_version'] or original.get('id')!=review['form_id'] or original.get('version')!=review['form_version']:raise ValueError('Legacy form identity mismatch')
 if data.findtext('meta/instanceID')!=review['instance_id']:raise ValueError('Legacy instance mismatch')
 if review.get('authorization')!='User explicitly requested synthetic household and head names':raise ValueError('Synthetic enrichment not authorized')
 household=data.find('household')
 for field in ['household_name','household_head_name']:
  if household.findtext(field):raise ValueError('Do not overwrite an existing source name')
  value=review['synthetic_names'][field]
  if not value.startswith('Synthetic '):raise ValueError('Synthetic label required')
  node=household.find(field)
  if node is None:node=ET.SubElement(household,field)
  node.text=value
 normalized=ET.tostring(data);mapped=map_submission(normalized,definition,master)
 mapped.update(mapping_version='2026-11-10.legacy-demo.1',source_sha256=review['source_sha256'],normalized_sha256=hashlib.sha256(normalized).hexdigest(),enrichment={'synthetic':True,'authorization':review['authorization'],'added_fields':review['synthetic_names'],'original_source_preserved':True})
 mapped['notes'].append('Names are user-authorized synthetic demo enrichment, not collected or verified identities. Original ODK XML is unchanged.')
 return mapped
