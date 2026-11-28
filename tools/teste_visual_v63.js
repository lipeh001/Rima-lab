#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]);
const html=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const gradle=fs.readFileSync(['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync),'utf8');
const checks=[
 ['release 3.4.1 / code 83',/versionCode\s*(?:=\s*)?83/.test(gradle)&&/versionName\s*(?:=\s*)?["']3\.4\.1["']/.test(gradle)],
 ['Favorites clears prior category highlight at source',html.includes("c.classList.remove('on','active','selected')")&&html.includes('function setMode(v,root)')],
 ['Favorites visibility drives category selected state',html.includes("const favOpen=!!document.querySelector('#bp>.rima-v43-favlist:not([hidden]),#bq>.rima-v43-favlist:not([hidden]),#bbq>.rima-v43-favlist:not([hidden])');")],
 ['Favorites hearts use same dark/gold palette as catalog hearts',html.includes('rimalab-favorites-selection-colors-v63')&&html.includes('background:rgba(255,203,84,.16)!important')&&html.includes('color:#ffcb54!important')],
 ['selected category has no white offset shadow',html.includes('box-shadow:none!important;')&&html.includes('filter:none!important;transform:none!important;')],
 ['no duplicate heart injection in legacy decorators',html.includes("row.classList.contains('rima-v43-fav-row')||row.closest('.rima-v43-favlist')")&&html.includes("row.classList.contains('rima-v43-fav-row')||row.closest('.rima-v43-favlist')||row.querySelector('[data-rima-fav]')")]
];
let failed=0;
for(const [name,ok] of checks){console.log((ok?'PASS ':'FAIL ')+name);if(!ok)failed++}
const scripts=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)];
for(let i=0;i<scripts.length;i++){try{new Function(scripts[i][1])}catch(e){console.log('INLINE_JS_ERROR script '+(i+1)+': '+e.message);failed++}}
console.log('V63_RESULT '+(checks.length+scripts.length-failed)+'/'+(checks.length+scripts.length));
if(failed)process.exit(1);
