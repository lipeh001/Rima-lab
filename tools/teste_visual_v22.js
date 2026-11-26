const fs=require('fs');
const path=require('path');
const root=path.resolve(process.argv[2]);
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
 ['splash usa lockup oficial da home',h.includes('<div class="brand-mark splash-brand-mark" aria-hidden="true"><span>R</span><i></i></div>')],
 ['splash não mantém marca provisória',!h.includes('<div class="splash-mark" aria-hidden="true"><span class="splash-initial">R</span></div>')],
 ['CSS preserva moldura e proporção da logo',h.includes('#rima-splash .brand-mark.splash-brand-mark')&&h.includes('width:86px!important;height:86px!important')],
 ['helper de retorno ao topo',h.includes('function rimaReturnPreviousScreenToTop()')&&h.includes('window.scrollTo(0,0)')],
 ['lvStop chama retorno ao topo',/function lvStop\(\)[\s\S]*?rimaReturnPreviousScreenToTop\(\)/.test(h)],
 ['versão 3.0.0 / code 42',g.includes('versionCode 42')&&g.includes("versionName '3.0.0'")]
];
let failed=0;
for(const [name,ok] of checks){console.log((ok?'PASS ':'FAIL ')+name);if(!ok)failed++}
if(failed)process.exit(1);
console.log('VISUAL_V22_TESTS_OK');
