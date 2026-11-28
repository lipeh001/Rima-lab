#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]),hp=path.join(root,'app/src/main/assets/rima-lab.html');
const gp=['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync);
if(!fs.existsSync(hp)||!gp)throw new Error('V59: HTML/Gradle ausentes');
const h=fs.readFileSync(hp,'utf8'),g=fs.readFileSync(gp,'utf8'),pass=[],fail=[];
const check=(n,ok,d='')=>(ok?pass:fail).push({n,d});
check('versão 3.3.7/code79',/versionCode\s*(?:=\s*)?79/.test(g)&&/versionName\s*(?:=\s*)?["']3\.3\.7["']/.test(g));
check('limpeza centralizada de títulos',h.includes('function rimaV59CleanTitle(value)')&&h.includes('esc(rimaV59CleanTitle(x[1]))')&&h.includes("esc(rimaV59CleanTitle(t.x[1]||''))"));
check('entidades HTML decodificadas antes de escapar',h.includes(".replace(/&quot;/gi,'\"')")&&h.includes(".replace(/&amp;/gi,'&')"));
check('fonte dos favoritos igual à lista',h.includes("font-family:Anton,Impact,'Arial Narrow',sans-serif!important;font-size:16px!important;font-weight:400!important"));
check('borda externa da seleção removida',h.includes('.rima-v43-fav-row.is-selected')&&h.includes('border:0!important;border-bottom:1px solid rgba(255,255,255,.075)!important'));
check('destaque aplicado apenas ao botão de beat',h.includes('.rima-v43-fav-play.is-selected')&&h.includes('box-shadow:none!important;outline:0!important'));
check('coração do player no tamanho dos outros controles',h.includes('#pbar #rima-v29-player-heart')&&h.includes('width:27px!important')&&h.includes('height:27px!important')&&h.includes('flex:0 0 27px!important'));
check('coração menos alto e estado preenchido preservado',h.includes('transform:scaleY(.82)!important')&&h.includes('[aria-pressed="true"]::before{content:\'♥\''));
check('espaço de rolagem no setup com player visível',h.includes('body.rima-v51-player-eligible #train-step-2')&&h.includes('padding-bottom:calc(112px'));
check('layout horizontal recupera cabeçalho e lista',h.includes('grid-template-columns:minmax(0,1fr) 88px!important')&&h.includes('grid-template-rows:30px 12px minmax(0,1fr)!important'));
check('lista horizontal mostra cartões em faixa',h.includes('display:flex!important;flex-direction:row!important')&&h.includes('overflow-x:auto!important')&&h.includes('flex:0 0 clamp(190px,27vw,310px)!important'));
check('gestos horizontais sem bloquear rolagem vertical',h.includes('touch-action:pan-x pan-y!important'));
check('patch V58 preservado',h.includes('rimalab-stage-selector-favorites-v58')&&h.includes('rimalab-startup-unfreeze-v57'));
const scripts=[...h.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)];
let syntax=true,errors=[];
for(let i=0;i<scripts.length;i++){try{new Function(scripts[i][1])}catch(e){syntax=false;errors.push('script '+i+': '+e.message)}}
check('sintaxe de todos os scripts inline',syntax,errors.join('; '));
const extra=path.join(root,'app/src/main/assets/beats/boom-bap-extra.json');
if(fs.existsSync(extra)){
 const data=JSON.parse(fs.readFileSync(extra,'utf8')),tracks=data.tracks||[];
 const bad=tracks.filter(t=>typeof t.name==='string'&&(/&quot;|^\s|\s$/.test(t.name)));
 check('JSON do catálogo sem entidades/espacos externos',bad.length===0,String(bad.length)+' título(s) ainda precisam de limpeza');
}
for(const x of pass)console.log('PASS '+x.n+(x.d?' — '+x.d:''));
for(const x of fail)console.log('FAIL '+x.n+(x.d?' — '+x.d:''));
console.log('V59_RESULT '+pass.length+' passed; '+fail.length+' failed');
if(fail.length)process.exit(1);
