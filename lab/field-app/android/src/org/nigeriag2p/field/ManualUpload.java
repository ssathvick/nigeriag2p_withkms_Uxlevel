package org.nigeriag2p.field;
import android.content.Context;import org.json.*;import java.io.*;import java.net.*;import java.util.*;
// One user action, one record, one attempt. No scheduled work.
final class ManualUpload {
 static final java.util.concurrent.atomic.AtomicBoolean BUSY=new java.util.concurrent.atomic.AtomicBoolean();
 volatile boolean cancelled;
 private HttpURLConnection connection;
 void cancel(){HttpURLConnection c;synchronized(this){cancelled=true;c=connection;}if(c!=null)new Thread(c::disconnect,"cancel-upload").start();}
 static String esc(String x){return x.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;").replace("'","&apos;");}
 static String tag(String n,String x){return "<"+n+">"+esc(x)+"</"+n+">";}
 static String xml(JSONObject r){String lat=r.optString("lat"),lon=r.optString("lon"),accuracy=r.optString("accuracy");return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><data id=\"nsipa_field_household_demo\" version=\"2026111001\"><visit>"+tag("enumerator_id",r.optString("officer"))+tag("visit_date",r.optString("date"))+tag("consent","yes")+"</visit><location>"+tag("state",r.optString("state"))+tag("lga",r.optString("lga"))+tag("ward",r.optString("ward"))+(lat.isEmpty()?"":tag("coordinates",lat+" "+lon+" 0 "+(accuracy.isEmpty()?"0":accuracy)))+"</location><household>"+tag("household_name",r.optString("household_name"))+tag("household_head_name",r.optString("head_name"))+tag("sample_reference",r.optString("ref"))+tag("household_size",r.optString("size"))+tag("children",r.optString("children"))+tag("shelter",r.optString("shelter"))+"</household><livelihood>"+tag("livelihood_type",r.optString("livelihood"))+tag("priority_needs",r.optString("need"))+"</livelihood><review>"+tag("review_confirmation","yes")+"</review><meta>"+tag("instanceID",r.optString("id"))+tag("instanceName",r.optString("head_name")+" - "+r.optString("ref"))+"</meta></data>";}
 int post(String endpoint,String xml)throws Exception {if(!"https".equalsIgnoreCase(new URL(endpoint).getProtocol()))throw new IOException("HTTPS required");String boundary="Field"+UUID.randomUUID().toString().replace("-","");HttpURLConnection c=(HttpURLConnection)new URL(endpoint+"/submission").openConnection();synchronized(this){if(cancelled){c.disconnect();throw new IOException("Cancelled");}connection=c;}try{c.setConnectTimeout(15000);c.setReadTimeout(15000);c.setInstanceFollowRedirects(false);c.setRequestMethod("POST");c.setDoOutput(true);c.setRequestProperty("X-OpenRosa-Version","1.0");c.setRequestProperty("Content-Type","multipart/form-data; boundary="+boundary);if(cancelled)throw new IOException("Cancelled");try(OutputStream out=c.getOutputStream()){if(cancelled)throw new IOException("Cancelled");out.write(("--"+boundary+"\r\nContent-Disposition: form-data; name=\"xml_submission_file\"; filename=\"submission.xml\"\r\nContent-Type: text/xml; charset=utf-8\r\n\r\n").getBytes("UTF-8"));out.write(xml.getBytes("UTF-8"));out.write(("\r\n--"+boundary+"--\r\n").getBytes("UTF-8"));}return c.getResponseCode();}finally{c.disconnect();synchronized(this){connection=null;}}}
 String send(Context context,String endpoint,JSONObject item){
  String error="";
  try{if(cancelled)return "Cancelled";int code=post(endpoint,xml(item));if(code!=201)error="HTTP "+code;}
  catch(Exception e){error="Upload interrupted or failed; server receipt may be unknown. Check the server before retrying.";}
  try{synchronized(FieldStore.LOCK){JSONObject all=FieldStore.read(context);JSONArray rows=all.getJSONArray("records");for(int i=0;i<rows.length();i++){JSONObject row=rows.getJSONObject(i);if(item.optString("id").equals(row.optString("id"))&&"approved-demo".equals(row.optString("status"))){if(error.isEmpty()){row.put("status","sent");row.remove("sync_error");}else row.put("sync_error",error);break;}}FieldStore.write(context,all);}}
  catch(Exception e){return "Could not save upload outcome. Check the server before retrying.";}
  return error.isEmpty()?"Server accepted this sample (HTTP 201).":error;
 }
}
