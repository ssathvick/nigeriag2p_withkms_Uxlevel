package org.nigeriag2p.field;
import org.json.JSONObject;import java.net.*;import java.io.*;
public class SyncHarness {
 static Fake last;static int code=201;
 static class Fake extends HttpURLConnection {
  ByteArrayOutputStream body=new ByteArrayOutputStream();boolean closed;
  Fake(URL u){super(u);}public void connect(){}public void disconnect(){closed=true;}public boolean usingProxy(){return false;}
  public OutputStream getOutputStream(){return body;}public int getResponseCode(){return code;}
 }
 static void check(boolean ok){if(!ok)throw new AssertionError();}
 public static void main(String[] args)throws Exception {
  URL.setURLStreamHandlerFactory(protocol->"https".equals(protocol)?new URLStreamHandler(){protected URLConnection openConnection(URL u){return last=new Fake(u);}}:null);
  JSONObject r=new JSONObject();r.put("id","uuid:sample-sync-test");r.put("ref","A&B<sample>");r.put("lat","9.9000");r.put("lon","8.9000");
  String xml=ManualUpload.xml(r);check(xml.contains("A&amp;B&lt;sample&gt;"));check(xml.contains("9.9000 8.9000 0 0"));
  ManualUpload attempt=new ManualUpload();check(attempt.post("https://test.invalid/project",xml)==201);
  check(last.getURL().getPath().equals("/project/submission"));check(last.getRequestProperty("X-OpenRosa-Version").equals("1.0"));check(!last.getInstanceFollowRedirects());check(last.getConnectTimeout()==15000&&last.getReadTimeout()==15000);check(last.closed);
  check(last.body.toString("UTF-8").contains("name=\"xml_submission_file\""));
  code=500;check(attempt.post("https://test.invalid/project",xml)==500);
  ManualUpload cancelled=new ManualUpload();cancelled.cancel();try{cancelled.post("https://test.invalid/project",xml);throw new AssertionError();}catch(IOException expected){}check(last.body.size()==0);
  try{attempt.post("http://test.invalid/project",xml);throw new AssertionError();}catch(IOException expected){}
  System.out.println("PASS: multipart/XML, HTTPS-only, redirect disabled, timeouts, response codes, pre-cancellation and disconnect. Mock transport; no device or server test.");
 }
}
