#!/usr/bin/env node
const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]);
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
 ['player oculto ao entrar na etapa 2',h.includes('body.pl:not(.sy):not(.rima-player-visible) #pbar{display:none!important}')],
 ['player exibido apenas após áudio iniciar',h.includes("body.classList.add('rima-player-visible')")&&h.includes('window.zSetPL=wrapped')],
 ['player removido ao parar ou sair',h.includes("body.classList.remove('rima-player-visible')")&&h.includes('window.stop=wrapped')],
 ['Ouvir usa o player real existente',h.includes("body.classList.contains('pv')&&typeof window.stop")],
 ['calibrador pede microfone real',h.includes("navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:false,noiseSuppression:false,autoGainControl:false},video:false})")],
 ['calibrador gera cinco sinais de medição',h.includes('const count=5,spacing=1.12')&&h.includes('calChirp(sr)')],
 ['calibrador cruza sinal de referência com microfone',h.includes('function calCorrelation(record,template')&&h.includes('calCorrelation(dec,template,expected')],
 ['calibrador aplica mediana e salva LAT',h.includes('values[Math.floor(values.length/2)]')&&h.includes('setLat(applied)')],
 ['calibrador mantém cancelamento e encerra microfone',h.includes('function calCancel()')&&h.includes('run.stream.getTracks().forEach(t=>t.stop())')],
 ['ajuste manual suporta Bluetooth com delay maior',h.includes('max="800"')&&h.includes('Math.min(800,+v||0)')],
 ['banner sem prefixo 1 e heading Escolha o modo',h.includes('#rima-v29-mode-banner:before{display:none')&&h.includes("h.textContent='Escolha o modo'")],
 ['dificuldade e beat mantêm ordem 2 e 3',h.includes("if(n)n.textContent='2'")&&h.includes("if(n)n.textContent='3'")],
 ['dicas reajustam no resize, rotação e viewport',h.includes("window.addEventListener('orientationchange'")&&h.includes('visualViewport.addEventListener')&&h.includes('const cap=landscape?16:18')],
 ['player horizontal vai para a base',h.includes('bottom:calc(4px + env(safe-area-inset-bottom,0px))')&&!h.includes('calc(58px + env(safe-area-inset-bottom,0px))')],
 ['versão 3.1.4 / code 56',g.includes('versionCode 56')&&g.includes("versionName '3.1.4'")]
];
let fail=0;for(const [name,ok] of checks){console.log((ok?'PASS ':'FAIL ')+name);if(!ok)fail++}if(fail)process.exit(1);
