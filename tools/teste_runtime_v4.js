#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]||'.');
const assets=path.join(root,'app/src/main/assets');
const h=fs.readFileSync(path.join(assets,'rima-lab.html'),'utf8');
const main=fs.readFileSync(path.join(root,'app/src/main/java/app/rimalab/MainActivity.java'),'utf8');
const service=fs.readFileSync(path.join(root,'app/src/main/java/app/rimalab/MusicService.java'),'utf8');
const p=path.join(assets,'beats/boom-bap-extra.json');
const manifest=JSON.parse(fs.readFileSync(p,'utf8'));
const ids=new Set((manifest.tracks||[]).map(x=>String(x.id)));
const checks=[
 ['player em paisagem usa dock horizontal compacto',h.includes('rima-runtime-v4')&&h.includes('#pbar .pwscr { display:none')&&h.includes('orientation:landscape')],
 ['palco em paisagem reserva área e não fica sob o player',h.includes('#lv>.stage { grid-column:1!important')&&h.includes('body.pl main { padding-bottom:calc(136px')],
 ['luz pulsa na moldura sem aplicar animação nas letras',h.includes('rl-edge-energy')&&h.includes('#stg.stage.hit::after')&&!h.includes('.stage.hit .word{animation:rl-edge-energy')],
 ['troca de faixa não dispara dois redraws',h.includes("function zSwap(){if(play){if(!zRestartAct()){zLoad(ZS.k=='syn'?zBars():0);pk()}return}pk()}")],
 ['troca durante treino preserva scroll',h.includes('window.__rimaNoAutoScroll=1')&&h.includes('if(!window.__rimaNoAutoScroll)')],
 ['cache do Jamendo é renovado sem apagar beats salvos',h.includes('ZCATALOG_VERSION')&&h.includes('!ZCATALOG_FORCE_REFRESH&&zCacheFresh')],
 ['30 beats extras do Jamendo têm IDs únicos',manifest.tracks.length===30&&ids.size===30),
 ['cada beat extra tem áudio, nome, artista e duração',manifest.tracks.every(x=>x.audio&&x.name&&x.artist&&x.duration>=85)],
 ['cada beat extra passou por teste de resposta de áudio',manifest.verifiedCount===30&&manifest.tracks.every(x=>x.audio)],
 ['Drill exclui a faixa identificada pelo usuário',h.includes('with\\s+some\\s+money|all\\$?tarv')&&h.includes("st==='Drill'")],
 ['catálogo rejeita resultado marcado como vocal',h.includes("vi!=='instrumental'")],
 ['notificação pausada continua disponível no painel',main.includes('if (st < 0)')&&main.includes('.putExtra("st", st)')],
 ['canal de notificação novo e verificável',main.includes('getNotificationChannel(MusicService.CH)')&&service.includes('rimalab_player_v3')],
 ['Android usa MediaSession real',service.includes('new MediaSession(this, "RimaLabMedia")')&&service.includes('setMediaSession(mediaSession.getSessionToken())')],
 ['notification actions têm play/pause/next/previous/stop',service.includes('onSkipToNext')&&service.includes('onSkipToPrevious')&&service.includes('A_STOP')]
];
let bad=0;
for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++;}
console.log((checks.length-bad)+'/'+checks.length+' verificações runtime');
process.exit(bad?1:0);
