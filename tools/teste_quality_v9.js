#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const icon=fs.readFileSync(path.join(root,'app/src/main/res/drawable/ic_stat_beat.xml'),'utf8');
const gradle=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
 ['dicas usam famílias fonéticas curadas, não apenas as três últimas letras',h.includes('rima-rich-hints-v9')&&h.includes("const family=rimasDe(t)")&&!h.includes("IX.get(kk(t))")],
 ['TAÇA tem pelo menos duas rimas adequadas',h.includes("'TAÇA':['graça','raça','caça','massa']")],
 ['CONSOLE tem sugestões relacionadas',h.includes("'CONSOLE':['controle','descontrole','enrole','engole']")],
 ['POSTE tem sugestões relacionadas',h.includes("'POSTE':['goste','encoste','desgoste','aposte']")],
 ['MAREMOTO tem sugestões relacionadas',h.includes("'MAREMOTO':['terremoto','remoto','moto','foto']")],
 ['BATIMENTO e LIMPAR têm quatro sugestões',h.includes("'BATIMENTO':['pensamento','lamento','talento','momento']")&&h.includes("'LIMPAR':['poupar','disparar','preparar','escapar']")],
 ['modo Palavra não gera prompts narrativos',h.includes('while(!r&&tries++<24)')&&h.includes("w='coração';r='razão, paixão, canção, ilusão'")&&!h.includes("sub:r&&Math.random()<.5?'Rimas possíveis: '+r:nP()")],
 ['calibrador usa um sinal em volume confortável e sete amostras',h.includes("GAINS=[.18],N=7,W=1")&&h.includes('for(let r=0;r<1;r++)')],
 ['calibrador estabiliza o resultado por mediana e passos de 5 ms',h.includes('Math.round(median/5)*5')&&h.includes('Math.abs(x-md)<=10')],
 ['calibrador não pede para aumentar o volume',!h.includes('Aumente um pouco o volume')&&h.includes('🔔')],
 ['calibrador permite ajustar até 1200 ms',h.includes('max="1200"')],
 ['sincronização usa o relógio de saída do AudioContext',h.includes('getOutputTimestamp')&&h.includes('zPerf()-performance.now()+LAT')],
 ['botão Voltar centraliza seu conteúdo',h.includes('rima-quality-v9')&&h.includes('.bk{display:flex!important;align-items:center!important;justify-content:center!important')],
 ['batida ilumina mais a moldura sem animar as letras',h.includes('rl-quality-edge-v9')&&h.includes('0 0 34px rgba(215,251,87,.42)')],
 ['ícone pequeno da notificação é uma onda, deixando o R grande sem segundo R',icon.includes('M4,10h2v8H4z')&&icon.includes('M12,3h2v15h-2z')&&!icon.includes('M5,3h8.1')],
 ['versão 2.9.1 pode atualizar a instalação anterior',gradle.includes('versionCode 28')&&gradle.includes("versionName '2.9.1'")]
];
let bad=0;
for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++;}
console.log((checks.length-bad)+'/'+checks.length+' verificações QUALITY_V9');
process.exit(bad?1:0);
