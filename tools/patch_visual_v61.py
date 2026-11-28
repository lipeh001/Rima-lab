#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V61_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-favorites-stable-render-v61' in h: raise SystemExit('V61_FAIL: patch já aplicado')
if 'rimalab-consistent-heart-favorites-v60' not in h or 'rimalab-favorites-layout-runtime-v43' not in h:
 raise SystemExit('V61_FAIL: base 3.3.8/V43/V60 ausente')

# V40 is an obsolete renderer. Once V43 owns Favorites, it must not rebuild
# or overwrite the same selector after player updates, resize or visibility changes.
old_v40="function scheduleRender(){if(renderQueued)return;renderQueued=true;requestAnimationFrame(()=>{renderQueued=false;wireTools();bindPlayer();if(favoritesMode)renderFavorites();else sync()})}"
new_v40="function scheduleRender(){if(typeof window.rimaV43ShowFavorites==='function')return;if(renderQueued)return;renderQueued=true;requestAnimationFrame(()=>{renderQueued=false;wireTools();bindPlayer();if(favoritesMode)renderFavorites();else sync()})}"
if h.count(old_v40)!=1: raise SystemExit('V61_FAIL: scheduleRender V40 não corresponde')
h=h.replace(old_v40,new_v40,1)

# V42 must stop publishing its stale Favorites view after V43 has taken ownership.
old_v42pk="const f=function(){const result=oldPk.apply(this,arguments);renderAll();setTimeout(renderAll,60);return result};"
new_v42pk="const f=function(){const result=oldPk.apply(this,arguments);if(typeof window.rimaV43ShowFavorites!=='function'){renderAll();setTimeout(renderAll,60)}return result};"
if h.count(old_v42pk)!=1: raise SystemExit('V61_FAIL: wrapper pk V42 não corresponde')
h=h.replace(old_v42pk,new_v42pk,1)
old_v42toggle="const wrapped=function(){const result=oldToggle.apply(this,arguments);setTimeout(updateFavorites,0);return result};"
new_v42toggle="const wrapped=function(){const result=oldToggle.apply(this,arguments);if(typeof window.rimaV43ShowFavorites!=='function')setTimeout(updateFavorites,0);return result};"
if h.count(old_v42toggle)!=1: raise SystemExit('V61_FAIL: wrapper toggle V42 não corresponde')
h=h.replace(old_v42toggle,new_v42toggle,1)

# V43 list gets the same .bsl container class as the regular category list,
# so both views inherit the same scrolling, card spacing and sizing rules.
h=h.replace('<div class="rima-v43-favlist" aria-label="Nenhum beat','<div class="bsl rima-v43-favlist" aria-label="Nenhum beat',1)
h=h.replace('<div class="rima-v43-favlist" aria-label="Seus beats favoritos">','<div class="bsl rima-v43-favlist" aria-label="Seus beats favoritos">',1)
if h.count('class="bsl rima-v43-favlist"')!=2: raise SystemExit('V61_FAIL: markup da lista Favorites não foi padronizado')

# Toolbar-only sync: never replace the Favorites card nodes on every player update.
sync_anchor="function sync(){document.querySelectorAll('.rima-v29-count').forEach(e=>e.textContent=String(count()));if(showing)render()}"
sync_add="""function syncToolbarOnly(){
  const n=String(count());
  ids.forEach(id=>{
   const root=document.getElementById(id);if(!root)return;
   let bar=root.querySelector(':scope > .rima-v43-tools');
   if(!bar)bar=ensureToolbar(root);
   const b=bar&&bar.querySelector('button.rima-v43-toggle');if(!b)return;
   const counter=b.querySelector('.rima-v29-count');if(counter)counter.textContent=n;
   b.classList.toggle('active',showing);b.setAttribute('aria-pressed',String(showing));
   if(showing)root.querySelectorAll('.row .tag.chip').forEach(chip=>{chip.classList.remove('on');chip.setAttribute('aria-pressed','false')});
  });
}
function sync(){document.querySelectorAll('.rima-v29-count').forEach(e=>e.textContent=String(count()));if(showing)render()}"""
if h.count(sync_anchor)!=1: raise SystemExit('V61_FAIL: sync V43 não corresponde')
h=h.replace(sync_anchor,sync_add,1)
old_v43pk="const f=function(){const r=oldPk.apply(this,arguments);render();return r};"
new_v43pk="const f=function(){const r=oldPk.apply(this,arguments);syncToolbarOnly();return r};"
if h.count(old_v43pk)!=1: raise SystemExit('V61_FAIL: wrapper pk V43 não corresponde')
h=h.replace(old_v43pk,new_v43pk,1)
old_v43bar="const f=function(){const r=oldBar.apply(this,arguments);render();return r};"
new_v43bar="const f=function(){const r=oldBar.apply(this,arguments);syncToolbarOnly();return r};"
if h.count(old_v43bar)!=1: raise SystemExit('V61_FAIL: wrapper bar V43 não corresponde')
h=h.replace(old_v43bar,new_v43bar,1)

css=r'''<style id="rimalab-favorites-stable-render-v61">
/* Favorites rows now use the same bsl > bi > beat-info > mc component as each category. */
#bp .rima-v43-favlist .rima-v43-fav-row,
#bq .rima-v43-favlist .rima-v43-fav-row,
#bbq .rima-v43-favlist .rima-v43-fav-row{
 display:flex!important;align-items:stretch!important;gap:9px!important;
 box-sizing:border-box!important;width:100%!important;min-width:0!important;
 margin:0!important;padding:7px 0!important;border:0!important;
 border-bottom:1px solid var(--ln)!important;border-radius:0!important;
 background:transparent!important;box-shadow:none!important
}
#bp .rima-v43-favlist .rima-v43-fav-row>.beat-info,
#bq .rima-v43-favlist .rima-v43-fav-row>.beat-info,
#bbq .rima-v43-favlist .rima-v43-fav-row>.beat-info{
 display:flex!important;flex:1 1 auto!important;flex-direction:column!important;
 min-width:0!important;max-width:100%!important;gap:3px!important
}
#bp .rima-v43-favlist .rima-v43-fav-play,
#bq .rima-v43-favlist .rima-v43-fav-play,
#bbq .rima-v43-favlist .rima-v43-fav-play{
 display:flex!important;flex:1 1 auto!important;flex-direction:column!important;
 justify-content:center!important;box-sizing:border-box!important;width:100%!important;
 min-width:0!important;max-width:100%!important;min-height:54px!important;height:auto!important;
 margin:0!important;padding:10px 14px!important;border:2px solid var(--ink)!important;
 border-radius:10px!important;background:var(--card)!important;color:var(--ink)!important;
 box-shadow:none!important;outline:0!important;text-align:left!important;
 font-family:inherit!important;font-size:inherit!important;font-weight:400!important;
 line-height:normal!important;letter-spacing:normal!important;text-transform:none!important;
 white-space:normal!important;overflow-wrap:anywhere!important;touch-action:manipulation!important
}
#bp .rima-v43-favlist .rima-v43-fav-play b,
#bq .rima-v43-favlist .rima-v43-fav-play b,
#bbq .rima-v43-favlist .rima-v43-fav-play b{
 display:block!important;max-width:100%!important;margin:0!important;overflow-wrap:anywhere!important;
 font-family:Anton,Impact,sans-serif!important;font-size:20px!important;font-weight:400!important;
 line-height:1.15!important;letter-spacing:normal!important
}
#bp .rima-v43-favlist .rima-v43-fav-play.on,
#bq .rima-v43-favlist .rima-v43-fav-play.on,
#bbq .rima-v43-favlist .rima-v43-fav-play.on,
#bp .rima-v43-favlist .rima-v43-fav-play.is-selected,
#bq .rima-v43-favlist .rima-v43-fav-play.is-selected,
#bbq .rima-v43-favlist .rima-v43-fav-play.is-selected{
 background:var(--ac)!important;color:var(--on)!important;
 border:2px solid var(--ink)!important;box-shadow:3px 3px 0 var(--ink)!important;
 outline:0!important
}
#bp .rima-v43-favlist .rima-v43-fav-play.on b,
#bq .rima-v43-favlist .rima-v43-fav-play.on b,
#bbq .rima-v43-favlist .rima-v43-fav-play.on b,
#bp .rima-v43-favlist .rima-v43-fav-play.is-selected b,
#bq .rima-v43-favlist .rima-v43-fav-play.is-selected b,
#bbq .rima-v43-favlist .rima-v43-fav-play.is-selected b{color:var(--on)!important}
#bp .rima-v43-favlist .beat-meta,#bq .rima-v43-favlist .beat-meta,#bbq .rima-v43-favlist .beat-meta{
 display:flex!important;align-items:center!important;gap:8px!important;min-width:0!important;
 padding:0 12px 7px!important;border:1px solid rgba(255,255,255,.08)!important;
 border-top:0!important;border-radius:0 0 14px 14px!important;background:rgba(255,255,255,.018)!important
}
#bp .rima-v43-favlist .beat-artist,#bq .rima-v43-favlist .beat-artist,#bbq .rima-v43-favlist .beat-artist{
 min-width:0!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important
}

/* Horizontal stage: allocate a real middle grid row to the selector and a flexible strip to beats. */
@media(orientation:landscape) and (min-width:560px){
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]){
  display:grid!important;box-sizing:border-box!important;width:100vw!important;height:100vh!important;
  min-height:100vh!important;max-height:100vh!important;
  grid-template-columns:minmax(0,1.42fr) minmax(0,1fr)!important;
  grid-template-rows:40px minmax(0,1fr) 40px!important;
  gap:6px 10px!important;padding:6px 12px calc(var(--rima-stage-bottom,108px) + 4px)!important;
  align-items:stretch!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.bk{
  grid-column:2!important;grid-row:1!important;width:100%!important;height:40px!important;min-height:40px!important;margin:0!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage{
  grid-column:1!important;grid-row:1 / 4!important;align-self:stretch!important;
  width:100%!important;height:100%!important;min-height:0!important;max-height:none!important;margin:0!important;
  box-sizing:border-box!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage){
  display:flex!important;flex-direction:column!important;align-items:stretch!important;
  grid-column:2!important;grid-row:2!important;align-self:stretch!important;
  box-sizing:border-box!important;width:100%!important;height:100%!important;
  min-width:0!important;min-height:0!important;max-height:none!important;
  margin:0!important;padding:8px 9px!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage)>.row.nw{
  flex:0 0 auto!important;min-height:0!important;margin:0 0 2px!important;gap:5px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage)>p.mut{
  flex:0 0 auto!important;margin:1px 0 2px!important;font-size:11px!important;line-height:1.15!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq{
  display:flex!important;position:relative!important;flex:1 1 auto!important;flex-direction:column!important;
  gap:4px!important;box-sizing:border-box!important;width:100%!important;max-width:100%!important;
  min-width:0!important;min-height:0!important;height:auto!important;max-height:none!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v50-category-row{
  display:flex!important;flex:0 0 36px!important;flex-wrap:nowrap!important;align-items:stretch!important;
  width:100%!important;height:36px!important;min-height:36px!important;max-height:36px!important;
  margin:0!important;padding:0!important;gap:5px!important;overflow:visible!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v50-category-row>.tag.chip{
  display:flex!important;flex:1 1 0%!important;align-items:center!important;justify-content:center!important;
  box-sizing:border-box!important;width:auto!important;min-width:0!important;max-width:none!important;
  height:36px!important;min-height:36px!important;margin:0!important;padding:4px 3px!important;
  border:1px solid rgba(255,255,255,.20)!important;border-radius:999px!important;
  white-space:nowrap!important;overflow:visible!important;font-size:clamp(9px,1vw,12px)!important;line-height:1.05!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools{
  display:flex!important;flex:0 0 40px!important;position:relative!important;width:100%!important;
  height:40px!important;min-height:40px!important;max-height:40px!important;margin:0!important;padding:0!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools button{
  width:100%!important;height:40px!important;min-height:40px!important;max-height:40px!important;margin:0!important;padding:5px 8px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>p.mut:not(:first-child){
  display:block!important;flex:0 0 12px!important;height:12px!important;min-height:12px!important;max-height:12px!important;
  margin:0!important;padding:0!important;overflow:hidden!important;white-space:nowrap!important;
  text-overflow:ellipsis!important;font-size:8px!important;line-height:12px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden]){
  display:flex!important;flex:1 1 auto!important;flex-direction:row!important;flex-wrap:nowrap!important;
  align-items:stretch!important;gap:8px!important;box-sizing:border-box!important;width:100%!important;
  max-width:100%!important;min-width:0!important;min-height:112px!important;height:auto!important;max-height:none!important;
  margin:0!important;padding:4px 5px!important;overflow-x:auto!important;overflow-y:hidden!important;
  overscroll-behavior-x:contain!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-x pan-y!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden])>.bi{
  display:flex!important;flex:0 0 clamp(190px,25vw,280px)!important;flex-direction:row!important;
  align-items:center!important;box-sizing:border-box!important;width:clamp(190px,25vw,280px)!important;
  min-width:0!important;max-width:none!important;height:100%!important;min-height:0!important;
  margin:0!important;padding:5px!important;gap:7px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden])>.bi>.beat-info{
  flex:1 1 0%!important;min-width:0!important;max-width:100%!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden])>.bi .mc{
  flex:1 1 auto!important;min-height:52px!important;height:auto!important;padding:8px 9px!important;
  font-size:clamp(12px,1.2vw,15px)!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.btn.w{
  grid-column:2!important;grid-row:3!important;align-self:stretch!important;width:100%!important;
  height:40px!important;min-height:40px!important;margin:0!important
 }
}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V61_FAIL: </body> ausente')
h=h[:pos]+css+'\n'+h[pos:]

m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='80': raise SystemExit('V61_FAIL: versionCode base não é 80')
g=g[:m.start(1)]+'81'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.3.8': raise SystemExit('V61_FAIL: versionName base não é 3.3.8')
g=g[:m.start(1)]+'3.3.9'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V61_OK: stop V40/V42 competing Favorites renderers, preserve first-tap DOM, share .bsl/.bi/.mc styling, stable landscape grid/scroll strip; 3.3.9/code81')
