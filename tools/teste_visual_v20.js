#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const fn=(h.match(/function rimaPulseStageFrame\(\)\{[\s\S]*?\n\}\nfunction pulse\(q\)\{/)||[])[0]||'';
const pulse=(h.match(/function pulse\(q\)\{[\s\S]*?\n\}/)||[])[0]||'';
const tick=(h.match(/function zTick\(\)\{[\s\S]*?\n\}/)||[])[0]||'';
const css=(h.match(/<style id="rimalab-visual-v20">[\s\S]*?<\/style>/)||[])[0]||'';
const checks=[
 ['v20 aplicado',!!css],
 ['pulso é calculado quadro a quadro com requestAnimationFrame',fn.includes('requestAnimationFrame(draw)')&&fn.includes('performance.now()')],
 ['escala aumenta 3,5% e retorna ao tamanho original',fn.includes('1+.035')&&fn.includes("scale(1)")],
 ['transform, brilho e borda são aplicados com prioridade inline',fn.includes("setProperty('transform'")&&fn.includes(",'important')")&&fn.includes("setProperty('box-shadow'")],
 ['contador confirma cada pulso executado',fn.includes('__rimaBeatPulseCount')&&fn.includes('__rimaBeatPulseLastAt')],
 ['callback de batida aciona a moldura',pulse.includes('rimaPulseStageFrame()')],
 ['relógio do áudio continua disparando pulse em cada subdivisão',tick.includes('if(bt>zQ){zQ=bt;pulse(')],
 ['palco permanece com altura fixa de 450px',/height:450px!important/.test(css)&&/flex:0 0 450px!important/.test(css)],
 ['moldura fica dentro do palco e não invade player',/inset:5px!important/.test(css)&&/overflow:hidden!important/.test(css)],
 ['palavra não escala nem anima',css.includes('#lv:not([hidden]) #stg.stage #cb')&&css.includes('transform:none!important')&&css.includes('animation:none!important')],
 ['não depende de @keyframes para pulsar',!fn.includes('classList.add')&&!css.includes('@keyframes')],
 ['build 2.9.13 / versionCode 40',g.includes('versionCode 40')&&g.includes("versionName '2.9.13'")]
];
let bad=0;for(const [n,ok] of checks){console.log((ok?'OK  ':'FAIL ')+n);if(!ok)bad++}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V20');process.exit(bad?1:0);
