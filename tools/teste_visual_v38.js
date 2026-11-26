#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]);
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
function body(id){const m=h.match(new RegExp('<script id="'+id+'">(.*?)</script>','s'));if(!m)throw Error('missing '+id);return m[1]}
const checks=[
 ['v30 sem MutationObserver',!body('rimalab-mode-config-runtime-v30').includes('new MutationObserver')],
 ['v30 atualiza texto apenas se necessário',body('rimalab-mode-config-runtime-v30').includes('if(el&&el.textContent!==v)')],
 ['v31 sem observer recursivo do #md',!body('rimalab-complete-runtime-v31').includes("const modeRoot=$('#md')")],
 ['v31 sem polling 1.5s',!body('rimalab-complete-runtime-v31').includes('setInterval(')],
 ['v33 sem polling 1.2s',!body('rimalab-player-polish-v33').includes('setInterval(')],
 ['v35 sem polling 0.9s',!body('rimalab-favorites-inline-v35').includes('setInterval(')],
 ['v35 atualiza ao trocar beat',body('rimalab-favorites-inline-v35').includes('oldBar=window.zBarUI')],
 ['scrollbar oculta sem bloquear rolagem',h.includes('rimalab-hide-scrollbar-v38')&&h.includes('scrollbar-width:none')&&!h.includes('touch-action:none')],
 ['versão 3.1.6 / code 58',g.includes('versionCode 58')&&g.includes("versionName '3.1.6'")]
];
let n=0;for(const [s,ok] of checks){console.log((ok?'PASS ':'FAIL ')+s);if(!ok)n++}if(n)process.exit(1);
