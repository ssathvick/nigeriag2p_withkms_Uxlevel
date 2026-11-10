// Operator-invoked adapter. Authentication and immutable source retrieval belong to the caller.
const reg='a0000000-0000-4000-8000-000000000002',form='c1000000-0000-4000-8000-000000000002';
async function importMapped(post,mapped,receipt,persist){
 if(receipt.source_sha256&&receipt.source_sha256!==mapped.source_sha256)throw Error('Source changed: review the new ODK version rather than overwriting an imported record');
 Object.assign(receipt,{source_sha256:mapped.source_sha256,odk_instance_id:mapped.odk_instance_id,form_id:mapped.form_id,mapping_version:mapped.mapping_version,internal_record_id:mapped.payload.internal_record_id});persist();
 if(receipt.submission_id)return {...receipt,reused:true};
 if(receipt.create_attempted)throw Error('Previous create outcome is uncertain. Reconcile the deterministic record ID before retrying; no duplicate submission was created.');
 receipt.create_attempted=true;persist();
 const created=await post('intake-form/save-intake-form-submission',{submission_id:null,section_id:'hh_composition_headship',section_register_id:reg,register_id:reg,form_id:form,section_payload:[{...mapped.payload,edit_action:'ADD',link_internal_record_id:''}]});
 receipt.submission_id=created.submission_id;persist();
 return {...receipt,reused:false};
}
module.exports={importMapped,reg,form};
