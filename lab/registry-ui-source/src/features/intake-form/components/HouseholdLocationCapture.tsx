'use client';
import {useState} from 'react';
import {setValues,setWidgetValue,type WidgetStore} from '@openg2p/registry-widgets';
const HH='a0000000-0000-4000-8000-000000000002';
export default function HouseholdLocationCapture({store,onCaptured}:{store:WidgetStore;onCaptured:()=>void}){
 const [busy,setBusy]=useState(false),[message,setMessage]=useState('');
 const capture=()=>{
  if(!navigator.geolocation){setMessage('Location is unavailable on this device. Select your area and enter coordinates manually.');return;}
  setBusy(true);setMessage('Waiting for device location permission…');
  navigator.geolocation.getCurrentPosition(position=>{
   const c=position.coords;
   if(!Number.isFinite(c.latitude)||!Number.isFinite(c.longitude)){setBusy(false);setMessage('The device did not return valid coordinates. Try again or enter them manually.');return;}
   const values:Record<string,unknown>={latitude:Number(c.latitude.toFixed(7)),longitude:Number(c.longitude.toFixed(7)),location_accuracy_m:Number(c.accuracy.toFixed(1)),location_captured_at:new Date(position.timestamp).toISOString(),location_capture_source:'Device location (editable)'};
   if(c.altitude!==null&&Number.isFinite(c.altitude))values.altitude=c.altitude;
   let next=structuredClone(store.getState().widget.values);
   for(const [key,value] of Object.entries(values))next=setWidgetValue(next,HH+'.'+key,key,value);
   store.dispatch(setValues(next));onCaptured();setBusy(false);setMessage('Location captured (accuracy ±'+Math.round(c.accuracy)+' m). Check the coordinates and select the matching State/FCT, LGA and ward. Save the section to retain them.');
  },error=>{setBusy(false);setMessage(error.code===1?'Location permission was denied. You can still select your area and enter coordinates manually.':'Could not get a location fix. Try again outdoors or enter coordinates manually.');},{enableHighAccuracy:true,timeout:20000,maximumAge:0});
 };
 return <div className="rounded-xl border border-primary-second bg-white p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-semibold">Household location</h2><p className="mt-1 text-sm">Use your phone or tablet GPS, or select Nigeria’s administrative area and enter coordinates manually. GPS does not verify residence.</p></div><button type="button" onClick={capture} disabled={busy} className="rounded-full bg-neutral-first px-5 py-3 font-semibold text-white disabled:opacity-60">{busy?'Getting location…':'Use current location'}</button></div>{message&&<p role="status" className="mt-3 text-sm">{message}</p>}</div>;
}
