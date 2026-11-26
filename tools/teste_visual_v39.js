#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]);
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const m=h.match(/<script id="rimalab-complete-runtime-v31">([\\s\\S]*?)<\\/script>/);
const guard=h.match(/<script id="rimalab-startup-observer-scope-fix-v39">([\\s\\S]*?)<\\/script>/);
const checks=[
 ['observer do catálogo observa somente filhos diretos',!!m&&m[1].includes("observe(root,{childList:true,subtree:false})")&&!m[1].includes("observe(root,{childList:true,subtree:true})")],
 ['observer não observa mutações feitas por decorateCatalog nos descendentes',!!m&&m[1].includes('function decorateCatalog()')&&m[1].includes("observe(root,{childList:true,subtree:false})")],
 ['diagnóstico de escopo de observer instalado',!!guard&&guard[1].includes("direct-children-only")],
 ['versão 3.1.7 / code 59',g.includes('versionCode 59')&&g.includes("versionName '3.1.7'")]
];
let failed=0;for(const [label,ok] of checks){console.log((ok?'PASS ':'FAIL ')+label);if(!ok)failed++}if(failed)process.exit(1);console.log(checks.length+'/'+checks.length+' testes v39 passaram');
