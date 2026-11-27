#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V45_FAIL: missing app assets or Gradle')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-selection-feedback-runtime-v45' in h: raise SystemExit('V45_FAIL: already applied')
if 'rimalab-landscape-stage-reflow-v46' in h: raise SystemExit('V46_FAIL: already applied')
if 'rimalab-favorites-layout-runtime-v43' not in h or 'rimalab-favorites-catalog-lexical-v44' not in h:
    raise SystemExit('V45_FAIL: expected V43/V44 runtimes missing')
replacement=r'''function renderRoot(root){
  const id=root.id,bar=ensureToolbar(root);removeView(root);
  if(id==='bp'){
   root.querySelectorAll(':scope > .bsl').forEach(e=>{if(!e.classList.contains('rima-v43-favlist'))e.hidden=showing});
   root.querySelectorAll(':scope > .catalog-attribution').forEach(e=>e.hidden=showing);
   root.querySelectorAll('.row .tag.chip').forEach(b=>{if(showing){b.classList.remove('on');b.setAttribute('aria-pressed','false')}});
   if(showing)bar.insertAdjacentHTML('afterend',favoriteMarkup());
  }else{
   // Keep stage category chips live; only swap the beat catalog content.
   if(showing){
    root.querySelectorAll('.row .tag.chip').forEach(b=>{b.classList.remove('on');b.setAttribute('aria-pressed','false')});
    root.querySelectorAll('.bsl').forEach(e=>{if(!e.classList.contains('rima-v43-favlist'))e.hidden=true});
    bar.insertAdjacentHTML('afterend',favoriteMarkup());
   }else root.querySelectorAll('.bsl').forEach(e=>{if(!e.classList.contains('rima-v43-favlist'))e.hidden=false});
  }
 }'''
v43_start=h.find('<script id="rimalab-favorites-layout-runtime-v43">')
if v43_start<0: raise SystemExit('V45_FAIL: V43 script opening tag missing')
v43_body=v43_start+len('<script id="rimalab-favorites-layout-runtime-v43">')
v43_end=h.find('</script>',v43_body)
if v43_end<0: raise SystemExit('V45_FAIL: V43 script closing tag missing')
v43_js=h[v43_body:v43_end]
# Category chips in either selector close Favorites and switch to that category.
old_chip="const chip=e.target&&e.target.closest?e.target.closest('#bp .row .tag.chip'):null;\n  if(chip&&showing)setMode(false,'bp');"
new_chip="const chip=e.target&&e.target.closest?e.target.closest('#bp .row .tag.chip,#bq .row .tag.chip'):null;\n  if(chip&&showing)setMode(false,chip.closest('#bp,#bq').id);"
if old_chip not in v43_js: raise SystemExit('V46_FAIL: stage category click handler not found')
v43_js=v43_js.replace(old_chip,new_chip,1)
start=v43_js.find('function renderRoot(root){')
end=v43_js.find('\n function render(){',start)
if start<0 or end<0: raise SystemExit('V45_FAIL: renderer function not found inside V43 script')
v43_js2=v43_js[:start]+replacement.rstrip('\n')+v43_js[end:]
h=h[:v43_body]+v43_js2+h[v43_end:]
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
/* Make all heart glyphs visibly heavier without changing tap targets. */
#bp .rima-v43-toggle,#bq .rima-v43-toggle,
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart,
#rima-v29-player-heart,.rima-v29-fav{
 font-weight:900!important;-webkit-text-stroke:.9px currentColor!important;
 text-shadow:0 0 .35px currentColor!important;
}
#bp .rima-v43-toggle,#bq .rima-v43-toggle{font-size:15px!important}
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart,#rima-v29-player-heart,.rima-v29-fav{font-size:20px!important}
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
landscape=r'''<style id="rimalab-landscape-stage-reflow-v46">
#bp .rima-v43-toggle,#bq .rima-v43-toggle{font-weight:500!important}
#bp .rima-v43-toggle .rima-v29-count,#bq .rima-v43-toggle .rima-v29-count{font-weight:850!important}
@media (orientation:landscape) and (min-width:600px){
 main{box-sizing:border-box!important;width:100%!important;max-width:none!important}
 #lv:not([hidden]){display:grid!important;box-sizing:border-box!important;width:100%!important;height:calc(100svh - 215px)!important;min-height:340px!important;max-height:none!important;grid-template-columns:minmax(0,1.42fr) minmax(0,1fr)!important;grid-template-rows:42px minmax(0,1fr) 42px!important;align-items:stretch!important;gap:7px 10px!important;margin:0!important;padding:0 0 3px!important;overflow:visible!important}
 #lv:not([hidden])>.bk{grid-column:2!important;grid-row:1!important;align-self:stretch!important;width:100%!important;height:42px!important;min-height:42px!important;margin:0!important}
 #lv:not([hidden])>#stg.stage{grid-column:1!important;grid-row:1/4!important;align-self:stretch!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;box-sizing:border-box!important;width:100%!important;height:100%!important;min-height:0!important;max-height:none!important;margin:0!important;overflow:hidden!important;padding:clamp(8px,1.3vh,13px) clamp(9px,1vw,16px)!important}
 #lv:not([hidden])>#stg.stage #ck{flex:0 0 auto!important;margin:0 0 4px!important}
 #lv:not([hidden])>#stg.stage #cb{flex:0 0 auto!important;box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-height:clamp(74px,14vh,112px)!important;height:auto!important;margin:0 auto 4px!important;white-space:normal!important;overflow-wrap:anywhere!important}
 #lv:not([hidden])>#stg.stage #rm{flex:0 0 auto!important;position:relative!important;inset:auto!important;display:flex!important;flex-wrap:wrap!important;justify-content:center!important;align-items:center!important;width:100%!important;height:auto!important;min-height:0!important;margin:4px auto 6px!important;padding:0 3px!important;transform:none!important;gap:5px!important}
 #lv:not([hidden])>#stg.stage #rm>*{max-width:48%!important;min-width:0!important;white-space:normal!important}
 #lv:not([hidden])>#stg.stage #sg{flex:0 0 auto!important;margin:4px 0!important}
 #lv:not([hidden])>#stg.stage #cs,#lv:not([hidden])>#stg.stage #cn{flex:0 0 auto!important;max-width:100%!important;margin:5px auto 0!important;line-height:1.2!important}
 #lv:not([hidden])>#stg.stage .v3bar{flex:0 0 auto!important;margin:8px auto 0!important}
 #lv:not([hidden])>.card:not(.stage){grid-column:2!important;grid-row:2!important;align-self:stretch!important;box-sizing:border-box!important;width:100%!important;height:100%!important;min-width:0!important;min-height:0!important;max-height:none!important;margin:0!important;padding:9px 10px!important;overflow-x:hidden!important;overflow-y:auto!important;overscroll-behavior:contain!important}
 #lv:not([hidden]) #bq{box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;margin:0!important}
 #lv:not([hidden]) #bq .bsl{max-width:100%!important;min-width:0!important}
 #lv:not([hidden])>.btn.w{grid-column:2!important;grid-row:3!important;align-self:stretch!important;width:100%!important;height:42px!important;min-height:42px!important;margin:0!important}
}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V46_FAIL: body close missing')
h=h[:pos]+landscape+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='64': raise SystemExit('V46_FAIL: expected versionCode 64')
g=g[:m.start()]+re.sub('64','67',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.2.2': raise SystemExit('V46_FAIL: expected versionName 3.2.2')
g=g[:m.start()]+m.group(0).replace('3.2.2','3.2.5')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V46_OK: stage category chips remain clickable from Favorites, selected beat feedback retained, bolder hearts; 3.2.5/code67')
