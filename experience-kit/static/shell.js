(()=>{'use strict';const config=window.OpenG2PExperience;if(!config?.baseUrl||window.top!==window.self||document.getElementById('ng2p-platform-bar'))return;
const bar=document.createElement('nav');bar.id='ng2p-platform-bar';bar.setAttribute('aria-label','Shared experience navigation');
const name=document.createElement('strong');name.textContent=config.brand?.name||'OpenG2P';
const workspace=document.createElement('a');workspace.textContent='My workspace';
const library=document.createElement('a');library.textContent='Knowledge library';library.href=config.baseUrl+'/knowledge';
const select=document.createElement('select');select.setAttribute('aria-label','Task persona');
for(const p of config.personas||[]){const option=document.createElement('option');option.value=p.id;option.textContent=p.name;select.append(option)}
let initial=new URLSearchParams(location.search).get('persona');try{initial=initial||sessionStorage.getItem('openg2p-task-persona')}catch{}
select.value=[...select.options].some(o=>o.value===initial)?initial:'all';
function update(){workspace.href=config.baseUrl+'/?persona='+encodeURIComponent(select.value);try{sessionStorage.setItem('openg2p-task-persona',select.value)}catch{}}
select.addEventListener('change',update);update();bar.append(name,workspace,library,select);document.body.append(bar);
})();
