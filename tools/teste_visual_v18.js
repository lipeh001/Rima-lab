#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const p=(h.match(/function pulse\(q\)\{[\s\S]*?\}(?=\s*function start\()/)||[])[0]||'';
const css=(h.match(/<style id="rimalab-visual-v18">[\s\S]*?<\/style>/)||[])[0]||'';
const checks=[
 ['pulso v18 instalado',css.length>0],
 ['altura/largura do palco fixas',/height:360px!important/.test(css)&&/min-height:360px!important/.test(css)&&/max-height:360px!important/.test(css)],
 ['palco nunca recebe transform no impacto',/#lv:not\(\[hidden\]\) #stg\.stage\.hit\{[\s\S]*?transform:none!important/.test(css)],
 ['palavra sem animação e sem escala',/#cb\.beat-word-hit\{[\s\S]*?transform:none!important/.test(css)&&/#cb\.beat-word-hit\{[\s\S]*?animation:none!important/.test(css)],
 ['callback não anima mais a palavra',p.length>0&&!p.includes('beat-word-hit')&&!p.includes('__rimaWordBeatTimer')],
 ['moldura é a única peça que pulsa',/\.stage\.hit::after\{[\s\S]*?animation:rimalab-frame-impact-v18/.test(css)&&/transform:scale\(1\.035\)/.test(css)],
 ['moldura retorna à escala original',/100%[\s\S]*?transform:scale\(1\)/.test(css)],
 ['sem ultrapassar a área do palco',/overflow:hidden!important/.test(css)&&/inset:5px!important/.test(css)],
 ['versão Android 2.9.11 / versionCode 38',g.includes('versionCode 38')&&g.includes("versionName '2.9.11'")]
];
let bad=0;for(const [n,ok] of checks){console.log((ok?'OK  ':'FAIL ')+n);if(!ok)bad++}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V18');process.exit(bad?1:0);
