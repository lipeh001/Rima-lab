#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const fit=h.includes('id="rima-word-fit-script-v13"')?h.slice(h.indexOf('id="rima-word-fit-script-v13"')):'';
const w=h.slice(h.indexOf('function wWord()'),h.indexOf('function wWord()')+700);
const checks=[
 ['gatilho original stamp(w) foi restaurado no avanço da palavra',w.includes("$('#cs').textContent=c.sub;stamp(w);WD.nw++")],
 ['fonte do palco voltou a 72px',h.includes('font-size:72px!important')],
 ['palavras curtas e médias não são reduzidas se couberem',fit.includes('raw.length<=12 && e.scrollWidth<=available')],
 ['a redução só ocorre quando a largura real ultrapassa o palco',fit.includes('if(e.scrollWidth<=available)low=mid;else high=mid')],
 ['observa mudanças de palavra e redimensionamento',fit.includes('MutationObserver')&&fit.includes('ResizeObserver')],
 ['não comprime texto com scaleX nem anima o texto',!fit.includes('scaleX(')&&h.includes('#stg.stage #cb.word,#stg.stage.hit #cb{transform:none!important;animation:none!important}')],
 ['pulso dourado suave substitui o piscar forte',h.includes('rimalab-gold-bloom-v13')&&h.includes('0.52s ease-out')],
 ['o pulso afeta palco e moldura sem deslocar o conteúdo',h.includes('#stg.stage.hit,#bt .stage.hit')&&h.includes('transform:none!important')],
 ['R da tela inicial é branco',h.includes('.splash-mark .splash-initial{color:#fff!important')],
 ['APK atualizado para 2.9.5 / versionCode 32',g.includes('versionCode 32')&&g.includes("versionName '2.9.5'")],
 ['não mantém o ajuste de fonte pequeno global da v12',!h.includes('id="rima-word-fit-v12"')&&!h.includes('id="rima-word-fit-script-v12"')]
];
let bad=0;for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V13');
process.exit(bad?1:0);
