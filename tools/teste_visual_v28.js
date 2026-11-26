#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]);
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
 ['player permanece visível na etapa 2',h.includes("document.body.classList.add('pl')")&&h.includes('body.pl:not(.sy) #pbar')],
 ['navegação preserva o áudio durante a etapa 2',h.includes('if(play&&!keepConfig)stop()')&&h.includes('if(!window.__rimaKeepPlayerOnNavigation)stop()')],
 ['retorno à aba Treino restaura a etapa 2',h.includes('const step2=window.__rimaTrainStep===2')],
 ['modo, rounds e opções são salvos',h.includes('rimalab_training_config_v28')&&h.includes('mode:mode')&&h.includes('nb4:nb4')&&h.includes('CH:CH')],
 ['dificuldade e calibração são preservadas',h.includes('DF:DF')&&h.includes('LAT:LAT')&&h.includes("localStorage.setItem('lat',v)")],
 ['tons de calibração têm ganho reforçado',h.includes('exponentialRampToValueAtTime(.64')],
 ['referência visual acompanha os tons',h.includes('cal-visual')&&h.includes("visual.classList.add('is-active')")],
 ['calibração não solicita microfone',!h.includes('getUserMedia')],
 ['botão Parar cancela o teste',h.includes('r.cancelled=true')&&h.includes('r.finish()')],
 ['ajustadores antigos de fonte foram removidos',!['rima-word-fit-script-v13','rima-word-fit-script-v15','rimalab-word-fit-v17','rimalab-word-vertical-fit-script-v24','rimalab-word-fit-v26'].some(id=>h.includes('id="'+id+'"'))],
 ['há um único ajustador de fonte adaptativo',h.includes('id="rimalab-word-fit-v28"')&&h.includes('len<=5?88:len<=8?80')],
 ['calibrador com espaçamento compacto',h.includes('rimalab-calibration-polish-v28')&&h.includes('margin:0 0 8px!important')],
 ['versão 3.0.5 / code 47',g.includes('versionCode 47')&&g.includes("versionName '3.0.5'")]
];
let failures=0;
for(const [label,ok] of checks){console.log((ok?'PASS ':'FAIL ')+label);if(!ok)failures++}
if(failures)process.exit(1);
console.log(checks.length+'/'+checks.length+' verificações v28 passaram');
