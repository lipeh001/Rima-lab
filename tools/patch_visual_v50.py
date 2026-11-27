#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V50_FAIL: missing HTML or Gradle')
h=hp.read_text(encoding='utf-8')
g=gp.read_text(encoding='utf-8')
if 'rimalab-final-layout-scroll-v50' in h: raise SystemExit('V50_FAIL: already applied')
if 'rimalab-shared-selector-orientation-runtime-v49' not in h or 'rimalab-favorites-layout-runtime-v43' not in h:
    raise SystemExit('V50_FAIL: expected V43/V49 runtimes missing')

# The landscape dock uses the same #pbar element. Add breathing room for its
# time label and seek controls without creating a second player.
player_script=re.search(r'<script id="rimalab-selector-favorites-sync-v42">(.*?)</script>',h,re.S)
if not player_script: raise SystemExit('V50_FAIL: V42 player dock runtime missing')
player_js=player_script.group(1)
old_h="set('height','70px');set('min-height','70px');set('max-height','70px');"
new_h="const dockHeight=window.innerHeight<420?70:84;set('height',dockHeight+'px');set('min-height',dockHeight+'px');set('max-height',dockHeight+'px');"
if old_h not in player_js: raise SystemExit('V50_FAIL: V42 player height assignment missing')
player_js=player_js.replace(old_h,new_h,1)
h=h[:player_script.start(1)]+player_js+h[player_script.end(1):]

# Update the V42 landscape player geometry: the time label moves below the
# control row, and the seek controls receive a separate row beneath it.
style_pat=re.compile(r'(<style id="rimalab-landscape-player-dock-v42">)(.*?)(</style>)',re.S)
m=style_pat.search(h)
if not m: raise SystemExit('V50_FAIL: V42 player CSS missing')
css=m.group(2)
repls=[
 ("height:70px!important;min-height:70px!important;max-height:70px!important","height:84px!important;min-height:84px!important;max-height:84px!important"),
 ("top:29px!important;bottom:auto!important;height:9px!important;min-height:9px!important","top:40px!important;bottom:auto!important;height:9px!important;min-height:9px!important"),
 ("flex:0 0 25px!important;align-items:center!important;gap:7px!important;width:100%!important;height:25px!important;min-height:25px!important;margin:0!important;padding:0 1px!important",
  "flex:0 0 24px!important;align-items:center!important;gap:7px!important;width:100%!important;height:24px!important;min-height:24px!important;margin:9px 0 0!important;padding:0 1px!important")
]
for a,b in repls:
    if a not in css: raise SystemExit('V50_FAIL: V42 player geometry fragment missing: '+a[:55])
    css=css.replace(a,b,1)
h=h[:m.start(2)]+css+h[m.end(2):]

# Update Favorites behavior and rendering in the single shared V43 runtime.
open_tag='<script id="rimalab-favorites-layout-runtime-v43">'
a=h.find(open_tag)
if a<0: raise SystemExit('V50_FAIL: V43 runtime opening tag missing')
body=a+len(open_tag); z=h.find('</script>',body)
if z<0: raise SystemExit('V50_FAIL: V43 runtime closing tag missing')
js=h[body:z]

# Add a stable category-row class for the landscape layout.
old_row="if(categoryRow){if(categoryRow.nextElementSibling!==bar)categoryRow.insertAdjacentElement('afterend',bar)}"
new_row="if(categoryRow){categoryRow.classList.add('rima-v50-category-row');if(categoryRow.nextElementSibling!==bar)categoryRow.insertAdjacentElement('afterend',bar)}"
if old_row not in js: raise SystemExit('V50_FAIL: category row placement missing')
js=js.replace(old_row,new_row,1)

# Put the heart first and the download control second, matching the regular
# Boom bap / Trap / Drill cards.
old_order="""+'</div>'+favoriteDownloadMarkup(t)+'<button class="rima-v43-fav-heart" type="button" data-v43-heart="'+esc(t.key)+'" aria-label="Remover dos favoritos" aria-pressed="true">♥</button></div>'"""
new_order="""+'</div><button class="rima-v43-fav-heart" type="button" data-v43-heart="'+esc(t.key)+'" aria-label="Remover dos favoritos" aria-pressed="true">♥</button>'+favoriteDownloadMarkup(t)+'</div>'"""
if old_order not in js: raise SystemExit('V50_FAIL: Favorites action order fragment missing')
js=js.replace(old_order,new_order,1)

# Keep Favorites selected when tapped again. Switching out is done with a
# category chip, just as tapping an already-selected category never deselects it.
old_toggle="""  const root=b.closest('#bp,#bq').id;
  if(showing){
   setMode(false,root);
   if(typeof window.zLS==='function')window.zLS('Boom bap');
   else if(typeof ZS!=='undefined')ZS.s='Boom bap';
   render();
  }else setMode(true,root);"""
new_toggle="""  const root=b.closest('#bp,#bq').id;
  if(showing){activeRoot=root;return}
  setMode(true,root);"""
if old_toggle not in js: raise SystemExit('V50_FAIL: Favorites toggle handler fragment missing')
js=js.replace(old_toggle,new_toggle,1)

# Save the vertical page/list position before the playback path rebuilds #bp/#bq.
# The same snapshot is used by renderRoot after the list DOM is recreated.
insert_after=" let showing=false,activeRoot='bp',busy=false;"
if insert_after not in js: raise SystemExit('V50_FAIL: Favorites runtime state declaration missing')
scroll_code=r"""
 const scrollSnapshots=window.__rimaV50FavoritesScroll||(window.__rimaV50FavoritesScroll={});
 function captureFavoriteScroll(root){
  if(!root)return null;
  const view=root.querySelector(':scope > .rima-v43-favlist');
  const parents=[];
  for(let p=root.parentElement;p&&p!==document.documentElement;p=p.parentElement){
   if(p.scrollTop>0||p.scrollHeight>p.clientHeight+2)parents.push({el:p,top:p.scrollTop});
  }
  const state={listTop:view?view.scrollTop:(scrollSnapshots[root.id]?.listTop||0),pageY:window.scrollY||document.scrollingElement.scrollTop||0,parents};
  scrollSnapshots[root.id]=state;
  return state;
 }
 function restoreFavoriteScroll(root,state){
  if(!root||!state)return;
  const restore=()=>{
   const view=root.querySelector(':scope > .rima-v43-favlist');
   if(view&&Math.abs(view.scrollTop-state.listTop)>1)view.scrollTop=state.listTop;
   (state.parents||[]).forEach(p=>{if(p.el&&Math.abs(p.el.scrollTop-p.top)>1)p.el.scrollTop=p.top});
   const current=window.scrollY||document.scrollingElement.scrollTop||0;
   if(Math.abs(current-state.pageY)>2)window.scrollTo(0,state.pageY);
  };
  requestAnimationFrame(()=>{restore();requestAnimationFrame(restore)});
  setTimeout(restore,60);setTimeout(restore,180);setTimeout(restore,380);setTimeout(restore,650);
 }
"""
js=js.replace(insert_after,insert_after+scroll_code,1)

# Capture state in renderRoot before it removes the Favorites view. If pk() has
# already replaced the root's innerHTML, play() has placed the snapshot above.
old_render=""" function renderRoot(root){
  const bar=ensureToolbar(root);
  removeView(root);"""
new_render=""" function renderRoot(root){
  const bar=ensureToolbar(root);
  const priorView=root.querySelector(':scope > .rima-v43-favlist');
  const savedScroll=priorView?captureFavoriteScroll(root):(scrollSnapshots[root.id]||null);
  removeView(root);"""
if old_render not in js: raise SystemExit('V50_FAIL: renderRoot beginning missing')
js=js.replace(old_render,new_render,1)
old_insert="""  if(showing)bar.insertAdjacentHTML('afterend',favoriteMarkup());
 }"""
new_insert="""  if(showing){
   const wrap=document.createElement('div');wrap.innerHTML=favoriteMarkup();
   const view=wrap.firstElementChild;
   if(view){
    bar.insertAdjacentElement('afterend',view);
    if(savedScroll)restoreFavoriteScroll(root,savedScroll);
   }
  }
 }"""
if old_insert not in js: raise SystemExit('V50_FAIL: renderRoot favorite insertion missing')
js=js.replace(old_insert,new_insert,1)

# Playback stores the exact scroll position before the underlying pk()/zLP()
# path causes a full catalog rebuild.
old_play=""" function play(k){
  const key=String(k||'');if(!allTracks().some(t=>t.key===key))return;
  const start=window.rimaV41StartFavorites||window.rimaV29PlayFav;
  if(typeof start==='function')start(key);
  else {const t=allTracks().find(t=>t.key===key);if(t&&typeof window.zLP==='function')window.zLP(t.i,0,t.cat)}
 }"""
new_play=""" function play(k){
  const key=String(k||'');if(!allTracks().some(t=>t.key===key))return;
  const root=document.getElementById(activeRoot)||document.getElementById('bp');
  const state=captureFavoriteScroll(root);
  const start=window.rimaV41StartFavorites||window.rimaV29PlayFav;
  if(typeof start==='function')start(key);
  else {const t=allTracks().find(t=>t.key===key);if(t&&typeof window.zLP==='function')window.zLP(t.i,0,t.cat)}
  restoreFavoriteScroll(root,state);
  setTimeout(()=>{if(scrollSnapshots[activeRoot]===state)delete scrollSnapshots[activeRoot]},1000);
 }"""
if old_play not in js: raise SystemExit('V50_FAIL: Favorites playback function missing')
js=js.replace(old_play,new_play,1)

h=h[:body]+js+h[z:]

# Extend V49 orientation runtime so the html root receives the lock class too.
v49_open='<script id="rimalab-shared-selector-orientation-runtime-v49">'
va=h.find(v49_open)
if va<0: raise SystemExit('V50_FAIL: V49 orientation runtime missing')
vb=va+len(v49_open); vz=h.find('</script>',vb)
vjs=h[vb:vz]
old_class="body.classList.toggle('rima-live-landscape',active);"
new_class="body.classList.toggle('rima-live-landscape',active);document.documentElement.classList.toggle('rima-live-landscape',active);"
if old_class not in vjs: raise SystemExit('V50_FAIL: V49 body orientation class missing')
vjs=vjs.replace(old_class,new_class,1)
h=h[:vb]+vjs+h[vz:]

css=r"""<style id="rimalab-final-layout-scroll-v50">
/* Never allow horizontal page drift; vertical page/list scrolling remains enabled. */
html,body{max-width:100vw!important;overflow-x:hidden!important;overscroll-behavior-x:none!important}
main,.tab,#bp,#bq{min-width:0!important;max-width:100%!important;box-sizing:border-box!important}
#bp,#bq{overflow-x:hidden!important;touch-action:pan-y!important}
#bp>.rima-v43-favlist,#bq>.rima-v43-favlist{touch-action:pan-y!important;overscroll-behavior-x:none!important}
#bp>.rima-v43-favlist .rima-v43-fav-row,#bq>.rima-v43-favlist .rima-v43-fav-row{
 grid-template-columns:minmax(0,1fr) 44px 42px!important;
 gap:8px!important;min-width:0!important;
}
#bp .rima-v43-fav-row>.rima-v43-fav-heart,#bq .rima-v43-fav-row>.rima-v43-fav-heart{grid-column:2!important;grid-row:1!important}
#bp .rima-v43-fav-row>.rima-v47-fav-download,#bq .rima-v43-fav-row>.rima-v47-fav-download{grid-column:3!important;grid-row:1!important}
@media(max-width:380px){
 #bp>.rima-v43-favlist .rima-v43-fav-row,#bq>.rima-v43-favlist .rima-v43-fav-row{grid-template-columns:minmax(0,1fr) 40px 40px!important;gap:6px!important}
 #bp .rima-v43-fav-row>.rima-v43-fav-heart,#bq .rima-v43-fav-row>.rima-v43-fav-heart{width:40px!important;min-width:40px!important;height:40px!important;min-height:40px!important}
}
/* The setup catalog should extend the page vertically instead of capping the list. */
@media(orientation:portrait) and (max-width:700px){
 #train-step-2 #bp>.bsl,#train-step-2 #bp>.rima-v43-favlist{
  max-height:none!important;height:auto!important;overflow:visible!important;
  overflow-x:hidden!important;overscroll-behavior:initial!important;
 }
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage{
  justify-content:center!important;
  padding-top:clamp(20px,4vh,38px)!important;padding-bottom:clamp(20px,4vh,38px)!important;
 }
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage #cb{
  display:flex!important;flex:1 1 auto!important;align-items:center!important;justify-content:center!important;
  min-height:clamp(110px,18svh,165px)!important;height:auto!important;
  margin:5px auto 8px!important;padding:6px 4px!important;
 }
}
/* In landscape, keep category chips and Favorites visible; only the beat list scrolls. */
@media(orientation:landscape) and (min-width:560px){
 html.rima-live-landscape,body.rima-live-landscape{
  width:100vw!important;max-width:100vw!important;height:100vh!important;max-height:100vh!important;
  overflow:hidden!important;overflow-x:hidden!important;overscroll-behavior:none!important;touch-action:pan-y!important;
 }
 body.rima-live-landscape main{
  position:fixed!important;inset:0!important;width:100vw!important;max-width:100vw!important;
  height:100vh!important;max-height:100vh!important;overflow:hidden!important;overflow-x:hidden!important;
  overscroll-behavior:none!important;touch-action:pan-y!important;
 }
 body.rima-live-landscape #lv:not([hidden]){
  left:0!important;right:0!important;top:0!important;bottom:0!important;
  width:100vw!important;max-width:100vw!important;height:100vh!important;max-height:100vh!important;
  overflow:hidden!important;overflow-x:hidden!important;overscroll-behavior:none!important;touch-action:pan-y!important;
 }
 body.rima-live-landscape #lv:not([hidden])>.card:not(.stage){
  display:flex!important;flex-direction:column!important;min-width:0!important;min-height:0!important;
  width:100%!important;max-width:100%!important;height:100%!important;max-height:100%!important;
  overflow:hidden!important;overflow-x:hidden!important;overscroll-behavior:none!important;
 }
 body.rima-live-landscape #lv:not([hidden])>.card:not(.stage)>.row.nw,
 body.rima-live-landscape #lv:not([hidden])>.card:not(.stage)>p.mut{flex:0 0 auto!important}
 body.rima-live-landscape #lv:not([hidden]) #bq{
  display:flex!important;flex:1 1 auto!important;flex-direction:column!important;
  min-width:0!important;min-height:0!important;width:100%!important;max-width:100%!important;
  height:100%!important;max-height:100%!important;overflow:hidden!important;overflow-x:hidden!important;
 }
 body.rima-live-landscape #bq>.rima-v50-category-row{
  display:flex!important;flex:0 0 auto!important;flex-wrap:nowrap!important;align-items:stretch!important;
  width:100%!important;max-width:100%!important;min-width:0!important;box-sizing:border-box!important;
  gap:5px!important;margin:5px 0 6px!important;padding:0!important;overflow:visible!important;
 }
 body.rima-live-landscape #bq>.rima-v50-category-row>.tag.chip{
  display:flex!important;flex:1 1 0!important;min-width:0!important;max-width:none!important;
  align-items:center!important;justify-content:center!important;box-sizing:border-box!important;
  padding:8px 2px!important;margin:0!important;font-size:clamp(9px,1vw,12px)!important;
  line-height:1.1!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;
 }
 body.rima-live-landscape #bq>.rima-v43-tools{
  display:flex!important;flex:0 0 auto!important;position:relative!important;float:none!important;clear:both!important;
  width:100%!important;max-width:100%!important;min-width:0!important;margin:2px 0 6px!important;
 }
 body.rima-live-landscape #bq>.rima-v43-tools button{width:100%!important;max-width:100%!important;min-height:40px!important}
 body.rima-live-landscape #bq>.bsl,
 body.rima-live-landscape #bq>.rima-v43-favlist{
  display:block!important;flex:1 1 auto!important;min-width:0!important;min-height:0!important;
  height:auto!important;max-height:none!important;width:100%!important;max-width:100%!important;
  overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;
  -webkit-overflow-scrolling:touch!important;touch-action:pan-y!important;
 }
 body.rima-live-landscape #bq>.catalog-attribution{flex:0 0 auto!important;margin:4px 0 0!important}
 body.rima-live-landscape #bq>.rima-v43-favlist .rima-v43-fav-row{
  grid-template-columns:minmax(0,1fr) 44px 42px!important;
 }
 /* One existing player, taller only while landscape: time and seek row no longer overlap. */
 body.pl #pbar{
  height:84px!important;min-height:84px!important;max-height:84px!important;
  padding:4px 8px 3px!important;box-sizing:border-box!important;
 }
 body.pl #pbar .pwrow{flex:0 0 36px!important;height:36px!important;min-height:36px!important}
 body.pl #pbar .pwinfo{
  display:flex!important;position:absolute!important;right:10px!important;top:40px!important;bottom:auto!important;
  height:9px!important;min-height:9px!important;margin:0!important;font-size:8px!important;
 }
 body.pl #pbar .pwscr{
  display:flex!important;position:relative!important;inset:auto!important;flex:0 0 24px!important;
  height:24px!important;min-height:24px!important;width:100%!important;margin:9px 0 0!important;
  padding:0 1px!important;gap:7px!important;z-index:10!important;
 }
}
@media(orientation:landscape) and (max-height:420px) and (min-width:560px){
 body.pl #pbar{height:70px!important;min-height:70px!important;max-height:70px!important;padding:3px 7px 2px!important}
 body.pl #pbar .pwrow{flex-basis:32px!important;height:32px!important;min-height:32px!important}
 body.pl #pbar .pwinfo{top:35px!important}
 body.pl #pbar .pwscr{flex-basis:22px!important;height:22px!important;min-height:22px!important;margin-top:7px!important}
}
</style>
<script id="rimalab-final-layout-scroll-runtime-v50">
(function(){
 'use strict';
 const body=document.body,html=document.documentElement;
 const lv=document.getElementById('lv');
 function landscape(){return !!(window.matchMedia&&window.matchMedia('(orientation:landscape) and (min-width:560px)').matches)}
 function sync(){
  const active=landscape()&&!!(lv&&!lv.hidden)&&body.classList.contains('pl')&&!body.classList.contains('pv');
  body.classList.toggle('rima-live-landscape',active);
  html.classList.toggle('rima-live-landscape',active);
  if(active){body.scrollLeft=0;html.scrollLeft=0}
 }
 function settle(){requestAnimationFrame(sync);setTimeout(sync,120);setTimeout(sync,320)}
 // Category chips are the single explicit way to leave Favorites in both selectors.
 // V43 originally wired only #bp; #bq now uses the same close action.
 document.addEventListener('click',function(e){
  const chip=e.target&&e.target.closest?e.target.closest('#bp .row .tag.chip,#bq .row .tag.chip'):null;
  if(!chip)return;
  const root=chip.closest('#bp,#bq');
  if(root&&root.querySelector(':scope > .rima-v43-favlist')&&typeof window.rimaV43ShowFavorites==='function'){
   window.rimaV43ShowFavorites(false);
  }
 },true);
 if(lv&&window.MutationObserver)new MutationObserver(settle).observe(lv,{attributes:true,attributeFilter:['hidden']});
 window.addEventListener('resize',settle,{passive:true});
 window.addEventListener('orientationchange',settle,{passive:true});
 if(window.visualViewport)window.visualViewport.addEventListener('resize',settle,{passive:true});
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)settle()});
 settle();
 window.rimaV50SyncLayout=sync;
})();
</script>"""
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V50_FAIL: </body> missing')
h=h[:pos]+css+'\n'+h[pos:]

m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='70': raise SystemExit('V50_FAIL: expected base versionCode 70')
g=g[:m.start()]+re.sub('70','71',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.2.8': raise SystemExit('V50_FAIL: expected base versionName 3.2.8')
g=g[:m.start()]+m.group(0).replace('3.2.8','3.2.9')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V50_OK: preserve Favorites list/page scroll when a saved beat is played; Favorites remains selected until a category is chosen; heart then download order; center portrait stage word; vertical-only page scrolling; pinned landscape categories/Favorites with scrollable list; 84px single horizontal player with separated time/seek rows; 3.2.9/code71')
