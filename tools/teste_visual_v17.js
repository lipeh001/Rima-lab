#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
 ['CSS v17 instalado',h.includes('id="rimalab-visual-v17"')],
 ['pulso exclusivo da moldura',h.includes('rimalab-frame-only-v17')&&h.includes('#stg.stage.hit::after')],
 ['texto sem animação, escala ou filtro',h.includes('#stg.stage #cb.beat-word-hit')&&h.includes('animation:none!important')&&h.includes('transform:none!important')&&h.includes('filter:none!important')],
 ['brilho do texto reduzido',h.includes('text-shadow:0 0 5px rgba(237,195,77,.12)!important')],
 ['palco permanece com geometria independente da palavra',h.includes('overflow:visible!important')&&h.includes('position:relative!important')],
 ['fonte adaptativa para palavras curtas, médias e longas',h.includes('length<=5?88:length<=8?98:108')],
 ['ajuste automático por mudança de palavra e tamanho',h.includes('new MutationObserver(fit)')&&h.includes('new ResizeObserver(fit)')],
 ['versão Android 2.9.9 / versionCode 36',g.includes('versionCode 36')&&g.includes("versionName '2.9.9'")]
];
let bad=0;for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V17');process.exit(bad?1:0);
