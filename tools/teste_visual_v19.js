#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const p=(h.match(/function pulse\(q\)\{[\s\S]*?\n\}/)||[])[0]||'';
const lv=(h.match(/function lvStart\(\)\{[\s\S]*?\n\}\nfunction lvStop\(\)/)||[])[0]||'';
const tick=(h.match(/function zTick\(\)\{[\s\S]*?\n\}/)||[])[0]||'';
const css=(h.match(/<style id="rimalab-visual-v19">[\s\S]*?<\/style>/)||[])[0]||'';
const checks=[
 ['estilo v19 foi aplicado',css.length>0],
 ['palco tem altura fixa suficiente de 450px',/height:450px!important/.test(css)&&/min-height:450px!important/.test(css)&&/max-height:450px!important/.test(css)],
 ['o palco não é redimensionado por palavras',/flex:0 0 450px!important/.test(css)&&/transform:none!important/.test(css)],
 ['camada independente da moldura está dentro dos limites',/\.rima-beat-frame\{/.test(css)&&/inset:5px!important/.test(css)&&/overflow:hidden!important/.test(css)],
 ['a moldura expande 3,5% e retorna',/rimalab-frame-impact-v19/.test(css)&&/scale\(1\.035\)/.test(css)&&/100%[\s\S]*?scale\(1\)/.test(css)],
 ['o callback de batida aciona a camada, não a classe hit do palco',p.includes('rimaPulseStageFrame()')&&!p.includes("classList.add('hit')")&&!p.includes("classList.add('beat-word-hit')")],
 ['o relógio do áudio continua chamando pulse no beat real',tick.includes('if(bt>zQ){zQ=bt;pulse(')],
 ['o texto estático não escala nem anima',css.includes('#lv:not([hidden]) #stg.stage #cb')&&css.includes('animation:none!important')&&css.includes('transform:none!important')],
 ['falta de seleção mostra aviso sem voltar ao primeiro passo',lv.includes('Selecione um beat antes de começar o treino.')&&!lv.includes('go(0)')&&!lv.includes("$('#train-step-2').hidden=true")],
 ['a seleção de beat apaga o aviso inline',h.includes('rima-select-beat-note')&&h.includes('__rimaSelectNote.remove()')],
 ['classe imersiva é aplicada antes de revelar a tela',lv.indexOf("document.body.classList.add('pl')")<lv.indexOf('screen.hidden=false')],
 ['versão Android 2.9.12 / versionCode 39',g.includes('versionCode 39')&&g.includes("versionName '2.9.12'")]
];
let bad=0;for(const [n,ok] of checks){console.log((ok?'OK  ':'FAIL ')+n);if(!ok)bad++}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V19');process.exit(bad?1:0);
