#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V58_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-stage-selector-favorites-v58' in h: raise SystemExit('V58_FAIL: patch já aplicado')
if 'rimalab-startup-unfreeze-v57' not in h or 'rimalab-player-stage-gate-runtime-v51' not in h:
 raise SystemExit('V58_FAIL: base 3.3.5/V51 ausente')

# 1) A playback failure must not replace the live stage with the setup-step error screen.
old_fallback="function zFallback(msg){zEC=[];if(!play)return;const text=(msg||'Não foi possível carregar este beat.')+' Volte à lista e escolha outra faixa.';stop();zMsg(text);const ck=$('#ck'),cb=$('#cb'),cs=$('#cs');if(ck)ck.textContent='Beat indisponível';if(cb)cb.textContent='↩';if(cs)cs.textContent=text;try{$('#lv').hidden=false;$('#lv').style.display=''}catch(e){} }"
new_fallback="""function zFallback(msg){
 zEC=[];if(!play)return;
 const text=(msg||'Não foi possível carregar este beat.')+' Volte à lista e escolha outra faixa.';
 const live=document.getElementById('lv'),setup=document.getElementById('train-step-2');
 const inLiveStage=!!(live&&!live.hidden&&(!setup||setup.hidden));
 stop();
 if(inLiveStage){
  document.body.classList.add('pl');document.body.classList.remove('pv','sy','rima-player-visible');
  const ck=document.getElementById('ck'),cb=document.getElementById('cb'),cs=document.getElementById('cs');
  if(ck)ck.textContent='Beat indisponível';
  if(cb)cb.textContent='↩';
  if(cs)cs.textContent='Esse beat não abriu. Escolha outra faixa na lista abaixo.';
  window.__rimaV58RecoveryPending=true;
  return;
 }
 if(setup&&!setup.hidden){
  const bp=document.getElementById('bp');
  if(bp){let note=bp.querySelector('.rima-v58-audio-error');if(!note){note=document.createElement('p');note.className='rima-v58-audio-error';bp.appendChild(note)}note.textContent='Esse beat não abriu. Escolha outra faixa.'}
  return;
 }
 zMsg(text);
}"""
if h.count(old_fallback)!=1: raise SystemExit('V58_FAIL: zFallback base não corresponde')
h=h.replace(old_fallback,new_fallback,1)

# 2) Allow the player to become visible during the setup-step preview as well as during live training.
gate_id='rimalab-player-stage-gate-runtime-v51'
m=re.search(r'<script\b[^>]*id=["\']'+gate_id+r'["\'][^>]*>(.*?)</script>',h,re.S)
if not m: raise SystemExit('V58_FAIL: gate V51 ausente')
js=m.group(1)
old_live="const live=!lv.hidden&&(!setup||setup.hidden)&&body.classList.contains('pl')&&!body.classList.contains('pv')&&!body.classList.contains('sy');"
new_live="const live=!lv.hidden&&(!setup||setup.hidden)&&body.classList.contains('pl')&&!body.classList.contains('pv')&&!body.classList.contains('sy');const setupPreview=!!(setup&&!setup.hidden&&body.classList.contains('pl')&&body.classList.contains('pv')&&!body.classList.contains('sy'));"
if js.count(old_live)!=1: raise SystemExit('V58_FAIL: expressão live V51 não corresponde')
js=js.replace(old_live,new_live,1)
if js.count('const eligible=live&&audio;')!=1: raise SystemExit('V58_FAIL: condição eligible V51 não corresponde')
js=js.replace('const eligible=live&&audio;','const eligible=(live||setupPreview)&&audio;',1)
h=h[:m.start(1)]+js+h[m.end(1):]

# 3) Scoped selection recovery/synchronization. No global MutationObserver or polling is introduced.
runtime=r'''<script id="rimalab-stage-selector-favorites-v58">
(function(){
 'use strict';
 const body=document.body;
 const $=s=>document.querySelector(s);
 function syncSelection(){
  const key=String(window.ZS&&ZS.k==='lib'&&ZS.key||'');
  document.querySelectorAll('#bp .bsl .bi .mc[data-rima-track-key],#bq .bsl .bi .mc[data-rima-track-key],#bbq .bsl .bi .mc[data-rima-track-key]').forEach(b=>{
   const on=!!key&&b.getAttribute('data-rima-track-key')===key;
   b.classList.toggle('on',on);b.setAttribute('aria-pressed',String(on));
  });
  document.querySelectorAll('#bp .rima-v43-fav-row,#bq .rima-v43-fav-row,#bbq .rima-v43-fav-row').forEach(row=>{
   const on=!!key&&row.getAttribute('data-key')===key;
   row.classList.toggle('is-selected',on);
   const b=row.querySelector('.rima-v43-fav-play');
   if(b){b.classList.toggle('on',on);b.classList.toggle('is-selected',on);b.setAttribute('aria-pressed',String(on));if(on)b.setAttribute('aria-current','true');else b.removeAttribute('aria-current')}
  });
 }
 function settleSelection(){requestAnimationFrame(()=>requestAnimationFrame(syncSelection))}
 const oldLP=window.zLP;
 if(typeof oldLP==='function'&&!oldLP.__rimaV58){
  const wrapped=function(){
   const result=oldLP.apply(this,arguments);
   const pending=!!window.__rimaV58RecoveryPending;
   if(pending&&window.ZS&&ZS.k==='lib'&&ZS.key&&document.getElementById('lv')&&!document.getElementById('lv').hidden){
    window.__rimaV58RecoveryPending=false;
    const note=document.querySelector('.rima-v58-audio-error');if(note)note.remove();
    requestAnimationFrame(()=>{if(typeof window.lvStart==='function')window.lvStart()});
   }
   settleSelection();return result;
  };
  wrapped.__rimaV58=true;window.zLP=wrapped;
 }
 const oldLS=window.zLS;
 if(typeof oldLS==='function'&&!oldLS.__rimaV58){
  const wrapped=function(){const result=oldLS.apply(this,arguments);settleSelection();return result};
  wrapped.__rimaV58=true;window.zLS=wrapped;
 }
 const oldFav=window.rimaV41StartFavorites;
 if(typeof oldFav==='function'&&!oldFav.__rimaV58){
  const wrapped=function(){const result=oldFav.apply(this,arguments);settleSelection();return result};
  wrapped.__rimaV58=true;window.rimaV41StartFavorites=wrapped;
 }
 document.addEventListener('click',e=>{
  const chip=e.target&&e.target.closest?e.target.closest('#bp .row .tag.chip,#bq .row .tag.chip,#bbq .row .tag.chip'):null;
  if(chip)settleSelection();
  const favorite=e.target&&e.target.closest?e.target.closest('#bp [data-v43-play],#bq [data-v43-play],#bbq [data-v43-play]'):null;
  if(favorite)settleSelection();
 },true);
 window.rimaV58SyncSelection=syncSelection;
 settleSelection();
})();
</script>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V58_FAIL: </body> ausente')
h=h[:pos]+runtime+'\n'+h[pos:]

css=r'''<style id="rimalab-stage-selector-favorites-style-v58">
/* Keep the live selector's category row and Favorites toolbar as separate, fixed-height controls. */
#lv:not([hidden]) #bq{box-sizing:border-box!important;min-width:0!important;max-width:100%!important}
#lv:not([hidden]) #bq>.rima-v50-category-row{box-sizing:border-box!important;flex:0 0 38px!important;width:100%!important;min-width:0!important;height:38px!important;min-height:38px!important;margin:3px 0 5px!important;padding:0!important;gap:6px!important;overflow:hidden!important}
#lv:not([hidden]) #bq>.rima-v50-category-row>.tag.chip{box-sizing:border-box!important;flex:1 1 0!important;min-width:0!important;max-width:none!important;height:38px!important;min-height:38px!important;margin:0!important;padding:7px 3px!important;display:flex!important;align-items:center!important;justify-content:center!important;white-space:nowrap!important;line-height:1.05!important}
#lv:not([hidden]) #bq>.rima-v43-tools{box-sizing:border-box!important;flex:0 0 42px!important;width:100%!important;min-width:0!important;height:42px!important;min-height:42px!important;margin:0 0 7px!important;padding:0!important;overflow:visible!important}
#lv:not([hidden]) #bq>.rima-v43-tools button{box-sizing:border-box!important;width:100%!important;min-width:0!important;height:42px!important;min-height:42px!important;margin:0!important;padding:7px 12px!important;line-height:1.1!important}
#lv:not([hidden]) #bq>.rima-v43-favlist,#lv:not([hidden]) #bq>.bsl{box-sizing:border-box!important;min-width:0!important;max-width:100%!important}

/* Favorites use the same card geometry, typography and selected treatment as Boom bap/Trap/Drill. */
#bp .rima-v43-fav-row,#bq .rima-v43-fav-row,#bbq .rima-v43-fav-row{
 display:flex!important;align-items:center!important;gap:8px!important;box-sizing:border-box!important;
 width:100%!important;min-width:0!important;margin:0!important;padding:4px 0!important;
 border:0!important;border-bottom:1px solid rgba(255,255,255,.075)!important;border-radius:0!important;
 background:transparent!important;box-shadow:none!important
}
#bp .rima-v43-fav-row>.beat-info,#bq .rima-v43-fav-row>.beat-info,#bbq .rima-v43-fav-row>.beat-info{
 display:flex!important;flex:1 1 0%!important;flex-direction:column!important;gap:3px!important;
 width:auto!important;min-width:0!important;max-width:100%!important
}
#bp .rima-v43-fav-play,#bq .rima-v43-fav-play,#bbq .rima-v43-fav-play{
 display:flex!important;align-items:center!important;justify-content:flex-start!important;
 box-sizing:border-box!important;width:100%!important;min-width:0!important;max-width:100%!important;
 min-height:58px!important;height:auto!important;margin:0!important;padding:10px 12px!important;
 border:1px solid rgba(255,255,255,.12)!important;border-left:1px solid rgba(255,255,255,.12)!important;
 border-radius:14px!important;background:var(--card,rgba(255,255,255,.035))!important;
 color:var(--ink,#f2f5eb)!important;text-align:left!important;white-space:normal!important;
 overflow-wrap:anywhere!important;line-height:1.2!important;font-size:16px!important;
 font-family:inherit!important;cursor:pointer!important;touch-action:manipulation!important
}
#bp .rima-v43-fav-play b,#bq .rima-v43-fav-play b,#bbq .rima-v43-fav-play b{
 display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;
 max-width:100%!important;overflow:hidden!important;font-family:inherit!important;font-weight:800!important;
 font-size:16px!important;line-height:1.2!important;letter-spacing:normal!important
}
#bp .rima-v43-fav-play.on,#bq .rima-v43-fav-play.on,#bbq .rima-v43-fav-play.on,
#bp .rima-v43-fav-play.is-selected,#bq .rima-v43-fav-play.is-selected,#bbq .rima-v43-fav-play.is-selected{
 background:linear-gradient(105deg,rgba(229,196,91,.34),rgba(229,196,91,.14))!important;
 background-color:rgba(229,196,91,.22)!important;border:1px solid rgba(239,207,106,.98)!important;
 border-left:4px solid #e5c45b!important;color:#fff1b5!important;
 box-shadow:inset 0 0 0 1px rgba(255,235,170,.10),0 0 0 1px rgba(229,196,91,.22),0 7px 20px rgba(229,196,91,.14)!important
}
#bp .rima-v43-fav-row.is-selected,#bq .rima-v43-fav-row.is-selected,#bbq .rima-v43-fav-row.is-selected{background:transparent!important;box-shadow:none!important}
#bp .rima-v43-fav-meta,#bq .rima-v43-fav-meta,#bbq .rima-v43-fav-meta,
#bp .rima-v43-fav-row .beat-meta,#bq .rima-v43-fav-row .beat-meta,#bbq .rima-v43-fav-row .beat-meta{
 display:flex!important;align-items:center!important;gap:8px!important;min-width:0!important;
 padding:4px 10px 0!important;border:0!important;background:transparent!important
}

/* Normalize every favorite heart to a true square glyph; do not stretch the font or button. */
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart,#bbq .rima-v43-fav-heart,
#bp .rima-v29-fav,#bq .rima-v29-fav,#bbq .rima-v29-fav,#pbar #rima-v29-player-heart{
 box-sizing:border-box!important;display:grid!important;place-items:center!important;
 flex:0 0 42px!important;width:42px!important;min-width:42px!important;max-width:42px!important;
 height:42px!important;min-height:42px!important;max-height:42px!important;padding:0!important;
 font-family:Arial,sans-serif!important;font-size:21px!important;font-style:normal!important;
 font-weight:400!important;font-stretch:normal!important;letter-spacing:0!important;line-height:1!important;
 text-align:center!important;white-space:nowrap!important;transform:none!important
}
#bp .rima-v43-toggle,#bq .rima-v43-toggle,#bbq .rima-v43-toggle{font-family:inherit!important;letter-spacing:normal!important}

/* Portrait keeps the page vertically scrollable; the selector never expands when categories change. */
@media(orientation:portrait) and (max-width:760px){
 html,body,main{overflow-x:hidden!important}
 body.pl:not(.pv) #lv:not([hidden]){overflow-y:auto!important;overflow-x:hidden!important;touch-action:pan-y!important}
 body.pl:not(.pv) #lv:not([hidden])>.card:not(.stage){height:auto!important;max-height:none!important;min-height:0!important;overflow:visible!important}
 body.pl:not(.pv) #lv:not([hidden]) #bq{display:flex!important;flex:0 0 auto!important;flex-direction:column!important;height:auto!important;max-height:none!important;min-height:0!important;overflow:visible!important}
 body.pl:not(.pv) #lv:not([hidden]) #bq>.bsl:not([hidden]),body.pl:not(.pv) #lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden]){
  flex:0 0 auto!important;min-height:0!important;height:auto!important;max-height:min(28vh,235px)!important;
  overflow-y:auto!important;overflow-x:hidden!important;touch-action:pan-y!important;-webkit-overflow-scrolling:touch!important
 }
 #bp>.rima-v43-tools,#bq>.rima-v43-tools{height:42px!important;min-height:42px!important}
}

/* Landscape: full-width category/Favorites controls, several beats visible, horizontal list swipe, no bottom nav. */
@media(orientation:landscape) and (min-width:560px){
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage){min-width:0!important;overflow:hidden!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq{
  display:grid!important;grid-template-columns:minmax(0,1fr)!important;
  grid-template-rows:34px 38px 12px minmax(0,1fr)!important;
  column-gap:0!important;row-gap:4px!important;width:100%!important;max-width:100%!important;
  min-width:0!important;height:100%!important;max-height:100%!important;min-height:0!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v50-category-row{
  grid-column:1!important;grid-row:1!important;display:flex!important;width:100%!important;
  height:34px!important;min-height:34px!important;max-height:34px!important;margin:0!important;
  padding:0!important;gap:5px!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v50-category-row>.tag.chip{
  flex:1 1 0%!important;width:auto!important;min-width:0!important;height:34px!important;min-height:34px!important;
  max-width:none!important;padding:4px 2px!important;font-size:clamp(9px,1vw,12px)!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools{
  grid-column:1!important;grid-row:2!important;display:flex!important;width:100%!important;
  height:38px!important;min-height:38px!important;max-height:38px!important;margin:0!important;padding:0!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools button{
  width:100%!important;height:38px!important;min-height:38px!important;max-height:38px!important;padding:4px 8px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>p.mut:not(:first-child){
  grid-column:1!important;grid-row:3!important;display:block!important;height:12px!important;min-height:12px!important;
  max-height:12px!important;margin:0!important;padding:0!important;overflow:hidden!important;font-size:8px!important;line-height:12px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden]),
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden]){
  grid-column:1!important;grid-row:4!important;display:grid!important;position:relative!important;
  grid-auto-flow:column!important;grid-auto-columns:clamp(190px,27vw,310px)!important;
  grid-template-rows:minmax(0,1fr)!important;align-items:stretch!important;gap:8px!important;
  box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;
  height:100%!important;max-height:100%!important;min-height:0!important;margin:0!important;padding:3px 4px 5px!important;
  overflow-x:auto!important;overflow-y:hidden!important;overscroll-behavior-x:contain!important;
  -webkit-overflow-scrolling:touch!important;touch-action:pan-x pan-y!important;scroll-snap-type:x proximity!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl>.bi,
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist>.rima-v43-fav-row{
  box-sizing:border-box!important;display:flex!important;flex-direction:row!important;align-items:center!important;
  width:100%!important;min-width:0!important;max-width:none!important;height:100%!important;min-height:0!important;
  margin:0!important;padding:5px!important;scroll-snap-align:start!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl>.bi>.beat-info,
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist>.rima-v43-fav-row>.beat-info{
  flex:1 1 0%!important;min-width:0!important;max-width:100%!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl>.bi .mc,
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist .rima-v43-fav-play{
  min-height:54px!important;height:auto!important;padding:8px 10px!important;font-size:clamp(12px,1.3vw,16px)!important
 }
 html body.pl:not(.pv).rima-live-landscape nav{display:none!important;visibility:hidden!important;pointer-events:none!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]){padding-bottom:calc(var(--rima-stage-bottom,108px) + 4px)!important}
}
/* Keep vertical page scrolling on touch; only the landscape beat strip captures horizontal swipes. */
.rima-v58-audio-error{margin:8px 0!important;padding:8px 10px!important;border:1px solid rgba(229,196,91,.4)!important;border-radius:10px!important;color:#f0d77d!important;font-size:13px!important}
</style>'''
pos=h.lower().rfind('</body>')
h=h[:pos]+css+'\n'+h[pos:]

# Version bump is intentionally isolated to Android metadata.
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='77': raise SystemExit('V58_FAIL: versionCode base não é 77')
g=g[:m.start(1)]+'78'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.3.5': raise SystemExit('V58_FAIL: versionName base não é 3.3.5')
g=g[:m.start(1)]+'3.3.6'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V58_OK: stage selector dimensions, favorites parity, square hearts, selection recovery, preview player gate, landscape horizontal beat strip/nav hidden; 3.3.6/code78')
