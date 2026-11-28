#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]);
const hp=path.join(root,'app/src/main/assets/rima-lab.html');
const gp=['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync);
if(!fs.existsSync(hp)||!gp)throw new Error('V57: HTML/Gradle ausentes');
const h=fs.readFileSync(hp,'utf8'),g=fs.readFileSync(gp,'utf8'),pass=[],fail=[];
const check=(name,ok,detail='')=>(ok?pass:fail).push({name,detail});
check('versão 3.3.5/code77',/versionCode\\s*(?:=\\s*)?77/.test(g)&&/versionName\\s*(?:=\\s*)?["']3\\.3\\.5["']/.test(g));
check('runtime V56 removido',!h.includes('rimalab-centered-heart-runtime-v56'));
check('sem observador global V56',!h.includes("attributeFilter:['class','aria-pressed']")&&!h.includes('rimaV56RefreshHearts'));
check('runtime V57 instalado',h.includes('rimalab-startup-unfreeze-v57')&&h.includes('__rimaStartupUnfreeze'));
check('sistema de favoritos V54 preservado',h.includes('rimalab-unified-catalog-favorites-v54')&&h.includes('rimalab-favorites-layout-runtime-v43'));
check('observer do catálogo limitado a filhos diretos',h.includes('observe(root,{childList:true,subtree:false})'));
const startupStart=h.indexOf('<script id="rimalab-startup-unfreeze-v57">');
const startupEnd=startupStart>=0?h.indexOf('</script>',startupStart):-1;
const startup=startupStart>=0&&startupEnd>startupStart?h.slice(startupStart,startupEnd):'';
check('sem polling adicionado pelo V57',!!startup&&!startup.includes('setInterval(')&&!startup.includes('setTimeout('));
check('correções de layout V56 preservadas',h.includes('rimalab-layout-and-heart-system-v56')&&h.includes('grid-template-rows:30px 12px minmax(0,1fr)!important')&&h.includes('max-height:min(26vh,220px)!important'));
const scripts=[...h.matchAll(/<script\\b[^>]*>([\\s\\S]*?)<\\/script>/gi)];
let syntax=true,errors=[];
for(let i=0;i<scripts.length;i++){try{new Function(scripts[i][1])}catch(e){syntax=false;errors.push('script '+i+': '+e.message)}}
check('sintaxe dos scripts inline',syntax,errors.join('; '));
for(const x of pass)console.log('PASS '+x.name+(x.detail?' — '+x.detail:''));
for(const x of fail)console.log('FAIL '+x.name+(x.detail?' — '+x.detail:''));
console.log('V57_RESULT '+pass.length+' passed; '+fail.length+' failed');
if(fail.length)process.exit(1);
