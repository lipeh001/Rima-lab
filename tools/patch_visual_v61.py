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
old_v42pk="const wrapped=function(){const result=oldPk.apply(this,arguments);renderAll();setTimeout(renderAll,60);return result};"
new_v42pk="const f=function(){const result=oldPk.apply(this,arguments);if(typeof window.rimaV43ShowFavorites!=='function'){renderAll();setTimeout(renderAll,60)}return result};"
if h.count(old_v42pk)!=1: raise SystemExit('V61_FAIL: wrapper pk V42 não corresponde')
h=h.replace(old_v42pk,new_v42pk,1)
old_v42pk_tail='wrapped.__rimaV42=true;window.pk=wrapped;'
if h.count(old_v42pk_tail)!=1: raise SystemExit('V61_FAIL: finalização wrapper V42 não corresponde')
h=h.replace(old_v42pk_tail,'f.__rimaV42=true;window.pk=f;',1)
old_v42toggle="const wrapped=function(){const result=oldToggle.apply(this,arguments);setTimeout(updateFavorites,0);return result};"
new_v42toggle="const wrapped=function(){const result=oldToggle.apply(this,arguments);if(typeof window.rimaV43ShowFavorites!=='function')setTimeout(updateFavorites,0);return result};"
if h.count(old_v42toggle)!=1: raise SystemExit('V61_FAIL: wrapper toggle V42 não corresponde')
h=h.replace(old_v42toggle,new_v42toggle,1)

# V43 list gets the same .bsl container class as the regular category list,
# so both views inherit the same scrolling, card spacing and sizing rules.
h=h.replace("return '<div class=\"rima-v43-favlist\"><div class=\"rima-v43-empty mut\">","return '<div class=\"bsl rima-v43-favlist\"><div class=\"rima-v43-empty mut\">",1)
h=h.replace('<div class="rima-v43-favlist" aria-label="Seus beats favoritos">','<div class="bsl rima-v43-favlist" aria-label="Seus beats favoritos">',1)
if h.count('class="bsl rima-v43-favlist"')!=2: raise SystemExit('V61_FAIL: markup da lista Favorites não foi padronizado')

# Toolbar-only sync: never replace the Favorites card nodes on every player update.
sync_anchor="function sync(){document.querySelectorAll('.rima-v29-count').forEach(e=>e.textContent=String(count()));if(showing)render()}"
view_anchor="let showing=false,activeRoot='bp',busy=false;"
if h.count(view_anchor)!=1: raise SystemExit('V61_FAIL: estado V43 não corresponde')
h=h.replace(view_anchor,view_anchor+'\n const favoriteViews=new Map();',1)
sync_add="""function syncToolbarOnly(){
  const n=String(count());
  ids.forEach(id=>{
   const root=document.getElementById(id);if(!root)return;
   let bar=ensureToolbar(root);
   const b=bar&&bar.querySelector('button.rima-v43-toggle');if(!b)return;
   // Remove stale duplicate controls/icons left by legacy V40/V42 toolbars.
   Array.from(bar.querySelectorAll(':scope > button')).filter(x=>x!==b).forEach(x=>x.remove());
   b.innerHTML='<span class="rima-v60-heart-glyph" aria-hidden="true">♥</span><span class="rima-v60-fav-label">Favoritos</span><span class="rima-v29-count">'+n+'</span>';
   b.classList.toggle('active',showing);b.setAttribute('aria-pressed',String(showing));
   let view=root.querySelector(':scope > .rima-v43-favlist');
   if(showing){
    if(!view){view=favoriteViews.get(id)||null;if(view&&!view.isConnected)bar.insertAdjacentElement('afterend',view)}
    if(!view){renderRoot(root);return}
    favoriteViews.set(id,view);
    const selectedKey=String(window.ZS&&ZS.k==='lib'&&ZS.key||'');
    view.querySelectorAll('[data-v43-play]').forEach(card=>{const active=!!selectedKey&&card.getAttribute('data-v43-play')===selectedKey;card.classList.toggle('is-selected',active);card.classList.toggle('on',active);card.setAttribute('aria-pressed',String(active))});
    root.querySelectorAll(':scope > .bsl:not(.rima-v43-favlist)').forEach(list=>{list.hidden=true});
    root.querySelectorAll(':scope > .catalog-attribution').forEach(note=>{note.hidden=true});
    view.hidden=false;
    root.querySelectorAll('.row .tag.chip').forEach(chip=>{chip.classList.remove('on');chip.setAttribute('aria-pressed','false')});
   }else{
    if(view)removeView(root);favoriteViews.delete(id);
    root.querySelectorAll(':scope > .bsl:not(.rima-v43-favlist)').forEach(list=>{list.hidden=false});
    root.querySelectorAll(':scope > .catalog-attribution').forEach(note=>{note.hidden=false});
    root.querySelectorAll(':scope > .rima-v40-favlist,:scope > .rima-v42-favlist').forEach(old=>old.remove());
    const selected=String(window.ZS&&ZS.s||'').trim().toLowerCase();
    root.querySelectorAll('.row .tag.chip').forEach(chip=>{
     const label=String(chip.textContent||'').trim().toLowerCase();
     const active=!!selected&&label.startsWith(selected);
     chip.classList.toggle('on',active);chip.setAttribute('aria-pressed',String(active));
    });
   }
  });
}
function fixLandscapeList(){
 if(!document.body.classList.contains('rima-live-landscape'))return;
 const list=document.querySelector('#bq>.bsl:not([hidden])');if(!list)return;
 list.style.setProperty('display','flex','important');
 list.style.setProperty('flex-direction','row','important');
 list.style.setProperty('flex-wrap','nowrap','important');
 list.style.setProperty('height','112px','important');
 list.style.setProperty('min-height','112px','important');
 list.style.setProperty('max-height','112px','important');
 list.style.setProperty('flex','0 0 112px','important');
 list.style.setProperty('flex-shrink','0','important');
 list.style.setProperty('overflow-x','auto','important');
 list.style.setProperty('overflow-y','hidden','important');
 list.style.setProperty('touch-action','pan-x pan-y','important');
 list.querySelectorAll(':scope > .bi').forEach(card=>{
  card.style.setProperty('flex','0 0 320px','important');
  card.style.setProperty('width','320px','important');
  card.style.setProperty('height','100%','important');
 });
}
window.addEventListener('resize',fixLandscapeList);
window.addEventListener('orientationchange',()=>setTimeout(fixLandscapeList,0));
function sync(){document.querySelectorAll('.rima-v29-count').forEach(e=>e.textContent=String(count()));if(showing)render()}"""
if h.count(sync_anchor)!=1: raise SystemExit('V61_FAIL: sync V43 não corresponde')
h=h.replace(sync_anchor,sync_add,1)
old_v43pk="const f=function(){const r=oldPk.apply(this,arguments);render();return r};"
new_v43pk="const f=function(){ids.forEach(id=>{const v=document.querySelector('#'+id+' > .rima-v43-favlist');if(v)favoriteViews.set(id,v)});const r=oldPk.apply(this,arguments);syncToolbarOnly();fixLandscapeList();return r};"
if h.count(old_v43pk)!=1: raise SystemExit('V61_FAIL: wrapper pk V43 não corresponde')
h=h.replace(old_v43pk,new_v43pk,1)
old_v43bar="const f=function(){const r=oldBar.apply(this,arguments);render();return r};"
new_v43bar="const f=function(){const r=oldBar.apply(this,arguments);syncToolbarOnly();fixLandscapeList();return r};"
if h.count(old_v43bar)!=1: raise SystemExit('V61_FAIL: wrapper bar V43 não corresponde')
h=h.replace(old_v43bar,new_v43bar,1)

css=r'''<style id="rimalab-favorites-stable-render-v61">
/* Favorites uses the same bsl > bi > mc structure as each regular category. */
#bp .rima-v43-favlist,#bq .rima-v43-favlist,#bbq .rima-v43-favlist{
 display:block!important;box-sizing:border-box!important;width:100%!important;max-width:100%!important;
 min-width:0!important;max-height:46vh!important;overflow-y:auto!important;overflow-x:hidden!important;
 padding:2px 4px 2px 0!important;margin:8px 0!important;border-radius:14px!important;
 -webkit-overflow-scrolling:touch!important;overscroll-behavior:contain!important
}
#bp .rima-v43-fav-row,#bq .rima-v43-fav-row,#bbq .rima-v43-fav-row{
 display:flex!important;align-items:stretch!important;gap:8px!important;box-sizing:border-box!important;
 width:100%!important;min-width:0!important;margin:7px 0!important;padding:0 0 7px!important;
 border:0!important;border-bottom:1px solid var(--ln)!important;border-radius:0!important;
 background:transparent!important;box-shadow:none!important
}
#bp .rima-v43-fav-row.is-selected,#bq .rima-v43-fav-row.is-selected,#bbq .rima-v43-fav-row.is-selected{
 border:0!important;border-bottom:1px solid var(--ln)!important;border-radius:0!important;
 background:transparent!important;box-shadow:none!important;outline:0!important
}
#bp .rima-v43-fav-row>.beat-info,#bq .rima-v43-fav-row>.beat-info,#bbq .rima-v43-fav-row>.beat-info{
 display:flex!important;flex:1 1 0%!important;flex-direction:column!important;
 min-width:0!important;max-width:100%!important;gap:0!important
}
#bp .rima-v43-fav-play,#bq .rima-v43-fav-play,#bbq .rima-v43-fav-play{
 display:flex!important;flex:1 1 auto!important;align-items:center!important;justify-content:center!important;
 box-sizing:border-box!important;width:100%!important;min-width:0!important;max-width:100%!important;
 min-height:54px!important;height:auto!important;margin:0!important;padding:10px 14px!important;
 text-align:left!important;white-space:normal!important;overflow-wrap:anywhere!important;
 font-family:inherit!important;font-weight:400!important;line-height:normal!important;
 border:2px solid var(--ink)!important;border-radius:6px!important;
 background:var(--card)!important;color:var(--ink)!important;box-shadow:none!important
}
#bp .rima-v43-fav-play.on,#bq .rima-v43-fav-play.on,#bbq .rima-v43-fav-play.on,
#bp .rima-v43-fav-play.is-selected,#bq .rima-v43-fav-play.is-selected,#bbq .rima-v43-fav-play.is-selected{
 background:var(--ac)!important;color:var(--on)!important;border:2px solid var(--ink)!important;
 box-shadow:3px 3px 0 var(--ink)!important
}
#bp .rima-v43-fav-play b,#bq .rima-v43-fav-play b,#bbq .rima-v43-fav-play b{
 display:block!important;margin:0!important;font-family:Anton,Impact,sans-serif!important;
 font-size:20px!important;font-weight:400!important;line-height:1.15!important;letter-spacing:normal!important
}
#bp .rima-v43-fav-row .beat-meta,#bq .rima-v43-fav-row .beat-meta,#bbq .rima-v43-fav-row .beat-meta{
 display:flex!important;align-items:center!important;gap:8px!important;min-width:0!important;
 margin:0!important;padding:3px 10px 0!important;border:0!important;background:transparent!important
}
#bp>.rima-v43-tools,#bq>.rima-v43-tools,#bbq>.rima-v43-tools{
 display:flex!important;align-items:stretch!important;width:100%!important;min-width:0!important
}
#bp>.rima-v43-tools button,#bq>.rima-v43-tools button,#bbq>.rima-v43-tools button{
 display:flex!important;align-items:center!important;justify-content:center!important;gap:7px!important
}
/* V43 markup includes a literal heart; V60 also draws ::before. Hide the text glyph. */
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart,#bbq .rima-v43-fav-heart,
#bp .rima-v29-fav,#bq .rima-v29-fav,#bbq .rima-v29-fav{font-size:0!important;line-height:0!important}
#bp .rima-v43-fav-heart::before,#bq .rima-v43-fav-heart::before,#bbq .rima-v43-fav-heart::before{font-size:21px!important;line-height:1!important}
#bp .rima-v43-fav-play.is-selected,#bq .rima-v43-fav-play.is-selected,#bbq .rima-v43-fav-play.is-selected,
#bp .rima-v43-fav-play.on,#bq .rima-v43-fav-play.on,#bbq .rima-v43-fav-play.on{
 background:var(--ac)!important;color:var(--on)!important;border:2px solid var(--ink)!important;box-shadow:3px 3px 0 var(--ink)!important
}
#bp .rima-v43-fav-play.is-selected b,#bq .rima-v43-fav-play.is-selected b,#bbq .rima-v43-fav-play.is-selected b,
#bp .rima-v43-fav-play.on b,#bq .rima-v43-fav-play.on b,#bbq .rima-v43-fav-play.on b{color:var(--on)!important}
/* Landscape: separate stage, selector card and stop button; make the beat strip tall enough to use. */
@media(orientation:landscape) and (min-width:560px){
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]){
  display:grid!important;position:fixed!important;inset:0!important;box-sizing:border-box!important;
  width:100vw!important;height:100vh!important;min-height:100vh!important;max-height:100vh!important;
  grid-template-columns:minmax(0,1.42fr) minmax(0,1fr)!important;
  grid-template-rows:40px minmax(0,1fr) 40px!important;gap:6px 10px!important;
  padding:6px 12px calc(var(--rima-stage-bottom,108px) + 4px)!important;
  align-items:stretch!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.bk{
  grid-column:2!important;grid-row:1!important;width:100%!important;height:40px!important;min-height:40px!important;margin:0!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage{
  grid-column:1!important;grid-row:1 / 4!important;align-self:stretch!important;
  width:100%!important;height:100%!important;min-height:0!important;max-height:none!important;margin:0!important;box-sizing:border-box!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage){
  display:flex!important;flex-direction:column!important;align-items:stretch!important;
  grid-column:2!important;grid-row:2!important;align-self:stretch!important;box-sizing:border-box!important;
  width:100%!important;height:100%!important;min-width:0!important;min-height:0!important;max-height:none!important;
  margin:0!important;padding:8px 9px!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage)>.row.nw{
  flex:0 0 auto!important;min-height:0!important;margin:0 0 2px!important;gap:5px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage)>p.mut{
  flex:0 0 auto!important;margin:1px 0 2px!important;font-size:10px!important;line-height:1.12!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq{
  display:flex!important;position:relative!important;flex:1 1 auto!important;flex-direction:column!important;gap:4px!important;
  box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;
  min-height:0!important;height:auto!important;max-height:none!important;overflow:hidden!important
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
  display:flex!important;flex:0 0 112px!important;height:112px!important;flex-direction:row!important;flex-wrap:nowrap!important;
  align-items:stretch!important;gap:8px!important;box-sizing:border-box!important;width:100%!important;
  max-width:100%!important;min-width:0!important;min-height:112px!important;max-height:112px!important;flex-shrink:0!important;align-self:stretch!important;
  margin:0!important;padding:4px 5px!important;overflow-x:auto!important;overflow-y:hidden!important;
  overscroll-behavior-x:contain!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-x pan-y!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden])>.bi{
  display:flex!important;flex:0 0 clamp(190px,25vw,280px)!important;flex-direction:row!important;align-items:center!important;
  box-sizing:border-box!important;width:clamp(190px,25vw,280px)!important;min-width:0!important;max-width:none!important;
  height:100%!important;min-height:0!important;margin:0!important;padding:5px!important;gap:7px!important
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
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='80': raise SystemExit('V61_FAIL: versionCode base não é 80')
g=g[:m.start(1)]+'81'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.3.8': raise SystemExit('V61_FAIL: versionName base não é 3.3.8')
g=g[:m.start(1)]+'3.3.9'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V61_OK: stop V40/V42 competing Favorites renderers, preserve first-tap DOM, share .bsl/.bi/.mc styling, stable landscape grid/scroll strip; 3.3.9/code81')
