#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const fn=(h.match(/function rimaPulseStageWord\(\)\{[\s\S]*?\n\}/)||[])[0]||'';
const pulse=(h.match(/function pulse\(q\)\{[\s\S]*?\n\}/)||[])[0]||'';
const css=(h.match(/<style id="rimalab-visual-v21">[\s\S]*?<\/style>/)||[])[0]||'';
const checks=[
 ['v21 aplicado',!!css],
 ['brilho da palavra acionado pelo mesmo callback da batida',pulse.includes('rimaPulseStageFrame();')&&pulse.includes('rimaPulseStageWord();')],
 ['brilho da palavra é animado quadro a quadro',fn.includes('requestAnimationFrame(draw)')&&fn.includes('performance.now()')],
 ['palavra não muda de posição nem escala',fn.includes("setProperty('transform','none','important')")],
 ['iluminação da palavra é sutil e temporária',fn.includes('0.12*strength')&&fn.includes('duration=190')],
 ['palco continua com dimensões fixas',/height:450px!important/.test(css)&&/flex:0 0 450px!important/.test(css)],
 ['layout reserva área inferior para o botão de dica',/padding:13px 14px 18px!important/.test(css)&&/padding:0 0 7px!important/.test(css)],
 ['botão de dica fica contido na largura do palco',/max-width:100%!important/.test(css)&&/overflow:hidden!important/.test(css)],
 ['moldura mantém camada própria e inset interno',/inset:5px!important/.test(css)&&/z-index:0!important/.test(css)],
 ['texto e elementos internos não recebem transform',css.includes('#lv:not([hidden]) #stg.stage #cb')&&css.includes('transform:none!important')],
 ['build 2.9.14 / versionCode 41',g.includes('versionCode 41')&&g.includes("versionName '2.9.14'")]
];
let bad=0;for(const [n,ok] of checks){console.log((ok?'OK  ':'FAIL ')+n);if(!ok)bad++}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V21');process.exit(bad?1:0);
