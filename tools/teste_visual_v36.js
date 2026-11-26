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
 ['banner sem prefixo 1 e heading Escolha o modo',h.includes('#rima-v29-mode-banner:before{display:none')&&h.includes("setText(head.querySelector('h2'),'Escolha o modo')")],
 ['observer de modo idempotente, sem loop de mutações',h.includes('rimalab-mode-number-clean-runtime-v37')&&h.includes('function setText(el,value){if(el&&el.textContent!==value)el.textContent=value}')],
 ['dificuldade e beat mantêm ordem 2 e 3',h.includes("if(n)n.textContent='2'")&&h.includes("if(n)n.textContent='3'")],
 ['dicas reajustam no resize, rotação e viewport',h.includes("window.addEventListener('orientationchange'")&&h.includes('visualViewport.addEventListener')&&h.includes('const cap=landscape?16:18')],
 ['player horizontal vai para a base',h.includes('bottom:calc(4px + env(safe-area-inset-bottom,0px))')&&!h.includes('calc(58px + env(safe-area-inset-bottom,0px))')],
 ['versão 3.1.5 / code 57',g.includes('versionCode 57')&&g.includes("versionName '3.1.5'")]
];
// Synthetic loopback: the exact correlation function from the app must recover a 250 ms return.
const vm=require('vm');
const calA=h.indexOf('function calChirp(sr){'),calB=h.indexOf('async function cal(){',calA);
let micCorrelationOk=false;
if(calA>=0&&calB>calA){
 const sandbox={};vm.runInNewContext(h.slice(calA,calB)+'\nglobalThis.__chirp=calChirp;globalThis.__corr=calCorrelation;',sandbox);
 const sr=48000,stride=4,template=sandbox.__chirp(sr),record=new Float32Array(sr*4),expected=sr*1,delay=sr*.250;
 for(let i=0;i<template.length;i++)record[expected+Math.round(delay)+i]=template[i];
 const dec=new Float32Array(Math.ceil(record.length/stride));
 for(let i=0,j=0;i<record.length;i+=stride,j++)dec[j]=record[i];
 const found=sandbox.__corr(dec,template,Math.round(expected/stride),sr,stride,850);
 micCorrelationOk=!!found&&Math.abs(found.delayMs-250)<2&&found.score>.9;
}
checks.push(['algoritmo de correlação recupera atraso sintético de 250 ms',micCorrelationOk]);
let fail=0;for(const [name,ok] of checks){console.log((ok?'PASS ':'FAIL ')+name);if(!ok)fail++}if(fail)process.exit(1);
