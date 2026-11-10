from pathlib import Path
p=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/android/src/org/nigeriag2p/field/MainActivity.java')
s=p.read_text(encoding='utf8')
s=s.replace('if(!oldLat.equals(val("lat"))||!oldLon.equals(val("lon")))set(record,"accuracy","");inputs.clear();}', 'if(!oldLat.equals(val("lat"))||!oldLon.equals(val("lon")))set(record,"accuracy","");}')
s=s.replace('void screen(String title){root=', 'void screen(String title){cancelLocation();root=')
s=s.replace('void captureLocation(){if(checkSelfPermission', 'void cancelLocation(){if(gpsListener!=null){try{((LocationManager)getSystemService(LOCATION_SERVICE)).removeUpdates(gpsListener);}catch(Exception ignored){}gpsListener=null;}}\n void captureLocation(){cancelLocation();if(checkSelfPermission')
s=s.replace('public void onLocationChanged(Location location){set(record,"lat"', 'public void onLocationChanged(Location location){harvest();set(record,"lat"')
p.write_text(s,encoding='utf8')
