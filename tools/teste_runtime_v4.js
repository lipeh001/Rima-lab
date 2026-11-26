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
 ['troca de faixa não chama rotina de reinício do palco',!h.includes("if(!zRestartAct())")],
 ['troca durante treino preserva scroll',h.includes('window.__rimaNoAutoScroll=1')&&h.includes('if(!window.__rimaNoAutoScroll)')],
 ['busca renova catálogo sem apagar beats salvos',h.includes('ZCATALOG_VERSION')&&h.includes("removeItem('jmraw8_at_'+st)")],
 ['API Jamendo envia include como lista, não separado por vírgula',h.includes('include=licenses+musicinfo')&&!h.includes('include=musicinfo%2Clicenses')],
 ['Drill exclui a faixa identificada pelo usuário',h.includes('with\\s+some\\s+money|all\\$?tarv')&&h.includes("st==='Drill'")],
 ['catálogo rejeita resultado marcado como vocal',h.includes("vi!=='instrumental'")],
 ['notificação pausada continua disponível no painel',main.includes('if (st < 0)')&&main.includes('.putExtra("st", st)')],
 ['canal de notificação novo e verificável',main.includes('getNotificationChannel(MusicService.CH)')&&service.includes('rimalab_player_v3')],
 ['Android usa MediaSession real',service.includes('new MediaSession(this, "RimaLabMedia")')&&service.includes('setMediaSession(mediaSession.getSessionToken())')],
 ['notification actions têm play/pause/next/previous/stop',service.includes('onSkipToNext')&&service.includes('onSkipToPrevious')&&service.includes('A_STOP')],
 ['bridge envia posição e duração reais para o Android',main.includes('mediaState(int st, String title, double duration, double position)')&&main.includes('.putExtra("duration"')&&main.includes('.putExtra("position"')],
 ['MediaSession publica duração e posição da faixa',service.includes('METADATA_KEY_DURATION')&&service.includes('currentPosition, playing ? 1f : 0f')],
 ['notificação atualiza o relógio durante a reprodução e não some na troca',h.includes('RimaNative.mediaState(st,title,d,c)')&&h.includes('if(play)zMedia(true)')&&h.includes('zMedia(false)')],
 ['calibrador aceita ajuste manual até 1200ms e persiste o valor',h.includes('max="1200"')&&h.includes('LATSET=true')&&h.includes('ctx.baseLatency')],
 ['botão voltar centralizado em todas as seções',h.includes('rima-back-center-v2')&&h.includes('justify-content:center')&&h.includes('margin-left:0!important')],
 ['botão Voltar permanece no canto esquerdo com texto centralizado',h.includes('rima-back-center-v2')&&h.includes('margin-left:0!important')&&h.includes('text-align:center!important')],
 ['selo do player mostra um único R ampliado',h.includes('<span>RL</span><i></i><i></i><i></i>')&&h.includes('font-size:17px!important')],
 ['calibrador mede a latência do pipeline sem pedir microfone',h.includes('ctx.baseLatency')&&h.includes('for(let i=0;i<9;i++)')&&!h.includes('getUserMedia')],
 ['calibrador usa mediana estável em passos de 5ms',h.includes('values.sort((a,b)=>a-b)')&&h.includes('Math.round(measured/5)*5')],
 ['palco usa relógio interpolado do áudio entre amostras do WebView',h.includes('let zClockP=0,zClockT=0,zClockR=1')&&h.includes('const estimate=zClockT+(p-zClockP)*zClockR')&&h.includes('zClockP=0;zClockT=0;')],



 ['catálogo adicionou beats reais com IDs sem duplicação',tracks.length>0&&tracks.length<=30&&manifest.count===tracks.length&&ids.size===tracks.length],
 ['cada beat extra tem áudio, título, artista e duração válida',tracks.every(x=>x.audio&&x.name&&x.artist&&x.duration>=85&&x.duration<=540)],
 ['Boom bap extra exclui lofi, chill e faixas sazonais',tracks.every(x=>!(/lofi|lo-fi|chill|relax|ambient|christmas|holiday|summer\\s*time|good\\s*vibes/i.test(x.name)))]
];
let bad=0;
for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++;}
console.log((checks.length-bad)+'/'+checks.length+' verificações runtime; '+tracks.length+' beats Boom bap novos validados');
process.exit(bad?1:0);
