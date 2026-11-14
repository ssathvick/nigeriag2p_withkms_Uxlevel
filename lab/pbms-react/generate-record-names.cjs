const fs=require('fs'),esbuild=require('esbuild');
esbuild.buildSync({entryPoints:['src/programme-names.js'],outfile:'../../tmp/programme-names.cjs',platform:'node',format:'cjs'});
const {programmeName}=require('../../tmp/programme-names.cjs');
const data=JSON.parse(fs.readFileSync('H:/Nigeria_Mosip/NSIPA-Private-Access-20261111/PBMS-label-source.json','utf8')),names={};
const kinds={'g2p.enrollment.cycle':'Enrollment cycle','g2p.disbursement.cycle':'Disbursement cycle','g2p.beneficiary.list':'Beneficiary list','g2p.eligibility.rule.definition':'Eligibility rule','g2p.entitlement.rule.definition':'Benefit entitlement rule','g2p.priority.rule.definition':'Priority rule'};
for(const [model,rows]of Object.entries(data)){for(const r of rows){let raw=r.program_mnemonic||r.mnemonic||r.cycle_mnemonic||r.benefit_mnemonic||r.display_name;if(!raw)continue;let name;
if(model==='g2p.program.definition')name=programmeName(raw);
else if(kinds[model]){let purpose=/ROLES/.test(raw)?'Role access test':/AUTO/.test(raw)?'Automatic processing test':null;name=[r.program_id&&programmeName(r.program_id[1]),purpose,kinds[model]+(r.list_stage?' — '+r.list_stage:'')+' '+(r.cycle_number||r.rule_number||r.id)].filter(Boolean).join(' — ');}
else if(model==='g2p.benefit.codes')name=programmeName(raw)+' — Benefit';
else if(model==='g2p.program.benefit.codes')name=programmeName(r.program_id?.[1]||raw)+' — Programme benefit '+r.id;
else name=programmeName(raw).replace(/_/g,' ');
(names[model]??={})[r.id]={raw,name};}}
fs.writeFileSync('src/record-names.json',JSON.stringify(names,null,2));
