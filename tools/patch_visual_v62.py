#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V62_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-favorites-player-scroll-stage-v62' in h: raise SystemExit('V62_FAIL: patch já aplicado')
if 'function fixLandscapeList()' not in h or 'rimalab-player-state-settle-v54' not in h or 'rimalab-consistent-heart-favorites-v60' not in h:
 raise SystemExit('V62_FAIL: base V60/V61/V54 ausente')

# The original V31 catalog decorator predates the Favorites .bsl/.bi markup and
# was injecting a second data-rima-fav button into every Favorites row.
v31_tag='<script id="rimalab-complete-runtime-v31">'
v31_a=h.find(v31_tag)
if v31_a<0: raise SystemExit('V62_FAIL: runtime V31 ausente')
v31_b=v31_a+len(v31_tag);v31_z=h.find('</script>',v31_b)
if v31_z<0: raise SystemExit('V62_FAIL: fechamento V31 ausente')
v31_js=h[v31_b:v31_z]
v31_old="$('.bsl .bi').forEach(row=>{\\n  if(row.querySelector('[data-rima-fav]'))return;"
v31_new="$('.bsl .bi').forEach(row=>{\\n  if(row.classList.contains('rima-v43-fav-row')||row.closest('.rima-v43-favlist')||row.querySelector('[data-rima-fav]'))return;"
if v31_js.count(v31_old)!=1: raise SystemExit('V62_FAIL: decorator V31 não corresponde')
v31_js=v31_js.replace(v31_old,v31_new,1)
h=h[:v31_b]+v31_js+h[v31_z:]

# V54's generic catalog decorator also sees Favorites rows after V61 gave them
# the .bsl > .bi catalog structure. It was injecting a second heart into each row.
tag='<script id="rimalab-player-state-settle-v54">'
a=h.find(tag)
if a<0: raise SystemExit('V62_FAIL: runtime V54 ausente')
b=a+len(tag);z=h.find('</script>',b)
if z<0: raise SystemExit('V62_FAIL: fechamento V54 ausente')
js=h[b:z]
old="if(row.querySelector('[data-rima-fav]'))return;"
new="if(row.classList.contains('rima-v43-fav-row')||row.closest('.rima-v43-favlist')||row.querySelector('[data-rima-fav]'))return;"
if js.count(old)!=1: raise SystemExit('V62_FAIL: decorator V54 não corresponde')
js=js.replace(old,new,1)
h=h[:b]+js+h[z:]

runtime=r'''<script id="rimalab-favorites-player-scroll-stage-v62">
(function(){
 'use strict';
 const FAV_KEY='rimalab_favorites_v29';
 let savedStageScroll=null,stageActive=false;
 const readFav=()=>{try{const a=JSON.parse(localStorage.getItem(FAV_KEY)||'[]');return new Set(Array.isArray(a)?a.map(String):[])}catch(_){return new Set()}};
 const selectedKey=()=>typeof ZS!=='undefined'&&ZS&&ZS.k==='lib'&&ZS.key?String(ZS.key):'';
 function ensurePlayerHeart(){
  const row=document.querySelector('#pbar .pwrow');if(!row)return null;
  let b=document.getElementById('rima-v29-player-heart');
  if(!b){
   b=document.createElement('button');b.id='rima-v29-player-heart';b.type='button';b.className='pws';
   b.addEventListener('click',()=>{const key=selectedKey();if(key&&typeof window.rimaV29ToggleFav==='function')window.rimaV29ToggleFav(key);settle()});
   const after=row.querySelector('.pwi');if(after)after.insertAdjacentElement('afterend',b);else row.appendChild(b);
  }
  return b;
 }
 function syncPlayerHeart(){
  const b=ensurePlayerHeart();if(!b)return;
  const key=selectedKey(),on=!!key&&readFav().has(key);
  b.classList.toggle('on',on);b.setAttribute('aria-pressed',String(on));
  b.setAttribute('aria-label',on?'Remover dos favoritos':'Adicionar aos favoritos');
  b.title=on?'Remover dos favoritos':'Adicionar aos favoritos';
  b.textContent='';
 }
 function cleanFavoriteRows(){
  document.querySelectorAll('#bp .rima-v43-fav-row,#bq .rima-v43-fav-row,#bbq .rima-v43-fav-row').forEach(row=>{
   row.querySelectorAll('button[data-rima-fav]:not(.rima-v43-fav-heart),button.rima-v29-fav:not(.rima-v43-fav-heart)').forEach(b=>b.remove());
   const hearts=Array.from(row.querySelectorAll('button.rima-v43-fav-heart,button[data-v43-heart]'));
   if(hearts.length){
    const keep=hearts.find(b=>b.classList.contains('rima-v43-fav-heart'))||hearts[0];
    hearts.filter(b=>b!==keep).forEach(b=>b.remove());
    keep.textContent='';
    keep.classList.add('rima-v29-fav');
    keep.setAttribute('aria-pressed','true');
    keep.setAttribute('aria-label','Remover dos favoritos');
    keep.title='Remover dos favoritos';
   }
  });
 }
 function syncCategories(){
  const favOpen=!!document.querySelector('#bp>.rima-v43-tools .rima-v43-toggle.active,#bq>.rima-v43-tools .rima-v43-toggle.active');
  const selected=String(typeof ZS!=='undefined'&&ZS&&ZS.s||'').trim().toLowerCase();
  document.querySelectorAll('#bp .rima-v50-category-row .tag.chip,#bq .rima-v50-category-row .tag.chip,#bbq .rima-v50-category-row .tag.chip').forEach(chip=>{
   const label=String(chip.textContent||'').trim().toLowerCase();
   const on=!favOpen&&!!selected&&label.startsWith(selected);
   chip.classList.toggle('on',on);chip.classList.toggle('active',on);
   chip.setAttribute('aria-pressed',String(on));
  });
 }
 function syncAll(){
  cleanFavoriteRows();syncPlayerHeart();syncCategories();
  if(typeof window.rimaV45SyncSelection==='function')window.rimaV45SyncSelection();
 }
 function settle(){
  requestAnimationFrame(syncAll);setTimeout(syncAll,45);setTimeout(syncAll,180);
 }
 function wrap(name){
  const old=window[name];
  if(typeof old!=='function'||old.__rimaV62)return;
  const wrapped=function(){
   const result=old.apply(this,arguments);
   settle();
   return result;
  };
  wrapped.__rimaV62=true;window[name]=wrapped;
 }
 ['zLP','zLS','zBarUI','pk','rimaV41StartFavorites','rimaV43ShowFavorites','rimaV29ToggleFav'].forEach(wrap);
 document.addEventListener('click',e=>{
  const chip=e.target&&e.target.closest?e.target.closest('#bp .rima-v50-category-row .tag.chip,#bq .rima-v50-category-row .tag.chip,#bbq .rima-v50-category-row .tag.chip'):null;
  if(chip)settle();
  const play=e.target&&e.target.closest?e.target.closest('#bp [data-v43-play],#bq [data-v43-play],#bbq [data-v43-play],#bp .bsl .bi .mc,#bq .bsl .bi .mc,#bbq .bsl .bi .mc'):null;
  if(play)settle();
  const heart=e.target&&e.target.closest?e.target.closest('#bp [data-v43-heart],#bq [data-v43-heart],#bbq [data-v43-heart],#pbar #rima-v29-player-heart'):null;
  if(heart)settle();
 },false);

 // The stage countdown can begin before the async beat analysis finishes.
 // Re-publish the already computed entry message whenever wStart runs.
 const oldWStart=window.wStart;
 if(typeof oldWStart==='function'&&!oldWStart.__rimaV62){
  const wrapped=function(){
   const result=oldWStart.apply(this,arguments);
   const msg=typeof ZS!=='undefined'&&ZS&&ZS.k==='syn'?'':(typeof ZS!=='undefined'&&ZS&&ZS.auto?'Beat sem introdução: já começa com tudo.':'Virada detectada. Entrando um pouco antes dela.');
   const line=document.getElementById('cs');
   if(line&&msg)line.textContent=msg;
   return result;
  };
  wrapped.__rimaV62=true;window.wStart=wrapped;
 }

 // Remember the exact setup scroll position before entering the stage, then
 // restore it after lvStop instead of unconditionally jumping to document top.
 const oldLvStart=window.lvStart;
 if(typeof oldLvStart==='function'&&!oldLvStart.__rimaV62){
  const wrapped=function(){
   if(!stageActive){
    const sc=document.scrollingElement;
    savedStageScroll=Number.isFinite(window.scrollY)?window.scrollY:(sc?sc.scrollTop:0);
    stageActive=true;
   }
   const result=oldLvStart.apply(this,arguments);
   requestAnimationFrame(()=>{fixStageList();requestAnimationFrame(fixStageList)});
   setTimeout(fixStageList,90);
   return result;
  };
  wrapped.__rimaV62=true;window.lvStart=wrapped;
 }
 const oldReturn=window.rimaReturnPreviousScreenToTop;
 if(typeof oldReturn==='function'&&!oldReturn.__rimaV62){
  const wrapped=function(){
   const y=savedStageScroll==null?0:savedStageScroll;
   const restore=()=>{
    try{window.scrollTo(0,y)}catch(_){}
    const sc=document.scrollingElement;if(sc)sc.scrollTop=y;
    if(document.documentElement)document.documentElement.scrollTop=y;
    if(document.body)document.body.scrollTop=y;
   };
   restore();requestAnimationFrame(()=>{restore();requestAnimationFrame(restore)});
   setTimeout(restore,90);setTimeout(restore,260);
   stageActive=false;savedStageScroll=null;
  };
  wrapped.__rimaV62=true;window.rimaReturnPreviousScreenToTop=wrapped;
 }

 function fixStageList(){
  const live=document.getElementById('lv');
  if(!live||live.hidden||document.body.classList.contains('rima-live-landscape'))return;
  const list=document.querySelector('#lv:not([hidden]) #bq>.bsl:not([hidden]),#lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden])');
  if(!list)return;
  list.style.setProperty('max-height','min(40vh,440px)','important');
  list.style.setProperty('min-height','min(28vh,300px)','important');
  list.style.setProperty('overflow-y','auto','important');
  list.style.setProperty('overflow-x','hidden','important');
 }
 window.addEventListener('resize',fixStageList,{passive:true});
 window.addEventListener('orientationchange',()=>setTimeout(fixStageList,80),{passive:true});
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',settle,{once:true});
 else settle();
 window.rimaV62Sync=syncAll;
})();</script>'''
css=r'''<style id="rimalab-favorites-player-scroll-stage-style-v62">
/* Exactly one centered heart glyph per control. The text node is removed by V62;
   the pseudo-element is the sole rendered icon in selector rows and player. */
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart,#bbq .rima-v43-fav-heart,
#bp .rima-v29-fav,#bq .rima-v29-fav,#bbq .rima-v29-fav,
#pbar #rima-v29-player-heart{
 position:relative!important;display:grid!important;place-items:center!important;
 box-sizing:border-box!important;padding:0!important;margin:0!important;
 font-size:0!important;line-height:0!important;text-align:center!important;
 transform:none!important;overflow:visible!important
}
#bp .rima-v43-fav-heart::before,#bq .rima-v43-fav-heart::before,#bbq .rima-v43-fav-heart::before,
#bp .rima-v29-fav::before,#bq .rima-v29-fav::before,#bbq .rima-v29-fav::before,
#pbar #rima-v29-player-heart::before{
 content:'♡'!important;position:absolute!important;inset:0!important;
 display:grid!important;place-items:center!important;margin:0!important;padding:0!important;
 width:100%!important;height:100%!important;box-sizing:border-box!important;
 font-family:Arial,sans-serif!important;font-size:20px!important;font-weight:900!important;
 line-height:1!important;letter-spacing:-1px!important;transform:none!important
}
#bp .rima-v43-fav-heart.on::before,#bq .rima-v43-fav-heart.on::before,#bbq .rima-v43-fav-heart.on::before,
#bp .rima-v29-fav.on::before,#bq .rima-v29-fav.on::before,#bbq .rima-v29-fav.on::before,
#bp .rima-v43-fav-heart[aria-pressed="true"]::before,#bq .rima-v43-fav-heart[aria-pressed="true"]::before,#bbq .rima-v43-fav-heart[aria-pressed="true"]::before,
#pbar #rima-v29-player-heart.on::before,#pbar #rima-v29-player-heart[aria-pressed="true"]::before{content:'♥'!important}
#pbar #rima-v29-player-heart{
 display:grid!important;place-items:center!important;flex:0 0 30px!important;
 width:30px!important;min-width:30px!important;max-width:30px!important;
 height:30px!important;min-height:30px!important;max-height:30px!important
}
#pbar #rima-v29-player-heart::before{font-size:20px!important}
#bp .rima-v60-heart-glyph,#bq .rima-v60-heart-glyph,#bbq .rima-v60-heart-glyph{
 display:inline-flex!important;align-items:center!important;justify-content:center!important;
 width:20px!important;height:20px!important;flex:0 0 20px!important;
 font-family:Arial,sans-serif!important;font-size:20px!important;line-height:20px!important;
 transform:none!important
}
/* Category controls regain a visible selected state after leaving Favorites. */
#bp .rima-v50-category-row>.tag.chip.on,#bq .rima-v50-category-row>.tag.chip.on,#bbq .rima-v50-category-row>.tag.chip.on,
#bp .rima-v50-category-row>.tag.chip.active,#bq .rima-v50-category-row>.tag.chip.active,#bbq .rima-v50-category-row>.tag.chip.active{
 background:var(--ac)!important;color:var(--on)!important;
 border-color:var(--ink)!important;box-shadow:3px 3px 0 var(--ink)!important
}
/* Portrait live selector: show complete beat cards in a taller, scrollable viewport. */
@media(orientation:portrait) and (max-width:760px){
 body.pl:not(.pv) #lv:not([hidden])>.card:not(.stage){
  max-height:min(50vh,760px)!important;min-height:0!important;overflow:visible!important
 }
 body.pl:not(.pv) #lv:not([hidden]) #bq>.bsl:not([hidden]),
 body.pl:not(.pv) #lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden]){
  display:block!important;box-sizing:border-box!important;
  max-height:min(40vh,440px)!important;min-height:min(28vh,300px)!important;
  height:auto!important;overflow-y:auto!important;overflow-x:hidden!important;
  overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important
 }
 body.pl:not(.pv) #lv:not([hidden]) #bq>.bsl:not([hidden])>.bi{
  box-sizing:border-box!important;min-height:96px!important;height:auto!important;
  overflow:visible!important;margin:0 0 7px!important
 }
 body.pl:not(.pv) #lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden])>.rima-v43-fav-row{
  box-sizing:border-box!important;min-height:88px!important;height:auto!important;
  overflow:visible!important;margin:0 0 7px!important
 }
}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V62_FAIL: </body> ausente')
h=h[:pos]+css+'\n'+runtime+'\n'+h[pos:]

m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='81': raise SystemExit('V62_FAIL: versionCode base não é 81')
g=g[:m.start(1)]+'82'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.3.9': raise SystemExit('V62_FAIL: versionName base não é 3.3.9')
g=g[:m.start(1)]+'3.4.0'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V62_OK: remove duplicate Favorites decorator, sync player heart and category states, preserve stage return scroll, restore entry message, expand portrait stage list; 3.4.0/code82')
