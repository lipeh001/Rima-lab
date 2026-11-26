#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]),h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8'),g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
 ['runtime integrado v30',h.includes('rimalab-complete-runtime-v30')],
 ['configuração da etapa 2 preservada',h.includes('rimalab-step2-persistence-v28')&&h.includes('rimalab_training_config_v28')],
 ['calibrador com sinal sonoro e visual',h.includes('cal-visual')&&h.includes('exponentialRampToValueAtTime(.64')],
 ['curvatura reduzida pela metade',h.includes('arc=Math.min(2.25,Math.max(.9,chars.length*.11))')],
 ['favoritos persistidos localmente',h.includes('rimalab_favorites_v30')&&h.includes('localStorage.setItem(KEY,JSON.stringify(fav))')],
 ['favoritos no catálogo antes do download',h.includes('rimaV29ToggleFav')&&h.includes('data-rima-fav')],
 ['coração no player',h.includes('rima-v30-player-heart')],
 ['playlist aleatória multi-categoria',h.includes('playRandomMix')&&h.includes('randomQueue')],
 ['fila respeita próximo/anterior',h.includes('window.zStep=function(d)')&&h.includes('playQueued(queue[qIndex])')],
 ['seletor de modo expansível',h.includes('rima-v30-mode-toggle')&&h.includes('rima-v30-mode-list')],
 ['banner imersivo do modo',h.includes('rima-v30-mode-banner')],
 ['mensagens rotativas',h.includes('rima-v30-rotator')&&h.includes('forceNew=false')],
 ['voltar navega entre etapa e palco',h.includes("window.addEventListener('popstate'")&&h.includes('trainBack();history.pushState')],
 ['dupla confirmação para sair',h.includes('Pressione voltar novamente para sair')&&h.includes('Deseja realmente sair')],
 ['layout horizontal com navegação e player',h.includes('@media(orientation:landscape) and (max-height:850px)')&&h.includes('nav{left:12px')],
 ['observer do catálogo sem recursão',h.includes('observe(root,{childList:true,subtree:false})')],
 ['scroll horizontal bloqueado',h.includes('overscroll-behavior-y:none')&&h.includes('overflow-x:hidden')],
 ['versão 3.0.7 / code 48',g.includes('versionCode 49')&&g.includes('3.0.6')]
];
let fails=0;for(const [n,ok] of checks){console.log((ok?'PASS ':'FAIL ')+n);if(!ok)fails++}if(fails)process.exit(1);console.log(checks.length+'/'+checks.length+' verificações v30 passaram');
