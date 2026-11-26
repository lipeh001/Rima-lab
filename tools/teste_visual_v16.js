#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const p=h.indexOf('function zLP(i,auto,style)'),e=h.indexOf('\n',p),lp=p>=0?h.slice(p,e>p?e:p+2400):'';
const checks=[
 ['tracking negativo removido e espaçamento legível',!h.includes('letter-spacing:-.045em!important;')&&h.includes('letter-spacing:.015em!important;')],
 ['palco reduzido de 52vh para 45vh',h.includes('min-height:45vh!important;')&&!h.includes('min-height:52vh!important;')],
 ['moldura projeta brilho para fora sem clipping',h.includes('overflow:visible!important')&&h.includes('inset:-5px!important')],
 ['pulso externo dourado da moldura',h.includes('rimalab-frame-pulse-v16')&&h.includes('inset:-8px!important')],
 ['palavra e moldura continuam no mesmo pulso',h.includes("word.classList.add('beat-word-hit')")&&h.includes("e.classList.add('hit')")],
 ['seleção inicial valida e reconstrói lista',lp.includes('zBuild(ZS.s)')&&lp.includes('const x=(ZLIB[ZS.s][1]||[])[i]')],
 ['estado selecionado é repintado após a escolha',lp.includes('ZS.key=zKey(x)')&&lp.includes('pk();requestAnimationFrame')],
 ['APK atualizado para 2.9.8 / versionCode 35',g.includes('versionCode 35')&&g.includes("versionName '2.9.8'")]
];
let bad=0;for(const [n,ok] of checks){console.log((ok?'OK  ':'FAIL ')+n);if(!ok)bad++}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V16');process.exit(bad?1:0);
