#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const service=fs.readFileSync(path.join(root,'app/src/main/java/app/rimalab/MusicService.java'),'utf8');
const gradle=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const start=h.indexOf('async function cal(){'),end=h.indexOf('\nconst CH=',start),cal=start>=0&&end>start?h.slice(start,end):'';
const css=h.includes('id="rima-landscape-seekbar-v11"')?h.slice(h.indexOf('id="rima-landscape-seekbar-v11"')):'';
const checks=[
 ['calibragem identificada como opcional',h.includes('Calibrar (opcional)')],
 ['calibrador usa latência do aparelho sem microfone',cal.includes('ctx.baseLatency')&&cal.includes('ctx.outputLatency')&&!cal.includes('getUserMedia')],
 ['limite de compensação reduzido para 300 ms',h.includes('max="300" step="1"')&&cal.includes('Math.min(300')],
 ['medição considera latência base e de saída',cal.includes('const base=Number(ctx.baseLatency)||0,output=Number(ctx.outputLatency)||0,v=base+output')],
 ['texto não exige som alto nem microfone',h.includes('Não precisa de microfone nem aumentar o volume.')||h.includes('Não precisa de microfone nem de aumentar o volume.')],
 ['player horizontal mostra o controle de posição',css.includes('#pbar .pwscr{display:flex!important')&&css.includes('input[type=range]')],
 ['seekbar horizontal aceita toque',css.includes('pointer-events:auto!important')&&css.includes('accent-color:#edc34d')],
 ['faixa problemática é filtrada também do cache salvo',h.includes('rimaIsBlockedBeatV11')&&h.includes('rap\\s+boom\\s+bap\\s+gritty\\s+old\\s+school')],
 ['ícone grande da notificação usa dourado',service.includes('p.setColor(0xFFEDC34D)')],
 ['APK incrementa versão para 2.9.3',gradle.includes('versionCode 30')&&gradle.includes("versionName '2.9.3'")]
];
let bad=0;for(const [n,ok] of checks){console.log((ok?'OK  ':'FAIL ')+n);if(!ok)bad++}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V11');process.exit(bad?1:0);
