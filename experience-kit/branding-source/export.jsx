(function(){
var root='H:/Nigeria_Mosip/codex/NSIPA-Identity/';
var names=['NSIPA-primary','NSIPA-stacked','NSIPA-monochrome','NSIPA-reversed','NSIPA-symbol','NSIPA-presentation'];
var report=[];
for(var n=0;n<names.length;n++){
 var d=app.open(File(root+names[n]+'.svg'));
 d.layers[0].name='Editable vector artwork and live typography';
 var opts=new IllustratorSaveOptions(); opts.pdfCompatible=true;
 d.saveAs(File(root+names[n]+'.ai'),opts);
 var png=new ExportOptionsPNG24();png.artBoardClipping=true;png.transparency=true;png.horizontalScale=150;png.verticalScale=150;
 d.exportFile(File(root+names[n]+'.png'),ExportType.PNG24,png);
 report.push(names[n]+': '+d.pathItems.length+' paths, '+d.textFrames.length+' live text objects');
 if(n<names.length-1)d.close(SaveOptions.DONOTSAVECHANGES);
}
return report.join('\n');
})();
