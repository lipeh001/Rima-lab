#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V45_FAIL: missing app assets or Gradle')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-selection-feedback-runtime-v45' in h: raise SystemExit('V45_FAIL: already applied')
if 'rimalab-favorites-layout-runtime-v43' not in h or 'rimalab-favorites-catalog-lexical-v44' not in h:
    raise SystemExit('V45_FAIL: expected V43/V44 runtimes missing')
pattern=r' function renderRoot\(root\)\{[\s\S]*?\n \}\n function render\(\)'
replacement=r''' function renderRoot(root){
  const bar=ensureToolbar(root);removeView(root);
  root.querySelectorAll(':scope > .bsl:not(.rima-v43-favlist)').forEach(e=>{e.hidden=showing});
  root.querySelectorAll(':scope > .catalog-attribution').forEach(e=>{e.hidden=showing});
  root.querySelectorAll(':scope > .row').forEach(row=>{
   if(!row.querySelector('.tag.chip'))return;
   row.hidden=showing;
   if(showing)row.querySelectorAll('.tag.chip').forEach(b=>{b.classList.remove('on');b.setAttribute('aria-pressed','false')});
  });
  if(showing)bar.insertAdjacentHTML('afterend',favoriteMarkup());
 }
 function render()'''
h2,n=re.subn(pattern,replacement,h,count=1)
if n!=1: raise SystemExit('V45_FAIL: could not replace shared Favorites renderer')
h=h2
css=r'''<style id="rimalab-selection-feedback-v45">
#bp .bsl .bi>.beat-info>.mc.on,#bq .bsl .bi>.beat-info>.mc.on,#bp .bsl .bi .mc.on,#bq .bsl .bi .mc.on{
 background:linear-gradient(105deg,rgba(229,196,91,.34),rgba(229,196,91,.14))!important;
 background-color:rgba(229,196,91,.22)!important;border:1px solid rgba(239,207,106,.98)!important;
 border-left:4px solid #e5c45b!important;color:#fff1b5!important;
 box-shadow:inset 0 0 0 1px rgba(255,235,170,.10),0 0 0 1px rgba(229,196,91,.22),0 7px 20px rgba(229,196,91,.14)!important;
}
#bp .bsl .bi .mc.on b,#bq .bsl .bi .mc.on b{color:#ffe39a!important}
#bp .bsl .bi .mc.on small,#bq .bsl .bi .mc.on small{color:#e7d9ad!important;opacity:1!important}
#bp .rima-v43-fav-row.is-selected,#bq .rima-v43-fav-row.is-selected{
 border:1px solid rgba(239,207,106,.95)!important;background:linear-gradient(105deg,rgba(229,196,91,.20),rgba(229,196,91,.07))!important;
 box-shadow:inset 3px 0 0 #e5c45b,0 0 0 1px rgba(229,196,91,.15)!important;
}
#bp .rima-v43-fav-play.is-selected,#bq .rima-v43-fav-play.is-selected{
 background:linear-gradient(105deg,rgba(229,196,91,.30),rgba(229,196,91,.12))!important;
 border-color:rgba(239,207,106,.95)!important;color:#fff1b5!important;
}
#bp .rima-v43-fav-play.is-selected b,#bq .rima-v43-fav-play.is-selected b{color:#ffe39a!important}
#bp .bsl .bi .mc[aria-pressed="true"],#bq .bsl .bi .mc[aria-pressed="true"]{outline:1px solid rgba(239,207,106,.35)!important;outline-offset:1px!important}
#bp .rima-v43-fav-row,#bq .rima-v43-fav-row{transition:background .16s,border-color .16s,box-shadow .16s!important}
</style>'''
runtime=r'''<script id="rimalab-selection-feedback-runtime-v45">
(function(){
 'use strict';
 const catalog=()=>typeof ZLIB!=='undefined'&&ZLIB?ZLIB:(window.ZLIB||{});
 const keyOf=x=>x&&x[4]!=null?'jm-'+String(x[4]):'';
 const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function syncSelection(){
  const key=String(typeof ZS!=='undefined'&&ZS&&ZS.k==='lib'&&ZS.key?ZS.key:'');
  document.querySelectorAll('#bp .bsl .bi .mc[data-rima-track-key],#bq .bsl .bi .mc[data-rima-track-key]').forEach(b=>{
   const selected=!!key&&b.getAttribute('data-rima-track-key')===key;
   b.classList.toggle('on',selected);b.setAttribute('aria-pressed',String(selected));
  });
  document.querySelectorAll('#bp .rima-v43-fav-row,#bq .rima-v43-fav-row').forEach(row=>{
   const selected=!!key&&row.getAttribute('data-key')===key;
   row.classList.toggle('is-selected',selected);
   const b=row.querySelector('.rima-v43-fav-play');
   if(b){b.classList.toggle('is-selected',selected);if(selected)b.setAttribute('aria-current','true');else b.removeAttribute('aria-current')}
  });
 }
 const oldPick=window.zBpick;
 if(typeof oldPick==='function'&&!oldPick.__rimaV45){
  const wrapped=function(){
   let out=oldPick.apply(this,arguments);
   out=out.replace(/<button class="mc([^"]*)" onclick="zLP\((\d+),0,'([^']+)'\)">/g,(full,classes,index,category)=>{
    const list=catalog()[category]&&catalog()[category][1]||[],item=list[Number(index)],key=keyOf(item);
    return '<button class="mc'+classes+'" data-rima-track-key="'+esc(key)+'" aria-pressed="'+String(!!key&&typeof ZS!=='undefined'&&ZS.k==='lib'&&ZS.key===key)+'" onclick="zLP('+index+',0,\''+category+'\')">';
   });
   return out;
  };
  wrapped.__rimaV45=true;window.zBpick=wrapped;
 }
 function wrap(name){
  const old=window[name];if(typeof old!=='function'||old.__rimaV45)return;
  const wrapped=function(){const result=old.apply(this,arguments);requestAnimationFrame(syncSelection);setTimeout(syncSelection,50);return result};
  wrapped.__rimaV45=true;window[name]=wrapped;
 }
 wrap('zLP');wrap('pk');wrap('zBarUI');wrap('rimaV43ShowFavorites');
 document.addEventListener('click',e=>{
  const target=e.target&&e.target.closest?e.target.closest('#bp .bsl .bi .mc,#bq .bsl .bi .mc,#bp [data-v43-play],#bq [data-v43-play]'):null;
  if(target){requestAnimationFrame(syncSelection);setTimeout(syncSelection,60)}
 },true);
 document.addEventListener('click',e=>{
  const heart=e.target&&e.target.closest?e.target.closest('#bp [data-rima-fav],#bp [data-v43-heart],#bq [data-rima-fav],#bq [data-v43-heart],#rima-v29-player-heart'):null;
  if(heart)setTimeout(syncSelection,40);
 },true);
 window.addEventListener('storage',syncSelection);
 function ready(){syncSelection();setTimeout(syncSelection,150)}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
 window.rimaV45SyncSelection=syncSelection;
})();
</script>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V45_FAIL: body close missing')
h=h[:pos]+css+'\n'+runtime+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='64': raise SystemExit('V45_FAIL: expected versionCode 64')
g=g[:m.start()]+re.sub('64','65',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.2.2': raise SystemExit('V45_FAIL: expected versionName 3.2.2')
g=g[:m.start()]+m.group(0).replace('3.2.2','3.2.3')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V45_OK: visible selection, stable track IDs, selected Favorites state, exclusive Favorites view in #bp/#bq; 3.2.3/code65')
