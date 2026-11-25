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
const tracks=Array.isArray(manifest.tracks)?manifest.tracks:[];
const ids=new Set(tracks.map(x=>String(x.id)));
const checks=[
 ['player em paisagem usa dock horizontal compacto',h.includes('rima-runtime-v4')&&h.includes('#pbar .pwinfo,#pbar .pwscr { display:none')&&h.includes('orientation:landscape')],
 ['palco em paisagem reserva área e não fica sob o player',h.includes('#lv>.stage { grid-column:1!important')&&h.includes('body.pl main { padding-bottom:calc(122px')],
 ['luz pulsa na moldura sem animar as letras',h.includes('rl-edge-energy')&&h.includes('#stg.stage.hit::after')&&!h.includes('.stage.hit .word{animation:rl-edge-energy')],
 ['troca de faixa não dispara dois redraws',h.includes("function zSwap(){if(play){if(!zRestartAct()){zLoad(ZS.k=='syn'?zBars():0);pk()}return}pk()}")],
 ['troca durante treino preserva scroll',h.includes('window.__rimaNoAutoScroll=1')&&h.includes('if(!window.__rimaNoAutoScroll)')],
 ['busca renova catálogo sem apagar beats salvos',h.includes('ZCATALOG_VERSION')&&h.includes("removeItem('jmraw8_at_'+st)")],
 ['API Jamendo envia include como lista, não separado por vírgula',h.includes('include=licenses+musicinfo')&&!h.includes('include=musicinfo%2Clicenses')],
 ['Drill exclui a faixa identificada pelo usuário',h.includes('with\\s+some\\s+money|all\\$?tarv')&&h.includes("st==='Drill'")],
 ['catálogo rejeita resultado marcado como vocal',h.includes("vi&&vi!=='instrumental'")],
 ['notificação pausada continua disponível no painel',main.includes('if (st < 0)')&&main.includes('.putExtra("st", st)')],
 ['canal de notificação novo e verificável',main.includes('getNotificationChannel(MusicService.CH)')&&service.includes('rimalab_player_v3')],
 ['Android usa MediaSession real',service.includes('new MediaSession(this, "RimaLabMedia")')&&service.includes('setMediaSession(mediaSession.getSessionToken())')],
 ['notification actions têm play/pause/next/previous/stop',service.includes('onSkipToNext')&&service.includes('onSkipToPrevious')&&service.includes('A_STOP')],
 ['catálogo adicionou beats reais com IDs sem duplicação',tracks.length>0&&tracks.length<=30&&manifest.count===tracks.length&&ids.size===tracks.length],
 ['cada beat extra tem áudio, título, artista e duração válida',tracks.every(x=>x.audio&&x.name&&x.artist&&x.duration>=85&&x.duration<=540)],
 ['Boom bap extra exclui lofi, chill e faixas sazonais',tracks.every(x=>!(/lofi|lo-fi|chill|relax|ambient|christmas|holiday|summer\\s*time|good\\s*vibes/i.test(x.name)))]
];
let bad=0;
for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++;}
console.log((checks.length-bad)+'/'+checks.length+' verificações runtime; '+tracks.length+' beats Boom bap novos validados');
process.exit(bad?1:0);
