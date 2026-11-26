#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]),h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8'),g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
 ['inicia sempre na etapa 1',h.includes("window.__rimaTrainStep=1;$('#train-step-1').hidden=false;$('#train-step-2').hidden=true;document.body.classList.remove('pl')")],
 ['resumo duplicado do modo oculto',h.includes('#module-summary{display:none!important}')],
 ['ajustador único de palavras',h.includes('rimalab-word-fit-v31')&&!h.includes('rimalab-word-fit-v28')&&!h.includes('rima-word-fit-v13')&&!h.includes('rimalab-word-vertical-fit-v24')],
 ['dicas não alteram fluxo vertical do palco',h.includes('#lv:not([hidden]) #stg.stage #rm{position:absolute')&&h.includes('#lv:not([hidden]) #stg.stage #rm span')],
 ['runtime integrado v30',h.includes('rimalab-complete-runtime-v31')],
 ['configuração da etapa 2 preservada',h.includes('rimalab-step2-persistence-v28')&&h.includes('rimalab_training_config_v28')],
 ['calibrador com sinal sonoro e visual',h.includes('cal-visual')&&h.includes('exponentialRampToValueAtTime(.64')],
 ['curvatura reduzida pela metade',h.includes('arc=Math.min(2.25,Math.max(.9,chars.length*.11))')],
 ['favoritos persistidos localmente',h.includes('rimalab_favorites_v29')&&h.includes('localStorage.setItem(KEY,JSON.stringify(fav))')],
 ['favoritos no catálogo antes do download',h.includes('rimaV29ToggleFav')&&h.includes('data-rima-fav')],
 ['coração no player',h.includes('rima-v29-player-heart')],
 ['playlist aleatória multi-categoria',h.includes('playRandomMix')&&h.includes('randomQueue')],
 ['fila respeita próximo/anterior',h.includes('window.zStep=function(d)')&&h.includes('playQueued(queue[qIndex])')],
 ['seletor de modo expansível',h.includes('rima-v29-mode-toggle')&&h.includes('rima-v29-mode-list')],
 ['banner imersivo do modo',h.includes('rima-v29-mode-banner')],
 ['mensagens rotativas',h.includes('rima-v29-rotator')&&h.includes('installMessages(true)')&&h.includes('lastEntryMessage')&&!h.includes('msgTimer')],
 ['voltar navega entre etapa e palco',h.includes("window.addEventListener('popstate'")&&h.includes('trainBack();history.pushState')],
 ['dupla confirmação para sair',h.includes('Pressione voltar novamente para sair')&&h.includes('Deseja realmente sair')],
 ['layout horizontal com navegação e player',h.includes('@media(orientation:landscape) and (max-height:850px)')&&h.includes('nav{left:12px')],
 ['observer do catálogo sem recursão',h.includes('observe(root,{childList:true,subtree:false})')],
 ['scroll horizontal bloqueado',h.includes('overscroll-behavior-y:none')&&h.includes('overflow-x:hidden')],
 ['ícone de notificação igual à marca do app',fs.existsSync(path.join(root,'app/src/main/res/drawable/ic_stat_beat.xml'))&&fs.readFileSync(path.join(root,'app/src/main/res/drawable/ic_stat_beat.xml'),'utf8').includes('viewportWidth=\"24\"')],
 ['palco com fluxo vertical sem sobreposição',h.includes('rimalab-stage-spacing-v32')&&h.includes('#rm{')&&h.includes('order:2!important')&&h.includes('order:3!important')],
 ['palavras com espaçamento legível e curvatura sutil',h.includes('letter-spacing:-.012em!important')&&h.includes('rima-curve-char')&&h.includes('translateY(var(--rima-curve-y,0px))')],
 ['dicas menores que a palavra principal',h.includes('main*.30')&&h.includes('Math.min(17,main*.30)')],
 ['versão 3.0.9 / code 51',g.includes('versionCode 51')&&g.includes('3.0.9')]
];
let fails=0;for(const [n,ok] of checks){console.log((ok?'PASS ':'FAIL ')+n);if(!ok)fails++}if(fails)process.exit(1);console.log(checks.length+'/'+checks.length+' verificações v30 passaram');
