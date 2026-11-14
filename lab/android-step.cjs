const {execFileSync}=require('child_process');
const actions=JSON.parse(process.argv[2]||'[["dump"]]');
for(const args of actions){
 const result=execFileSync(process.execPath,[__dirname+'/android-ui.cjs',...args],{encoding:'utf8',timeout:40000});
 const nodes=JSON.parse(result);
 console.log(JSON.stringify({action:args[0],controls:nodes.filter(n=>!['NSIPA Master Registry Household Interview','Back','Next'].includes(n.text)&&!['Save as draft','Go To Prompt','More options'].includes(n.description)).map(n=>({text:n.text,description:n.description,checked:n.checked,bounds:n.bounds}))}));
}
