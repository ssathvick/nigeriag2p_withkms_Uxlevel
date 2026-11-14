(()=>{
 const state=document.querySelector('select[name="state"]'),lga=document.getElementById('geo-lga');
 if(state&&lga){function update(){for(const option of lga.options){if(!option.value)continue;option.hidden=option.dataset.state!==state.value;option.disabled=option.hidden;if(option.disabled&&option.selected)lga.value=''}}state.addEventListener('change',update);update()}
 const button=document.getElementById('geo-capture'),status=document.getElementById('geo-capture-status'),lat=document.querySelector('[name="latitude"]'),lon=document.querySelector('[name="longitude"]'),accuracy=document.querySelector('[name="accuracy_m"]'),source=document.querySelector('[name="coordinate_source"]');if(!button)return;
 let watch=null,timer=null;function stop(){if(watch!==null)navigator.geolocation.clearWatch(watch);watch=null;clearTimeout(timer);button.disabled=false}
 for(const field of [lat,lon,accuracy])field.addEventListener('input',()=>{stop();source.value='user_reported'});
 window.addEventListener('pagehide',stop);
 button.addEventListener('click',()=>{
  if(!navigator.geolocation){status.textContent='This browser cannot capture device location. Enter field coordinates manually.';return}
  button.disabled=true;status.textContent='Allow location access to capture a fix with accuracy of 50 metres or better. Confirm the device is at the household.';
  timer=setTimeout(()=>{stop();status.textContent='No fix within 50 metres accuracy was received in 30 seconds. Retry outdoors, enter coordinates manually, or leave them empty.'},30000);
  watch=navigator.geolocation.watchPosition(position=>{if(!Number.isFinite(position.coords.accuracy)||position.coords.accuracy>50){status.textContent='Waiting for better accuracy (target: 50 metres). Manual entry remains available.';return}lat.value=position.coords.latitude.toFixed(7);lon.value=position.coords.longitude.toFixed(7);accuracy.value=position.coords.accuracy.toFixed(1);source.value='device_gps_reported';stop();status.textContent='Coordinates captured with reported accuracy of '+accuracy.value+' metres. Review before submitting. Household residence remains unverified.'},()=>{stop();status.textContent='Location was not captured. Check permission and GPS settings, enter field coordinates manually, or leave them empty.'},{enableHighAccuracy:true,timeout:30000,maximumAge:0});
 });
})();
