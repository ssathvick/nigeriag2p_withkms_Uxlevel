const{execFileSync}=require('child_process');
const password=execFileSync('wsl',['-d','Ubuntu-22.04','-u','root','--','python3','-c',"import yaml;print(yaml.safe_load(open('/opt/openg2p-lab/credentials.yaml'))['admin_password'],end='')"],{encoding:'utf8',stdio:['ignore','pipe','pipe']});
async function authenticate(page,host,service){
 const citizen=service==='beneficiary'?JSON.parse(execFileSync('wsl',['-d','Ubuntu-22.04','-u','root','--','cat','/opt/openg2p-lab/registration/test-account.json'],{encoding:'utf8',stdio:['ignore','pipe','pipe']})):null;
 await page.goto('https://'+host+(service==='portal-admin'?'/web':service==='registration'?'/registration/login?mode=staff':'/'),{waitUntil:'domcontentloaded'});
 for(let step=0;step<8;step++){
  await page.waitForTimeout(700);const url=new URL(page.url());
  if(url.hostname.includes('keycloak')&&await page.locator('#username').count()){
   await page.locator('#username').fill(citizen?.username||'admin');await page.locator('#password').fill(citizen?.password||password);await page.locator('form').filter({has:page.locator('#password')}).locator('[type=submit]').click();continue;
  }
  if(service==='odk'&&url.pathname.startsWith('/login')){await page.locator('a[href^="/v1/oidc/login"]').click();continue;}
  if(service==='superset'&&url.pathname.startsWith('/login')){await page.getByText('Sign In with NSIPA',{exact:true}).click();continue;}
  if(service==='beneficiary'&&url.pathname.endsWith('/login')){await page.locator('a[href*="getLoginProviderRedirect"]').click();continue;}
  if(['registry','portal-admin','beneficiary'].includes(service)&&await page.locator('input[name=login]').count()){
   await page.locator('input[name=login]').fill('admin@nigeria.openg2p.localhost');await page.locator('input[name=password]').fill(password);await page.locator('button[type=submit]').first().click();continue;
  }
  if(url.hostname===host&&!/\/login|\/callback|\/signin/.test(url.pathname))return;
 }
 throw Error('Sign-in did not reach requested service: '+new URL(page.url()).origin+new URL(page.url()).pathname);
}
module.exports={authenticate};
