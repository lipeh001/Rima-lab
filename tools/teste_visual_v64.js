#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]);
const html=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const gradle=fs.readFileSync(['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync),'utf8');
const checks=[
 ['release 3.4.2 / code 84',/versionCode\s*(?:=\s*)?84/.test(gradle)&&/versionName\s*(?:=\s*)?["']3\\.4\\.2["']/.test(gradle)],
 ['live category row has real bottom spacing and visible overflow',html.includes('rimalab-stage-selector-gap-entry-message-v64')&&html.includes('margin:0 0 14px!important;padding:2px 0 5px!important')&&html.includes('overflow:visible!important')],
 ['Favorites row is separated from category chips',html.includes('margin:8px 0 12px!important')&&html.includes('clear:both!important')],
 ['entry message is restored after wStart and lvStart',html.includes('rimalab-stage-selector-gap-entry-message-runtime-v64')&&html.includes("wrap('wStart')")&&html.includes("wrap('lvStart')")&&html.includes('Virada detectada. Entrando um pouco antes dela.')],
 ['message preserves no-intro and sync modes',html.includes('Beat sem introdução: já começa com tudo.')&&html.includes("state.k==='syn'?'':")],
 ['previous V62/V63 fixes remain',html.includes('rimalab-favorites-player-scroll-stage-v62')&&html.includes('rimalab-favorites-selection-colors-v63')]
];
let failed=0;
for(const [name,ok] of checks){console.log((ok?'PASS ':'FAIL ')+name);if(!ok)failed++}
console.log('V64_RESULT '+(checks.length-failed)+'/'+checks.length);
if(failed)process.exit(1);
