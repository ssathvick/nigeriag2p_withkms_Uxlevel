from pathlib import Path
root=Path(__file__).resolve().parents[1]/'field-app'
p=root/'build_form.py';s=p.read_text();s=s.replace("['text','sample_reference'", "['text','household_name','Household name','Enter a fictional household name for this demonstration.','yes'],\n['text','household_head_name','Household head name','Enter a fictional head name for this demonstration.','yes'],\n['text','sample_reference'")
s=s.replace('2026110401','2026111001').replace("concat('SAMPLE ', ${sample_reference})","concat(${household_head_name}, ' - ', ${sample_reference})").replace('Review: ${sample_reference}', 'Review: ${household_name}, head ${household_head_name}, reference ${sample_reference}')
p.write_text(s)
src=root/'android/src/org/nigeriag2p/field'
for p in [src/'MainActivity.java',src/'ManualUpload.java']:
 s=p.read_text().replace('2026110401','2026111001')
 accessor='val' if p.name=='MainActivity.java' else 'r.optString'
 s=s.replace('+tag("sample_reference",', '+tag("household_name",'+accessor+'("household_name"))+tag("household_head_name",'+accessor+'("head_name"))+tag("sample_reference",')
 s=s.replace('"SAMPLE "+'+accessor+'("ref")',accessor+'("head_name")+" - "+'+accessor+'("ref")')
 if p.name=='MainActivity.java':
  s=s.replace('screen("Household visit")','screen("Household Intake Form")')
  s=s.replace('r.optString("ref","Unfinished sample")','r.optString("head_name",r.optString("ref","Unfinished sample"))')
  s=s.replace('field("Sample reference","ref",0);','field("Household name","household_name",0);field("Household head name","head_name",0);field("Sample reference","ref",0);')
  s=s.replace('return "Reference: "','return "Household: "+val("household_name")+"\\nHead: "+val("head_name")+"\\nReference: "')
  s=s.replace('"ward","ref","size"','"ward","ref","household_name","head_name","size"')
  s=s.replace('Runnable finishSplash;', 'Runnable finishSplash, gpsTimeout;')
  s=s.replace('void cancelLocation(){','void cancelLocation(){if(gpsTimeout!=null){main.removeCallbacks(gpsTimeout);gpsTimeout=null;}')
  s=s.replace('Waiting for a GPS fix…','Waiting for GPS accuracy of 50 metres or better…')
  s=s.replace('public void onLocationChanged(Location location){harvest();','public void onLocationChanged(Location location){if(!location.hasAccuracy()||location.getAccuracy()>50){status.setText("Waiting for a more accurate fix (target 50 m). You can enter coordinates manually.");return;}cancelLocation();harvest();')
  s=s.replace('lm.requestSingleUpdate(LocationManager.GPS_PROVIDER,gpsListener,null);','lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,1000,0,gpsListener);gpsTimeout=()->{cancelLocation();status.setText("No fix within 50 m accuracy in 30 seconds. Retry outdoors or enter coordinates manually.");};main.postDelayed(gpsTimeout,30000);')
  s=s.replace('protected void onDestroy(){','protected void onDestroy(){cancelLocation();')
 p.write_text(s)
print('Updated names, instance labels and consent-triggered GPS threshold')
