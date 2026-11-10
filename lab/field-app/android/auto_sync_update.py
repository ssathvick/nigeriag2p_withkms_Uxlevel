from pathlib import Path
base=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/android')
p=base/'src/org/nigeriag2p/field/MainActivity.java';s=p.read_text(encoding='utf-8-sig')
a=s.index(' javax.crypto.SecretKey secret()');b=s.index(' void alert(',a)
s=s[:a]+''' String endpoint="";void load(){synchronized(FieldStore.LOCK){try{JSONObject all=FieldStore.read(this);records=all.getJSONArray("records");endpoint=all.optString("endpoint","");}catch(Exception e){alert("Storage error","Could not open device storage.");}}}
 void store(){synchronized(FieldStore.LOCK){try{JSONObject all=FieldStore.read(this);FieldStore.mergeSent(all,records);all.put("records",records);all.put("endpoint",endpoint);FieldStore.write(this,all);}catch(Exception e){alert("Storage error","Could not save on this device.");}}}
'''+s[b:]
s=s.replace('loadCatalog();load();home();','loadCatalog();load();UploadJob.schedule(this);home();')
s=s.replace('void home(){screen(', 'void home(){load();screen(')
s=s.replace('endpoint=s.replaceAll("/+$","");store();home();','endpoint=s.replaceAll("/+$","");store();UploadJob.schedule(this);home();')
s=s.replace('set(record,"reviewer","demo-supervisor");save();home();','set(record,"reviewer","demo-supervisor");save();UploadJob.schedule(this);home();')
s=s.replace('body.addView(text("Status: "+val("status"),16));','body.addView(text("Status: "+val("status")+(val("sync_error").isEmpty()?"":" · Last upload: "+val("sync_error")),16));')
s=s.replace('button(body,"Send approved sample to ODK",()->sync());','body.addView(text("Queued for automatic upload when online. Android may delay background work.",14));button(body,"Retry upload",()->sync());')
a=s.index(' void sync(){');s=s[:a]+''' void sync(){if(endpoint.isEmpty()){alert("Connection required","Set the ODK test project App User URL first.");return;}UploadJob.schedule(this);alert("Upload queued","Android will retry approved samples when network access is available. Refresh the workspace to check the status.");}
}
'''
p.write_text(s,encoding='utf8')
p=base/'AndroidManifest.xml';s=p.read_text();s=s.replace('android:versionCode="2" android:versionName="0.2-demo"','android:versionCode="3" android:versionName="0.3-demo"');s=s.replace('<uses-permission android:name="android.permission.INTERNET"/>','<uses-permission android:name="android.permission.INTERNET"/><uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/><uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>');s=s.replace('<activity android:name=".MainActivity"','<service android:name=".UploadJob" android:permission="android.permission.BIND_JOB_SERVICE" android:exported="false"/><activity android:name=".MainActivity"');p.write_text(s)
p=base/'build.sh';s=p.read_text().replace('src/org/nigeriag2p/field/MainActivity.java','src/org/nigeriag2p/field/*.java');s=s.replace("sed -i '1s/^\\xEF\\xBB\\xBF//' src/org/nigeriag2p/field/*.java","sed -i '1s/^\\xEF\\xBB\\xBF//' src/org/nigeriag2p/field/*.java");p.write_text(s)
