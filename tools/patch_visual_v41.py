#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in [root/'app/build.gradle',root/'app/build.gradle.kts'] if p.exists()),None)
if gp is None: raise SystemExit('V41_FAIL: app Gradle file missing')
h=hp.read_text(encoding='utf-8')
if 'rimalab-playlist-player-landscape-v41' in h: raise SystemExit('V41 already applied')

# Replace the over-expanded v40 stage rules with compact, responsive spacing.
start=h.find('<style id="rimalab-stage-responsive-spacing-v40">')
if start<0: raise SystemExit('V41_FAIL: v40 stage CSS missing')
end=h.find('</style>',start)
if end<0: raise SystemExit('V41_FAIL: v40 stage CSS unterminated')
end+=len('</style>')
css=r"""<style id="rimalab-stage-responsive-spacing-v41">
#lv:not([hidden]) #stg.stage{
 box-sizing:border-box!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;
 align-items:stretch!important;overflow:visible!important;height:auto!important;max-height:none!important;
 min-height:clamp(430px,57svh,610px)!important;padding:clamp(13px,1.8vh,19px) clamp(12px,2vw,20px) clamp(13px,1.8vh,19px)!important;gap:0!important;
}
#lv:not([hidden]) #stg.stage #ck{flex:0 0 auto!important;margin:3px 0 5px!important;line-height:1.2!important}
#lv:not([hidden]) #stg.stage #cb{
 flex:0 0 auto!important;min-width:0!important;width:100%!important;max-width:100%!important;box-sizing:border-box!important;
 min-height:clamp(90px,13vh,140px)!important;height:auto!important;margin:4px auto 5px!important;padding:5px!important;
 line-height:1.1!important;letter-spacing:.025em!important;white-space:nowrap!important;
}
#lv:not([hidden]) #stg.stage #rm{
 position:relative!important;inset:auto!important;flex:0 0 auto!important;display:flex!important;flex-wrap:wrap!important;
 justify-content:center!important;align-items:center!important;gap:7px!important;width:100%!important;height:auto!important;
 min-height:0!important;margin:5px auto 9px!important;padding:0 4px!important;transform:none!important;pointer-events:none!important;
}
#lv:not([hidden]) #stg.stage #rm>*{
 box-sizing:border-box!important;max-width:48%!important;min-width:0!important;margin:0!important;
 font-size:clamp(12px,1.8vw,16px)!important;line-height:1.15!important;padding:5px 9px!important;white-space:nowrap!important;
}
#lv:not([hidden]) #stg.stage #sg{flex:0 0 auto!important;min-height:7px!important;margin:5px 0 2px!important}
#lv:not([hidden]) #stg.stage #cs{flex:0 0 auto!important;min-height:1.2em!important;margin:8px auto 0!important;padding:0 3px!important;line-height:1.25!important}
#lv:not([hidden]) #stg.stage .v3bar{
 position:relative!important;inset:auto!important;z-index:7!important;display:flex!important;flex:0 0 auto!important;
 justify-content:center!important;align-items:center!important;width:100%!important;margin:12px auto 0!important;
 padding:0 0 3px!important;min-height:44px!important;
}
#lv:not([hidden]) #stg.stage .v3bar button{
 flex:0 1 auto!important;min-width:min(190px,72%)!important;max-width:min(280px,92%)!important;
 min-height:42px!important;margin:0!important;padding:9px 15px!important;white-space:normal!important;
}
/* Landscape keeps the old compact proportions; only a small height increase for the hint button. */
@media(orientation:landscape){
 #lv:not([hidden]) #stg.stage{
  min-height:clamp(310px,40svh,410px)!important;height:auto!important;max-height:none!important;
  padding:9px clamp(12px,1.8vw,20px) 10px!important;
 }
 #lv:not([hidden]) #stg.stage #ck{margin:0 0 3px!important}
 #lv:not([hidden]) #stg.stage #cb{min-height:clamp(76px,15svh,112px)!important;margin:1px auto 3px!important;padding:2px 5px!important}
 #lv:not([hidden]) #stg.stage #rm{gap:5px!important;margin:3px auto 6px!important}
 #lv:not([hidden]) #stg.stage #rm>*{max-width:24%!important;padding:3px 6px!important;font-size:clamp(10px,1.35vw,14px)!important}
 #lv:not([hidden]) #stg.stage #sg{margin:4px 0 1px!important}
 #lv:not([hidden]) #stg.stage #cs{margin:5px auto 0!important;font-size:clamp(11px,1.45vw,14px)!important}
 #lv:not([hidden]) #stg.stage .v3bar{margin:8px auto 0!important;min-height:40px!important}
 #lv:not([hidden]) #stg.stage .v3bar button{min-height:38px!important;padding:7px 13px!important}
}
@media(max-width:380px){
 #lv:not([hidden]) #stg.stage{padding-left:10px!important;padding-right:10px!important}
 #lv:not([hidden]) #stg.stage #rm{gap:5px!important;padding:0 2px!important}
 #lv:not([hidden]) #stg.stage #rm>*{max-width:49%!important;padding:4px 7px!important;font-size:clamp(10px,3vw,13px)!important}
}
@media(orientation:landscape) and (max-height:380px){
 #lv:not([hidden]) #stg.stage{min-height:292px!important;padding-top:6px!important;padding-bottom:7px!important}
 #lv:not([hidden]) #stg.stage #cb{min-height:68px!important}
 #lv:not([hidden]) #stg.stage #rm{margin:1px auto 3px!important}
 #lv:not([hidden]) #stg.stage .v3bar{margin-top:5px!important;min-height:36px!important}
 #lv:not([hidden]) #stg.stage .v3bar button{min-height:34px!important;padding:5px 10px!important}
}
</style>"""
h=h[:start]+css+h[end:]

runtime=r"""<script id="rimalab-playlist-player-landscape-v41">
(function(){
 'use strict';
 const $=s=>document.querySelector(s);
 const favKey='rimalab_favorites_v29';
 let queue=null,qIndex=0,queueKind='',internalPlay=false,frozenTime=null;
 const keyOf=x=>'jm-'+String(x[4]);
 const tracks=()=>Object.keys(ZLIB||{}).flatMap(cat=>(ZLIB[cat]&&ZLIB[cat][1]||[]).map((x,i)=>({cat,x,i,key:keyOf(x)})));
 const readFav=()=>{try{return Array.from(new Set(JSON.parse(localStorage.getItem(favKey)||'[]').map(String)))}catch(_){return[]}};
 function playAt(i){
  if(!queue||!queue.length)return;
  i=(i+queue.length)%queue.length;const t=queue[i];if(!t)return;
  qIndex=i;internalPlay=true;
  try{window.zLP(t.i,0,t.cat)}finally{internalPlay=false}
  queueKind=queueKind||'category';
  setTimeout(syncQueueButtons,80);
 }
 function startFavorites(k){
  const all=tracks(),saved=readFav();
  queue=all.filter(t=>saved.includes(t.key));queueKind='favorites';
  if(!queue.length){queue=null;return}
  let i=queue.findIndex(t=>t.key===String(k));if(i<0)i=0;
  playAt(i);
 }
 function startCategory(cat,index){
  const all=tracks().filter(t=>t.cat===cat);if(!all.length)return;
  queue=all;queueKind='category';
  const i=queue.findIndex(t=>t.i===index);playAt(i<0?0:i);
 }
 function syncQueueButtons(){
  const sh=$('#pwsh'),rp=$('#pwrp');
  if(sh){sh.title=queueKind==='favorites'?'Aleatório nos favoritos':'Aleatório nesta categoria';sh.setAttribute('aria-label',sh.title)}
  if(rp)rp.title=queueKind==='favorites'?'Repetir playlist de favoritos':'Repetir playlist da categoria';
 }
 const oldLP=window.zLP;
 if(typeof oldLP==='function'&&!oldLP.__rimaV41){
  const wrapped=function(i,a,s){
   const result=oldLP.apply(this,arguments);
   if(!internalPlay&&ZS.k==='lib'&&ZS.s&&Array.isArray(ZLIB[ZS.s]?.[1]))startCategory(ZS.s,i);
   return result;
  };wrapped.__rimaV41=true;window.zLP=wrapped;
 }
 const oldLS=window.zLS;
 if(typeof oldLS==='function'&&!oldLS.__rimaV41){
  const wrapped=function(s){queue=null;qIndex=0;queueKind='';const r=oldLS.apply(this,arguments);syncQueueButtons();return r};
  wrapped.__rimaV41=true;window.zLS=wrapped;
 }
 const oldStep=window.zStep;
 window.zStep=function(d){
  if(queue&&queue.length){
   if(ZS.rep==='one'){playAt(qIndex);return}
   let n=qIndex+(d<0?-1:1);
   if(n<0)n=ZS.rep==='all'?queue.length-1:0;
   if(n>=queue.length)n=ZS.rep==='all'?0:queue.length-1;
   if(n===qIndex&&ZS.rep!=='all')return;
   playAt(n);return;
  }
  return oldStep&&oldStep(d);
 };
 const oldShuffle=window.zShuf;
 window.zShuf=function(){
  if(queue&&queue.length>1){
   ZS.shuf^=1;
   if(ZS.shuf){const current=queue[qIndex],rest=queue.filter((_,i)=>i!==qIndex);for(let i=rest.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[rest[i],rest[j]]=[rest[j],rest[i]]}queue=[current,...rest];qIndex=0}
   else if(queueKind==='favorites'){const saved=readFav();queue=tracks().filter(t=>saved.includes(t.key));qIndex=Math.max(0,queue.findIndex(t=>t.key===String(ZS.key)))}
   else {const cat=ZS.s;queue=tracks().filter(t=>t.cat===cat);qIndex=Math.max(0,queue.findIndex(t=>t.key===String(ZS.key)))}
   syncQueueButtons();if(typeof window.zBarUI==='function')zBarUI();return;
  }
  return oldShuffle&&oldShuffle();
 };
 const oldRepeat=window.zRep;
 window.zRep=function(){const r=oldRepeat&&oldRepeat();syncQueueButtons();return r};
 const oldEnd=window.zEnd;
 if(typeof oldEnd==='function'&&!oldEnd.__rimaV41){
  const wrapped=function(){
   if(queue&&queue.length&&ZS.k==='lib'){
    if(ZS.rep==='one'){playAt(qIndex);return}
    if(qIndex<queue.length-1){playAt(qIndex+1);return}
    if(ZS.rep==='all'){playAt(0);return}
    queue=null;qIndex=0;queueKind='';
   }
   return oldEnd.apply(this,arguments);
  };wrapped.__rimaV41=true;window.zEnd=wrapped;
 }
 window.rimaV29PlayFav=startFavorites;
 window.rimaV41StartFavorites=startFavorites;
 // Replace the old click adapter with a direct, reliable start of the matching track.
 document.addEventListener('click',e=>{
  const b=e.target&&e.target.closest?e.target.closest('.rima-v40-play[data-rima-play]'):null;
  if(!b)return;e.preventDefault();e.stopPropagation();startFavorites(b.getAttribute('data-rima-play'));
 },true);
 // When a new manual track is selected, queue is its whole category. zLP wrapper above handles it.
 // Freeze the displayed progress exactly at the paused audio position.
 const oldSet=window.zSetPL;
 if(typeof oldSet==='function'&&!oldSet.__rimaV41){
  const wrapped=function(v){
   if(!v){try{frozenTime=typeof zCur==='function'?zCur():frozenTime}catch(_){}}
   else frozenTime=null;
   const r=oldSet.apply(this,arguments);return r;
  };wrapped.__rimaV41=true;window.zSetPL=wrapped;
 }
 const oldUI=window.zUI;
 if(typeof oldUI==='function'&&!oldUI.__rimaV41){
  const wrapped=function(){
   if(typeof zPL!=='undefined'&&!zPL&&typeof play!=='undefined'&&play){
    const c=Math.max(0,frozenTime==null?(typeof zCur==='function'?zCur():0):frozenTime),d=typeof zDur==='function'?zDur():0;
    const w=(d>0?Math.min(100,c/d*100):0)+'%',f=$('#pwf'),k=$('#pwk'),t=$('#pwtm');
    if(f)f.style.width=w;if(k)k.style.left=w;if(t&&typeof zFm==='function')t.textContent=zFm(c)+(d>0?' / '+zFm(d):'');
    return;
   }
   return oldUI.apply(this,arguments);
  };wrapped.__rimaV41=true;window.zUI=wrapped;
 }
 function ensureHeart(){const b=$('#rima-v29-player-heart');if(b){b.type='button';b.style.pointerEvents='auto'}}
 function ready(){ensureHeart();syncQueueButtons()}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
 window.addEventListener('orientationchange',()=>setTimeout(ready,150));
})();
</script>"""
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V41_FAIL: body close missing')
h=h[:pos]+runtime+'\\n'+h[pos:]

# Ensure the slight character arc remains subtle and consistent after orientation changes.
curve=re.search(r'const arc=Math\.min\(([\d.]+),Math\.max\(([\d.]+),chars\.length\*([\d.]+)\)\)',h)
if curve:
 h=h[:curve.start()]+ 'const arc=Math.min(2.7,Math.max(1.1,chars.length*.12))'+h[curve.end():]

# Landscape player: compact two-line dock at the actual bottom, restore seek +/- controls.
player=r"""<style id="rimalab-player-landscape-dock-v41">
@media(orientation:landscape){
 #pbar{
  position:fixed!important;top:auto!important;bottom:3px!important;left:10px!important;right:10px!important;
  inset:auto 10px 3px 10px!important;transform:none!important;width:auto!important;max-width:none!important;
  height:auto!important;min-height:88px!important;max-height:104px!important;display:flex!important;
  flex-direction:column!important;align-items:stretch!important;justify-content:flex-start!important;
  gap:1px!important;margin:0!important;padding:6px 10px 5px!important;overflow:visible!important;
  z-index:12000!important;border-radius:16px!important;
 }
 #pbar .pwrow{display:flex!important;flex:1 1 auto!important;min-width:0!important;min-height:42px!important;gap:6px!important}
 #pbar .pw-art{display:none!important}
 #pbar .pw-controls{display:flex!important;flex:0 0 auto!important;align-items:center!important;gap:3px!important}
 #pbar .pw-controls button{width:29px!important;height:31px!important}
 #pbar .pw-controls #pwb{width:35px!important;height:35px!important}
 #pbar .pwi{display:block!important;flex:1 1 auto!important;min-width:0!important;overflow:hidden!important}
 #pbar #pwn{display:block!important;max-width:100%!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;font-size:clamp(11px,1.25vw,15px)!important}
 #pbar #pws{display:block!important;font-size:10px!important;line-height:1.15!important}
 #pbar button.pws,#pbar #rima-v29-player-heart{display:grid!important;width:29px!important;height:29px!important;flex:0 0 29px!important}
 #pbar .pwinfo{display:flex!important;position:absolute!important;right:12px!important;bottom:34px!important;height:11px!important;min-height:11px!important;margin:0!important;font-size:9px!important}
 #pbar .pwscr{
  display:flex!important;visibility:visible!important;position:relative!important;inset:auto!important;
  flex:0 0 25px!important;align-items:center!important;gap:8px!important;width:100%!important;height:25px!important;
  min-height:25px!important;margin:0!important;padding:0 2px!important;z-index:10!important;
 }
 #pbar .pwscr .pwm{display:grid!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;
  width:42px!important;min-width:42px!important;height:23px!important;flex:0 0 42px!important;font-size:10px!important}
 #pbar .pwscr .pwp{display:block!important;visibility:visible!important;position:relative!important;flex:1 1 auto!important;
  min-width:20px!important;width:auto!important;height:5px!important;min-height:5px!important;margin:0!important}
 #pbar .pwscr .pwp:before,#pbar .pwscr .pwp i{top:0!important;height:5px!important}
 #pbar .pwscr .pwp b{top:-4px!important;width:13px!important;height:13px!important;margin-left:-6px!important}
 body.pl main,body.pl #lv:not([hidden]){padding-bottom:100px!important}
}
@media(orientation:landscape) and (max-height:380px){
 #pbar{min-height:78px!important;max-height:84px!important;padding:4px 8px 3px!important}
 #pbar .pwrow{min-height:36px!important}
 #pbar .pw-controls button{width:25px!important;height:27px!important}
 #pbar .pw-controls #pwb{width:30px!important;height:30px!important}
 #pbar .pwscr{flex-basis:23px!important;min-height:23px!important}
 #pbar .pwinfo{bottom:30px!important}
}
</style>"""
pos=h.lower().rfind('</body>')
h=h[:pos]+player+'\\n'+h[pos:]

g=gp.read_text(encoding='utf-8')
m=re.search(r'\bversionCode\s*=?\s*(\d+)',g)
if not m: raise SystemExit('V41_FAIL: versionCode missing')
g=g[:m.start(1)]+'61'+g[m.end(1):]
m=re.search(r"""versionName\s*=?\s*['"]([^'"]+)['"]""",g)
if not m: raise SystemExit('V41_FAIL: versionName missing')
g=g[:m.start(1)]+'3.1.9'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V41_OK: favorites playlist/category queues, shuffle/repeat/navigation, paused progress freeze, bottom landscape player with +/-10s, compact responsive stage and subtle word curve; 3.1.9')
