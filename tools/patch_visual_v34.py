#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
if 'rimalab-runtime-favorites-resume-v34' in h:
    raise SystemExit('V34_FAIL: patch already present')

# Favorite IDs must use the same canonical key as ZS.key (jm-<catalog id>).
old="const keyOf=x=>String(x&&x[4]||'');"
new="const keyOf=x=>x&&x[4]!=null?'jm-'+String(x[4]):'';"
if old not in h:
    raise SystemExit('V34_FAIL: keyOf anchor not found')
h=h.replace(old,new,1)
old="let fav=[];try{fav=JSON.parse(localStorage.getItem(KEY)||'[]');if(!Array.isArray(fav))fav=[]}catch(e){}"
new="""let fav=[];try{fav=JSON.parse(localStorage.getItem(KEY)||'[]');if(!Array.isArray(fav))fav=[];fav=[...new Set(fav.filter(Boolean).map(k=>String(k).startsWith('jm-')?String(k):'jm-'+String(k)))];localStorage.setItem(KEY,JSON.stringify(fav))}catch(e){}"""
if old not in h:
    raise SystemExit('V34_FAIL: favorites migration anchor not found')
h=h.replace(old,new,1)

css=r"""
<style id="rimalab-runtime-favorites-resume-v34">
/* Stage typography: give the main word and rhyme chips separate vertical lanes. */
#lv:not([hidden]) #stg.stage #cb{
  flex:0 0 auto!important;min-height:clamp(76px,18vh,132px)!important;
  height:auto!important;margin:4px auto 0!important;padding:10px 4px 8px!important;
  line-height:1.12!important;letter-spacing:.012em!important;
}
#lv:not([hidden]) #stg.stage #rm{
  position:relative!important;inset:auto!important;flex:0 0 auto!important;
  min-height:0!important;height:auto!important;margin:10px auto 9px!important;
  padding:0 5px!important;gap:7px!important;transform:none!important;
}
#lv:not([hidden]) #stg.stage #rm>*{
  max-width:48%!important;margin:0!important;line-height:1.15!important;
}
#lv:not([hidden]) #stg.stage #sg{margin:5px 0 3px!important}
#lv:not([hidden]) #stg.stage #cs{margin:4px 0 7px!important}
#lv:not([hidden]) #stg.stage .v3bar{margin:8px auto 3px!important}
@media(orientation:landscape){
 #lv:not([hidden]) #stg.stage #cb{min-height:clamp(84px,19vh,126px)!important;margin-top:3px!important;padding:7px 4px!important}
 #lv:not([hidden]) #stg.stage #rm{margin:11px auto 8px!important;gap:8px!important}
 #lv:not([hidden]) #stg.stage #sg{margin:5px 0 3px!important}
}
/* Landscape player is docked immediately above Android's app navigation, never mid-screen. */
@media(orientation:landscape){
 #pbar{position:fixed!important;top:auto!important;left:10px!important;right:10px!important;
   bottom:calc(58px + env(safe-area-inset-bottom,0px))!important;transform:none!important;
   width:auto!important;max-width:none!important;z-index:120!important}
 body.pl main,body.pl #lv:not([hidden]){padding-bottom:150px!important}
}
</style>
"""
runtime=r"""
<script id="rimalab-runtime-favorites-resume-v34">
(function(){
'use strict';
const $=s=>document.querySelector(s);
function syncFavoriteCatalog(){
 let fav=[];try{fav=JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]')}catch(_){}
 if(!Array.isArray(fav))fav=[];
 const current=String(window.ZS&&ZS.key||'');
 const on=!!current&&fav.includes(current);
 const player=$('#rima-v29-player-heart');
 if(player){player.classList.toggle('on',on);player.textContent=on?'♥':'♡';player.setAttribute('aria-pressed',String(on))}
 document.querySelectorAll('[data-rima-fav]').forEach(b=>{
   const k=String(b.getAttribute('data-rima-fav')||'');
   const yes=fav.includes(k);
   b.classList.toggle('on',yes);b.textContent=yes?'♥':'♡';b.setAttribute('aria-pressed',String(yes));
 });
 document.querySelectorAll('.rima-v29-count').forEach(e=>e.textContent=String(fav.length));
}
function resumeStage(){
 if(document.visibilityState==='hidden')return;
 try{
  if(window.ctx&&ctx.state==='suspended')ctx.resume();
  if(window.play&&window.zPL){
   if(window.zA&&zA.paused)zA.play().catch(()=>{});
   else if(window.ZY&&ZY.p&&typeof ZY.p.play==='function'&&ZY.p.paused)ZY.p.play();
   if(typeof window.zTick==='function'){
    try{cancelAnimationFrame(window.zR)}catch(_){}
    const c=typeof zCur==='function'?zCur():0,br=240/(window.ZS&&ZS.bpm||90);
    const T=(window.zC||0)+c-(window.LAT||0)/1000-(window.ZS&&ZS.ph||0);
    if(br>0&&isFinite(T)){window.zL=c;window.zQ=Math.floor(T/(br/4));window.zBI=Math.floor(T/br);window.zPre=window.zBI}
    zTick();
   }
  }
  if(window.WD&&typeof window.wLoop==='function'){
   try{cancelAnimationFrame(WD.raf)}catch(_){}
   WD.l=performance.now();WD.raf=requestAnimationFrame(wLoop);
  }
  const stage=$('#stg');
  if(stage&&!$('#lv')?.hidden&&typeof window.rimaPulseStageFrame==='function')rimaPulseStageFrame();
  if(stage&&!$('#lv')?.hidden&&typeof window.rimaPulseStageWord==='function')rimaPulseStageWord();
  window.dispatchEvent(new Event('resize'));
  if(typeof window.zBarUI==='function')zBarUI();
  syncFavoriteCatalog();
 }catch(e){window.__rimaResumeError=String(e)}
}
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')setTimeout(resumeStage,80)});
window.addEventListener('pageshow',()=>setTimeout(resumeStage,80));
window.addEventListener('focus',()=>setTimeout(resumeStage,80));
window.addEventListener('orientationchange',()=>setTimeout(resumeStage,180));
document.addEventListener('click',e=>{
 if(e.target.closest('#rima-v29-player-heart,[data-rima-fav],#rima-v29-favs'))setTimeout(syncFavoriteCatalog,40);
});
const oldToggle=window.rimaV29ToggleFav;
if(typeof oldToggle==='function'&&!oldToggle.__v34){
 const wrapped=function(k){const r=oldToggle.apply(this,arguments);setTimeout(syncFavoriteCatalog,0);return r};
 wrapped.__v34=true;window.rimaV29ToggleFav=wrapped;
}
const oldShow=window.rimaV29ShowFavorites;
if(typeof oldShow==='function'&&!oldShow.__v34){
 const wrapped=function(){const r=oldShow.apply(this,arguments);setTimeout(syncFavoriteCatalog,0);return r};
 wrapped.__v34=true;window.rimaV29ShowFavorites=wrapped;
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{syncFavoriteCatalog();resumeStage()},{once:true});
else {syncFavoriteCatalog();resumeStage()}
})();
</script>
"""
pos=h.lower().rfind('</body>')
if pos<0:raise SystemExit('V34_FAIL: </body> not found')
h=h[:pos]+css+'\n'+runtime+'\n'+h[pos:]

g=gp.read_text(encoding='utf-8')
m=re.search(r'\bversionCode\s+(\d+)',g)
if not m:raise SystemExit('V34_FAIL: versionCode missing')
g=g[:m.start(1)]+'54'+g[m.end(1):]
m=re.search(r"""versionName\s+['"]([^'"]+)['"]""",g)
if not m:raise SystemExit('V34_FAIL: versionName missing')
g=g[:m.start(1)]+'3.1.2'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V34_OK: canonical favorite IDs + legacy migration, bidirectional player/catalog heart sync, favorites view key consistency, foreground/orientation animation resume, separated stage layout, landscape dock position; 3.1.2')
