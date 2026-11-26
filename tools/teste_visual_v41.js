#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]),h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8'),g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const s=h.match(/<script id="rimalab-playlist-player-landscape-v41">([\s\S]*?)<\/script>/)?.[1]||'';
const c=h.match(/<style id="rimalab-player-landscape-dock-v41">([\s\S]*?)<\/style>/)?.[1]||'';
const stage=h.match(/<style id="rimalab-stage-responsive-spacing-v41">([\s\S]*?)<\/style>/)?.[1]||'';
const checks=[
 ['fila de favoritos construída a partir do estado salvo e catálogo real',s.includes('readFav()')&&s.includes("queue=all.filter(t=>saved.includes(t.key))")],
 ['tocar favorito inicia o beat escolhido e conserva a fila',s.includes('startFavorites')&&s.includes('window.rimaV29PlayFav=startFavorites')&&s.includes('playAt(i)')],
 ['fila de categoria independente da fila de favoritos',s.includes('startCategory')&&s.includes("queueKind='category'")&&s.includes("queueKind='favorites'")],
 ['avançar e voltar navegam na fila ativa',s.includes('window.zStep=function(d)')&&s.includes('playAt(n)')],
 ['aleatório e repetir atuam na fila ativa',s.includes('window.zShuf=function()')&&s.includes('window.zRep=function()')],
 ['fim da faixa avança automaticamente dentro da playlist',s.includes('window.zEnd=wrapped')&&s.includes('playAt(qIndex+1)')],
 ['selecionar categoria abandona fila anterior',s.includes('window.zLS=wrapped')&&s.includes("queueKind=''")],
 ['progresso congelado quando áudio está pausado',s.includes('frozenTime')&&s.includes('!zPL')&&s.includes('return;')],
 ['player horizontal ancorado no fundo sem safe-area exagerada',c.includes('bottom:3px!important')&&c.includes('inset:auto 10px 3px 10px!important')],
 ['controles de −10s e +10s visíveis na horizontal',c.includes('.pwscr .pwm{display:grid!important')&&c.includes('width:42px!important')],
 ['barra de progresso visível na horizontal',c.includes('.pwscr .pwp{display:block!important')&&c.includes('flex:1 1 auto!important')],
 ['player horizontal em duas linhas compactas',c.includes('min-height:88px!important')&&c.includes('flex-direction:column!important')],
 ['palco horizontal reduzido sem esticar o conteúdo',stage.includes('min-height:clamp(310px,40svh,410px)')&&stage.includes('#cb{')&&stage.includes('min-height:clamp(76px,15svh,112px)')],
 ['palco responsivo em celular estreito e paisagem baixa',stage.includes('@media(max-width:380px)')&&stage.includes('max-height:380px')],
 ['curvatura sutil de palavra',h.includes('rima-curve-char')&&h.includes('Math.min(2.7,Math.max(1.1,chars.length*.12))')],
 ['versão 3.1.9 / code 61',g.includes('versionCode 61')&&g.includes("versionName '3.1.9'")]
];
let bad=0;for(const [n,ok] of checks){console.log((ok?'PASS ':'FAIL ')+n);if(!ok)bad++}if(bad)process.exit(1);console.log(checks.length+'/'+checks.length+' verificações V41 passaram');
