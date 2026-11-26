#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
# Keep player/nav reserved area consistent in portrait and landscape; stage never gets resized by the dock.
css=r"""
<style id="rimalab-complete-v29">
:root{--rima-dock-space:154px}
body.pl main{padding-bottom:calc(var(--rima-dock-space) + env(safe-area-inset-bottom,0px))!important}
#pbar{bottom:calc(78px + env(safe-area-inset-bottom,0px))!important;z-index:90!important}
nav{position:fixed!important;left:12px!important;right:12px!important;bottom:calc(8px + env(safe-area-inset-bottom,0px))!important;z-index:91!important}
body.pl #pbar{bottom:calc(82px + env(safe-area-inset-bottom,0px))!important}
@media(orientation:landscape) and (max-height:850px){
 nav{left:12px!important;right:12px!important;bottom:calc(6px + env(safe-area-inset-bottom,0px))!important;min-height:48px!important}
 nav button{padding:5px 10px!important;min-height:46px!important}
 #pbar{left:12px!important;right:12px!important;width:auto!important;bottom:calc(60px + env(safe-area-inset-bottom,0px))!important;height:58px!important}
 body.pl main{padding-bottom:calc(126px + env(safe-area-inset-bottom,0px))!important}
 #lv:not([hidden]) #stg.stage{min-height:0!important;height:min(52vh,340px)!important;max-height:52vh!important}
 #lv:not([hidden]) #stg{padding:12px!important}
 #lv:not([hidden]) #ck,#lv:not([hidden]) #cs,#lv:not([hidden]) #cn{margin:3px 0!important}
}
@media(orientation:portrait){
 body.pl main{padding-bottom:calc(170px + env(safe-area-inset-bottom,0px))!important}
 #pbar{bottom:calc(86px + env(safe-area-inset-bottom,0px))!important}
 nav{bottom:calc(6px + env(safe-area-inset-bottom,0px))!important}
}
#lv:not([hidden]) #stg.stage{min-height:0!important}
#lv:not([hidden]) #cb{transform:none!important;letter-spacing:-.035em!important}
.mc,.btn,.tag,nav button{ -webkit-tap-highlight-color:transparent;touch-action:manipulation}
.mc:active,.btn:active,.tag:active{margin-right:0!important;transform:scale(.985);outline-offset:2px}
.rima-v29-banner{padding:18px 16px!important;margin:8px 0 14px!important;border:1px solid rgba(224,190,76,.26)!important;border-radius:20px!important;background:radial-gradient(ellipse at 85% 15%,rgba(220,183,62,.16),transparent 55%),linear-gradient(135deg,rgba(23,31,20,.98),rgba(12,16,13,.98))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.04),0 12px 28px rgba(0,0,0,.2)!important}
.rima-v29-banner strong{display:block;font-size:19px;letter-spacing:.12em;text-transform:uppercase;color:#e8c45c}
.rima-v29-banner p{margin:6px 0 0!important;font-size:12px!important;line-height:1.45;color:#b5bdac}
.rima-v29-rotator{min-height:22px;margin:8px 0 12px!important;color:#b9c0b0;font-size:12px;line-height:1.4}
.rima-v29-mode-toggle{width:100%;display:flex;align-items:center;justify-content:space-between;margin:8px 0 12px;padding:13px 15px;border:1px solid rgba(218,190,92,.35);border-radius:15px;background:linear-gradient(110deg,rgba(221,184,64,.13),rgba(116,95,183,.08));color:#f0e6c1;font-weight:800}
.rima-v29-mode-toggle:after{content:"";width:10px;height:10px;border-right:2px solid #e8c45c;border-bottom:2px solid #e8c45c;transform:rotate(45deg);transition:transform .2s}
.rima-v29-mode-toggle[aria-expanded=true]:after{transform:rotate(225deg)}
.rima-v29-mode-list{display:grid;gap:7px;overflow:hidden;max-height:0;opacity:0;transition:max-height .28s ease,opacity .2s ease}
.rima-v29-mode-list.open{max-height:360px;opacity:1}
.rima-v29-mode-list .mc{margin:0!important}
.rima-v29-fav{width:38px;height:38px;flex:0 0 38px;border-radius:50%;border:1px solid rgba(230,193,78,.35);background:rgba(230,193,78,.08);color:#d8d2c2;display:grid;place-items:center;font-size:19px}
.rima-v29-fav.on{color:#ffcb54;background:rgba(255,203,84,.16);border-color:#ffcb54}
.rima-v29-tools{display:flex;gap:8px;margin:10px 0 12px}
.rima-v29-tools button{flex:1;min-height:42px;border:1px solid rgba(220,190,80,.28);border-radius:13px;background:rgba(220,190,80,.08);color:#e8d89e;font-weight:750}
.rima-v29-tools button.active{background:rgba(220,190,80,.22);border-color:#e5c45b}
.rima-v29-count{display:inline-grid;place-items:center;min-width:20px;height:20px;margin-left:5px;padding:0 5px;border-radius:20px;background:#e3c15c;color:#17170f;font-size:10px}
#pbar #rima-v29-player-heart{width:30px;height:30px;flex:0 0 30px;background:transparent;border:1px solid rgba(255,203,84,.3);color:#aaa;box-shadow:none;font-size:18px}
#pbar #rima-v29-player-heart.on{color:#ffcb54;border-color:#ffcb54}
.rima-v29-note{padding:10px 12px!important;margin:8px 0!important;border-radius:12px!important;border:1px solid rgba(221,185,70,.24)!important;background:rgba(221,185,70,.07)!important;line-height:1.45!important}
html,body{overscroll-behavior-y:none}
body{overflow-x:hidden!important;max-width:100vw}
main,.tab,#train-step-1,#train-step-2{min-width:0!important;max-width:100%!important}
</style>
"""
if 'id="rimalab-complete-v29"' not in h:
 p=h.lower().rfind('</head>');h=h[:p]+css+h[p:] if p>=0 else h+css
script=r"""
<script id="rimalab-complete-runtime-v29">
(function(){
'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const KEY='rimalab_favorites_v29',MSG=[
'Cada barra é uma oportunidade de encontrar sua assinatura.',
'Respire, escute o compasso e confie na sua construção.',
'Consistência transforma treino em identidade.',
'Não procure a frase perfeita. Construa a próxima.',
'Presença, ritmo e intenção: mantenha os três vivos.',
'Seu melhor verso nasce quando você permanece no ritmo.',
'Experimente. Erre. Ajuste. Evolua.'
];
let fav=[];try{fav=JSON.parse(localStorage.getItem(KEY)||'[]');if(!Array.isArray(fav))fav=[]}catch(e){}
let favView=false,queue=null,qIndex=0,randomQueue=[],msgTimer=0,backArmed=false,backTimer=0,playingQueued=false;
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(fav))}catch(e){}updateCounts()};
const keyOf=x=>String(x&&x[4]||'');
const allTracks=()=>Object.keys(ZLIB||{}).flatMap(cat=>(ZLIB[cat]&&ZLIB[cat][1]||[]).map(x=>({cat,x})));
const getTrack=k=>allTracks().find(o=>keyOf(o.x)===String(k));
function updateCounts(){
 const n=fav.length;
 $$('.rima-v29-count').forEach(e=>e.textContent=String(n));
 const b=$('#rima-v29-favs');if(b)b.innerHTML='♥ Favoritos <span class="rima-v29-count">'+n+'</span>';
}
function toggleFav(k){
 k=String(k);if(!k)return;
 if(fav.includes(k))fav=fav.filter(x=>x!==k);else fav.push(k);
 save();decorateCatalog();const p=$('#rima-v29-player-heart');if(p)p.classList.toggle('on',fav.includes(String(ZS&&ZS.key||'')));
}
window.rimaV29ToggleFav=toggleFav;
function favButton(k){return '<button class="rima-v29-fav '+(fav.includes(String(k))?'on':'')+'" data-rima-fav="'+String(k).replace(/[^a-zA-Z0-9_-]/g,'')+'" onclick="rimaV29ToggleFav(\''+String(k).replace(/[^a-zA-Z0-9_-]/g,'')+'\');event.stopPropagation()" aria-label="'+(fav.includes(String(k))?'Remover dos favoritos':'Adicionar aos favoritos')+'">'+(fav.includes(String(k))?'♥':'♡')+'</button>'}
function decorateCatalog(){
 $$('.bsl .bi').forEach(row=>{
  if(row.querySelector('[data-rima-fav]'))return;
  const info=row.querySelector('.beat-info'),dl=row.querySelector('.dlb');if(!info||!dl)return;
  const title=info.querySelector('.mc b')?.textContent||'';
  const track=allTracks().find(o=>o.x[1]===title);
  if(!track)return;
  const k=keyOf(track.x);dl.insertAdjacentHTML('beforebegin',favButton(k));
 });
 const heart=$('#rima-v29-player-heart');
 if(heart)heart.classList.toggle('on',!!(window.ZS&&ZS.key&&fav.includes(String(ZS.key))));
 updateCounts();
}
function installTools(){
 const bp=$('#bp');if(!bp)return;
 let tools=$('#rima-v29-tools');
 if(!tools){tools=document.createElement('div');tools.id='rima-v29-tools';tools.className='rima-v29-tools';bp.appendChild(tools)}
 tools.innerHTML='<button id="rima-v29-random">⤨ Beat aleatório</button><button id="rima-v29-favs">♥ Favoritos <span class="rima-v29-count">'+fav.length+'</span></button>';
 $('#rima-v29-random').onclick=playRandomMix;
 $('#rima-v29-favs').onclick=showFavorites;
}
function showFavorites(){
 favView=true;queue=fav.slice();qIndex=0;
 const bp=$('#bp');if(!bp)return;
 const tracks=fav.map(getTrack).filter(Boolean);
 bp.innerHTML='<div class="rima-v29-tools"><button class="active">♥ Favoritos <span class="rima-v29-count">'+fav.length+'</span></button><button id="rima-v29-backcat">Voltar às categorias</button></div><p class="mut">'+tracks.length+' beat(s) salvo(s) nos favoritos.</p><div class="bsl">'+tracks.map(({cat,x})=>{const k=keyOf(x);return '<div class="bi"><div class="beat-info"><button class="mc" onclick="rimaV29PlayFav(\''+k+'\')"><b>'+String(x[1]).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))+'</b></button><div class="beat-meta">'+cat+'</div></div>'+favButton(k)+'</div>'}).join('')+'</div>';
 $('#rima-v29-backcat').onclick=()=>{favView=false;pk();installTools()};
 if(!tracks.length)bp.insertAdjacentHTML('beforeend','<p class="rima-v29-note">Ainda não há beats favoritos. Toque no coração de qualquer beat para guardá-lo aqui.</p>');
}
function playRandomMix(){
 const tracks=allTracks().filter(o=>o.x&&o.x[0]&&o.x[1]);
 if(!tracks.length)return;
 randomQueue=tracks.map(o=>({cat:o.cat,k:keyOf(o.x)})).sort(()=>Math.random()-.5);
 queue=randomQueue.map(o=>o.k);qIndex=0;
 playQueued(queue[0]);
}
function playQueued(k){
 const o=getTrack(k);if(!o)return;
 ZS.s=o.cat;const i=(ZLIB[o.cat][1]||[]).findIndex(x=>keyOf(x)===String(k));
 if(i<0)return;
 zLP(i,0,o.cat);ZS.shuf=0;zBarUI();
}
const oldStep=window.zStep;
window.zStep=function(d){
 if(queue&&queue.length){
  if(ZS.rep==='one'){playQueued(queue[qIndex]);return}
  qIndex=(qIndex+d+queue.length)%queue.length;
  playQueued(queue[qIndex]);return;
 }
 return oldStep&&oldStep(d);
};
const oldLP=window.zLP;
window.zLP=function(i,a,s){
 queue=null;qIndex=0;
 }\n const ret=oldLP.apply(this,arguments);
 setTimeout(()=>{const p=$('#rima-v29-player-heart');if(p)p.classList.toggle('on',!!(ZS.key&&fav.includes(String(ZS.key))))},50);
 return ret;
};
const oldPick=window.zBpick;
if(oldPick)window.zBpick=function(live){
 let out=oldPick.apply(this,arguments);
 out=out.replace('</div><div class="bsl">','</div><div class="rima-v29-tools"><button onclick="rimaV29Random()">⤨ Beat aleatório</button><button onclick="rimaV29ShowFavorites()">♥ Favoritos <span class="rima-v29-count">'+fav.length+'</span></button></div><div class="bsl">');
 return out;
};
window.rimaV29Random=playRandomMix;window.rimaV29ShowFavorites=showFavorites;window.rimaV29PlayFav=k=>{queue=fav.slice();qIndex=queue.indexOf(String(k));if(qIndex<0)qIndex=0;playQueued(queue[qIndex])};
function addPlayerHeart(){
 const row=$('#pbar .pwrow');if(!row||$('#rima-v29-player-heart'))return;
 const b=document.createElement('button');b.id='rima-v29-player-heart';b.className='pws';b.textContent='♡';b.title='Adicionar aos favoritos';b.onclick=()=>{if(!ZS||!ZS.key)return;toggleFav(ZS.key);b.textContent=fav.includes(String(ZS.key))?'♥':'♡';b.classList.toggle('on',fav.includes(String(ZS.key)))};
 const after=$('#pbar .pwi');if(after)after.insertAdjacentElement('afterend',b);else row.appendChild(b);
}
function modeName(){const m=(MD3||[]).find(x=>x[0]===mode);return m?m[1]:'Modo de treino'}
function modeDesc(){const m=(MD3||[]).find(x=>x[0]===mode);return m?m[2]:'Treine ritmo, presença e criatividade.'}
function installModeBanner(){
 const step=$('#train-step-2');if(!step)return;
 let banner=$('#rima-v29-mode-banner');
 if(!banner){banner=document.createElement('section');banner.id='rima-v29-mode-banner';banner.className='rima-v29-banner';const head=step.querySelector('.stp');if(head)head.insertAdjacentElement('beforebegin',banner);else step.prepend(banner)}
 banner.innerHTML='<strong>'+modeName()+'</strong><p>'+modeDesc()+'</p>';
 const first=$('#module-options');
 if(first&&!$('#rima-v29-mode-toggle')){
  const wrap=document.createElement('div');wrap.innerHTML='<button id="rima-v29-mode-toggle" class="rima-v29-mode-toggle" aria-expanded="false"><span>Trocar modo de treino</span></button><div id="rima-v29-mode-list" class="rima-v29-mode-list"></div>';
  first.insertAdjacentElement('beforebegin',wrap);
  const btn=$('#rima-v29-mode-toggle'),list=$('#rima-v29-mode-list');
  list.innerHTML=(MD3||[]).map(([k,n,d])=>'<button class="mc '+(k===mode?'on':'')+'" data-mode="'+k+'"><b>'+n+'</b><small>'+d+'</small></button>').join('');
  list.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{setMode(b.dataset.mode);installModeBanner();list.classList.remove('open');btn.setAttribute('aria-expanded','false');list.querySelectorAll('.mc').forEach(x=>x.classList.toggle('on',x.dataset.mode===mode))});
  btn.onclick=()=>{const open=!list.classList.contains('open');list.classList.toggle('open',open);btn.setAttribute('aria-expanded',String(open))};
 }
}
function installMessages(){
 const step=$('#train-step-2');if(!step)return;
 let el=$('#rima-v29-rotator');
 if(!el){el=document.createElement('p');el.id='rima-v29-rotator';el.className='rima-v29-rotator';const banner=$('#rima-v29-mode-banner');if(banner)banner.insertAdjacentElement('afterend',el)}
 if(!el.dataset.started){el.dataset.started='1';let i=Math.floor(Math.random()*MSG.length);el.textContent=MSG[i];clearInterval(msgTimer);msgTimer=setInterval(()=>{i=(i+1)%MSG.length;el.style.opacity='0';setTimeout(()=>{el.textContent=MSG[i];el.style.opacity='1'},220)},6500)}
}
function updateModeUI(){installModeBanner();installMessages()}
function setupBack(){
 history.pushState({rimaV29:1},'','#rima');
 window.addEventListener('popstate',()=>{
  const lv=$('#lv'),s2=$('#train-step-2'),s1=$('#train-step-1');
  if(lv&&!lv.hidden){lvStop();history.pushState({rimaV29:1},'','#rima');return}
  if(s2&&!s2.hidden){trainBack();history.pushState({rimaV29:1},'','#rima');return}
  if(s1&&!s1.hidden){
   if(!backArmed){backArmed=true;const note='Pressione voltar novamente para sair do Rima Lab.';if(window.RimaNative&&RimaNative.toast)RimaNative.toast(note);else alert(note);clearTimeout(backTimer);backTimer=setTimeout(()=>backArmed=false,2200);history.pushState({rimaV29:1},'','#rima');return}
   backArmed=false;
   if(confirm('Deseja realmente sair do Rima Lab?')){if(window.RimaNative&&RimaNative.exitApp)RimaNative.exitApp();else{history.pushState({rimaV29:1},'','#rima')}}
   else history.pushState({rimaV29:1},'','#rima');
  }
 });
}
function stabilizeStage(){const stage=$('#stg'),cb=$('#cb');if(!stage||!cb)return;cb.style.setProperty('max-width','100%','important');cb.style.setProperty('box-sizing','border-box','important');}\nfunction init(){
 installTools();addPlayerHeart();decorateCatalog();updateCounts();updateModeUI();setupBack();stabilizeStage();
 const root=$('#bp');if(root)new MutationObserver(()=>{decorateCatalog();installTools()}).observe(root,{childList:true,subtree:true});
 const s2=$('#train-step-2');if(s2)new MutationObserver(()=>{if(!s2.hidden)updateModeUI()}).observe(s2,{attributes:true,attributeFilter:['hidden']});
 const modeRoot=$('#md');if(modeRoot)new MutationObserver(()=>{if(!$('#train-step-2')?.hidden)updateModeUI()}).observe(modeRoot,{childList:true,subtree:true});
 setInterval(()=>{addPlayerHeart();decorateCatalog();updateCounts()},1500);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
</script>
"""
if 'id="rimalab-complete-runtime-v29"' not in h:
 p=h.lower().rfind('</body>')
 if p<0:raise SystemExit('V29_FAIL: body não encontrado')
 h=h[:p]+script+'\n'+h[p:]
# fix word curvature from existing curve script by halving CSS transform amount where explicit variable exists
h=h.replace('arc=Math.min(4.5,Math.max(1.8,chars.length*.22))','arc=Math.min(2.25,Math.max(.9,chars.length*.11))')
# version bump
g=gp.read_text(encoding='utf-8')
m=re.search(r'versionCode\s+(\d+)',g)
if not m:raise SystemExit('V29_FAIL: versionCode ausente')
if int(m.group(1))<48:g=g[:m.start(1)]+'48'+g[m.end(1):]
m=re.search(r"versionName\s+['\"]([^'\"]+)['\"]",g)
if not m:raise SystemExit('V29_FAIL: versionName ausente')
if m.group(1)<'3.0.6':g=g[:m.start(1)]+'3.0.6'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V29_OK: favoritos, fila aleatória, player heart, modo banner e seletor, mensagens rotativas, back navigation, CSS responsivo e versão 3.0.6')
