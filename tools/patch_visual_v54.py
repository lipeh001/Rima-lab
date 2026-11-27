#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V54_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-unified-catalog-favorites-v54' in h: raise SystemExit('V54_FAIL: patch repetido')
if 'rimalab-global-scroll-system-v53' not in h: raise SystemExit('V54_FAIL: V53 ausente')

# One favorites state machine for the three actual selectors: setup, live, battle.
tag='<script id="rimalab-favorites-layout-runtime-v43">'
a=h.find(tag)
if a<0: raise SystemExit('V54_FAIL: V43 runtime ausente')
b=a+len(tag);z=h.find('</script>',b);js=h[b:z]
if "ids=['bp','bq']" not in js: raise SystemExit('V54_FAIL: V43 roots inesperados')
js=js.replace("ids=['bp','bq']","ids=['bp','bq','bbq']",1)

# Favorites items reuse the same visual skeleton as the normal catalog cards.
pat=re.compile(r" function favoriteMarkup\(\)\{.*?\n \}\n function syncFavoriteDownloads",re.S)
replacement=r''' function favoriteMarkup(){
  const saved=new Set(read()),items=allTracks().filter(t=>saved.has(t.key));
  if(!items.length)return '<div class="rima-v43-favlist"><div class="rima-v43-empty mut">Nenhum beat favoritado ainda. Toque no coração de um beat para adicioná-lo.</div></div>';
  return '<div class="rima-v43-favlist" aria-label="Seus beats favoritos">'+items.map(t=>{
   const selected=!!(typeof ZS!=='undefined'&&ZS&&ZS.k==='lib'&&ZS.key===t.key);
   const title=esc(t.x[1]),artist=esc(t.x[6]||'Artista independente'),key=esc(t.key);
   return '<div class="bi rima-v43-fav-row" data-key="'+key+'">'+
    '<div class="beat-info"><button class="mc rima-v43-fav-play'+(selected?' on is-selected':'')+'" type="button" data-rima-track-key="'+key+'" data-v43-play="'+key+'" aria-pressed="'+String(selected)+'"'+(selected?' aria-current="true"':'')+'><b>'+title+'</b></button><div class="beat-meta"><span class="beat-artist">'+artist+'</span>'+favoriteStatusMarkup(t)+'</div></div>'+
    '<button class="rima-v29-fav rima-v43-fav-heart on" type="button" data-v43-heart="'+key+'" aria-label="Remover dos favoritos" aria-pressed="true">♥</button>'+favoriteDownloadMarkup(t)+'</div>';
  }).join('')+'</div>';
 }
 function syncFavoriteDownloads'''
js,n=pat.subn(replacement,js,count=1)
if n!=1: raise SystemExit('V54_FAIL: favoriteMarkup não encontrado')
js=js.replace("row&&row.querySelector('.rima-v43-fav-info')","row&&row.querySelector('.rima-v43-fav-info,.beat-info')",1)
for old,new in [
 ("#bp .rima-v43-toggle,#bq .rima-v43-toggle","#bp .rima-v43-toggle,#bq .rima-v43-toggle,#bbq .rima-v43-toggle"),
 ("b.closest('#bp,#bq').id","b.closest('#bp,#bq,#bbq').id"),
 ("#bp [data-v43-play],#bq [data-v43-play]","#bp [data-v43-play],#bq [data-v43-play],#bbq [data-v43-play]"),
 ("#bp [data-v43-heart],#bq [data-v43-heart]","#bp [data-v43-heart],#bq [data-v43-heart],#bbq [data-v43-heart]"),
 ("#bp .row .tag.chip,#bq .row .tag.chip","#bp .row .tag.chip,#bq .row .tag.chip,#bbq .row .tag.chip"),
 ("chip.closest('#bp,#bq').id","chip.closest('#bp,#bq,#bbq').id"),
 ("#bp [data-rima-fav],#rima-v29-player-heart","#bp [data-rima-fav],#bq [data-rima-fav],#bbq [data-rima-fav],#rima-v29-player-heart")
]:
 if old not in js: raise SystemExit('V54_FAIL: seletor V43 ausente: '+old)
 js=js.replace(old,new,1)
h=h[:b]+js+h[z:]

# Keep selection highlighting in all three catalog instances.
tag45='<script id="rimalab-selection-feedback-runtime-v45">'
a=h.find(tag45)
if a<0: raise SystemExit('V54_FAIL: V45 runtime ausente')
b=a+len(tag45);z=h.find('</script>',b);v=h[b:z]
for old,new in [
 ("#bp .bsl .bi .mc[data-rima-track-key],#bq .bsl .bi .mc[data-rima-track-key]","#bp .bsl .bi .mc[data-rima-track-key],#bq .bsl .bi .mc[data-rima-track-key],#bbq .bsl .bi .mc[data-rima-track-key]"),
 ("#bp .rima-v43-fav-row,#bq .rima-v43-fav-row","#bp .rima-v43-fav-row,#bq .rima-v43-fav-row,#bbq .rima-v43-fav-row"),
 ("#bp .bsl .bi .mc,#bq .bsl .bi .mc,#bp [data-v43-play],#bq [data-v43-play]","#bp .bsl .bi .mc,#bq .bsl .bi .mc,#bbq .bsl .bi .mc,#bp [data-v43-play],#bq [data-v43-play],#bbq [data-v43-play]"),
 ("#bp [data-rima-fav],#bp [data-v43-heart],#bq [data-rima-fav],#bq [data-v43-heart],#rima-v29-player-heart","#bp [data-rima-fav],#bp [data-v43-heart],#bq [data-rima-fav],#bq [data-v43-heart],#bbq [data-rima-fav],#bbq [data-v43-heart],#rima-v29-player-heart")
]:
 if old not in v: raise SystemExit('V54_FAIL: seletor V45 ausente: '+old)
 v=v.replace(old,new,1)
h=h[:b]+v+h[z:]
h=h.replace("['bp','bq'].forEach(id=>{","['bp','bq','bbq'].forEach(id=>{",1)

css=r'''<style id="rimalab-unified-catalog-favorites-v54">
/* Same single list and same card grammar in setup, live stage and battle. */
#train-step-2 #bp>.bsl,#train-step-2 #bp>.rima-v43-favlist,#lv:not([hidden]) #bq>.bsl,#lv:not([hidden]) #bq>.rima-v43-favlist,#bt #bbq>.bsl,#bt #bbq>.rima-v43-favlist{height:auto!important;max-height:min(42vh,320px)!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-y!important}

#bp>.rima-v43-tools,#bq>.rima-v43-tools,#bbq>.rima-v43-tools{display:flex!important;position:relative!important;float:none!important;clear:both!important;width:100%!important;max-width:100%!important;box-sizing:border-box!important;margin:8px 0 10px!important;padding:0!important}
#bp>.rima-v43-tools button,#bq>.rima-v43-tools button,#bbq>.rima-v43-tools button{display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;min-height:46px!important;padding:8px 14px!important;border:1px solid rgba(229,196,91,.55)!important;border-radius:14px!important;background:rgba(220,190,80,.12)!important;color:#f0d77d!important;font-weight:600!important;font-size:16px!important;white-space:nowrap!important}
#bp>.rima-v43-tools button.active,#bq>.rima-v43-tools button.active,#bbq>.rima-v43-tools button.active{background:rgba(220,190,80,.22)!important;border-color:#e5c45b!important}
#bp>.rima-v43-favlist,#bq>.rima-v43-favlist,#bbq>.rima-v43-favlist{display:block!important;position:relative!important;box-sizing:border-box!important;clear:both!important;float:none!important;width:100%!important;max-width:100%!important;min-width:0!important;max-height:46vh!important;overflow-y:auto!important;overflow-x:hidden!important;padding:2px 4px 2px 0!important;margin:8px 0!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-y!important}
#bp .rima-v43-fav-row,#bq .rima-v43-fav-row,#bbq .rima-v43-fav-row{display:flex!important;position:relative!important;align-items:stretch!important;gap:9px!important;width:100%!important;min-width:0!important;box-sizing:border-box!important;margin:0!important;padding:7px 0!important;border:0!important;border-bottom:1px solid rgba(255,255,255,.075)!important;border-radius:0!important;background:transparent!important;box-shadow:none!important}
#bp .rima-v43-fav-row>.beat-info,#bq .rima-v43-fav-row>.beat-info,#bbq .rima-v43-fav-row>.beat-info{display:flex!important;flex:1 1 auto!important;flex-direction:column!important;gap:3px!important;min-width:0!important;width:auto!important;max-width:100%!important}
#bp .rima-v43-favlist .rima-v43-fav-play,#bq .rima-v43-favlist .rima-v43-fav-play,#bbq .rima-v43-favlist .rima-v43-fav-play{display:flex!important;align-items:center!important;justify-content:flex-start!important;box-sizing:border-box!important;width:100%!important;min-width:0!important;max-width:100%!important;min-height:50px!important;height:auto!important;margin:0!important;padding:9px 12px 3px!important;border:1px solid rgba(255,255,255,.08)!important;border-bottom:0!important;border-radius:14px 14px 0 0!important;background:var(--card,#151a13)!important;color:var(--ink,#f2f5eb)!important;text-align:left!important;white-space:normal!important;overflow-wrap:anywhere!important;line-height:1.25!important;font-size:16px!important;cursor:pointer!important;pointer-events:auto!important;touch-action:manipulation!important}
#bp .rima-v43-fav-play b,#bq .rima-v43-fav-play b,#bbq .rima-v43-fav-play b{display:block!important;max-width:100%!important;font-family:Anton,Impact,'Arial Narrow',sans-serif!important;font-weight:400!important;font-size:16px!important;line-height:1.25!important;overflow-wrap:anywhere!important}
#bp .rima-v43-fav-row .beat-meta,#bq .rima-v43-fav-row .beat-meta,#bbq .rima-v43-fav-row .beat-meta{display:flex!important;align-items:center!important;gap:8px!important;min-width:0!important;padding:0 12px 7px!important;border:1px solid rgba(255,255,255,.08)!important;border-top:0!important;border-radius:0 0 14px 14px!important;background:rgba(255,255,255,.025)!important}
#bp .rima-v43-fav-row .beat-artist,#bq .rima-v43-fav-row .beat-artist,#bbq .rima-v43-fav-row .beat-artist{display:block!important;min-width:0!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;color:#9ba493!important;text-decoration:none!important;font:600 11px/1.3 'Archivo',system-ui,sans-serif!important}
#bp .rima-v43-fav-row>.rima-v43-fav-heart,#bq .rima-v43-fav-row>.rima-v43-fav-heart,#bbq .rima-v43-fav-row>.rima-v43-fav-heart{display:grid!important;place-items:center!important;align-self:center!important;flex:0 0 38px!important;width:38px!important;min-width:38px!important;height:38px!important;min-height:38px!important;margin:0!important;padding:0!important;border:1px solid rgba(230,193,78,.35)!important;border-radius:50%!important;background:rgba(230,193,78,.08)!important;color:#d8d2c2!important;font-size:19px!important;cursor:pointer!important;touch-action:manipulation!important}
#bp .rima-v43-fav-row>.rima-v43-fav-heart.on,#bq .rima-v43-fav-row>.rima-v43-fav-heart.on,#bbq .rima-v43-fav-row>.rima-v43-fav-heart.on{color:#ffcb54!important;background:rgba(255,203,84,.16)!important;border-color:#ffcb54!important}
#bp .rima-v43-fav-row>.rima-v47-fav-download,#bq .rima-v43-fav-row>.rima-v47-fav-download,#bbq .rima-v43-fav-row>.rima-v47-fav-download{display:grid!important;place-items:center!important;flex:0 0 40px!important;width:40px!important;min-width:40px!important;height:40px!important;min-height:40px!important;align-self:center!important}
#bp>.bsl[hidden],#bq>.bsl[hidden],#bbq>.bsl[hidden],#bp>.catalog-attribution[hidden],#bq>.catalog-attribution[hidden],#bbq>.catalog-attribution[hidden]{display:none!important}
#bp .rima-v43-fav-row.is-selected,#bq .rima-v43-fav-row.is-selected,#bbq .rima-v43-fav-row.is-selected{background:linear-gradient(90deg,rgba(229,196,91,.08),transparent)!important;box-shadow:inset 3px 0 0 #e5c45b!important}
#bp .rima-v43-fav-play.is-selected,#bq .rima-v43-fav-play.is-selected,#bbq .rima-v43-fav-play.is-selected{border-color:rgba(239,207,106,.95)!important}
#bp .rima-v43-toggle .rima-v29-count,#bq .rima-v43-toggle .rima-v29-count,#bbq .rima-v43-toggle .rima-v29-count{font-weight:800!important}
@media(max-width:380px){
 #bp .rima-v43-fav-row,#bq .rima-v43-fav-row,#bbq .rima-v43-fav-row{gap:6px!important}
 #bp .rima-v43-fav-row>.rima-v43-fav-heart,#bq .rima-v43-fav-row>.rima-v43-fav-heart,#bbq .rima-v43-fav-row>.rima-v43-fav-heart{flex-basis:36px!important;width:36px!important;min-width:36px!important;height:36px!important;min-height:36px!important}
 #bp .rima-v43-fav-row>.rima-v47-fav-download,#bq .rima-v43-fav-row>.rima-v47-fav-download,#bbq .rima-v43-fav-row>.rima-v47-fav-download{flex-basis:36px!important;width:36px!important;min-width:36px!important;height:36px!important;min-height:36px!important}
}
/* Stage 2 has one bounded inner list instead of a full-height catalog card. */
@media(orientation:portrait) and (max-width:760px){
 #train-step-2 #bp>.bsl,#train-step-2 #bp>.rima-v43-favlist{height:auto!important;max-height:min(36vh,310px)!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-y!important}
 body.pl:not(.pv) #lv:not([hidden])>.card:not(.stage){display:flex!important;flex-direction:column!important;min-height:0!important;max-height:40vh!important;height:auto!important;overflow:visible!important;box-sizing:border-box!important}
 body.pl:not(.pv) #lv:not([hidden]) #bq{display:flex!important;flex:1 1 auto!important;flex-direction:column!important;min-height:0!important;width:100%!important;max-width:100%!important;overflow:visible!important}
 body.pl:not(.pv) #lv:not([hidden]) #bq>.bsl,body.pl:not(.pv) #lv:not([hidden]) #bq>.rima-v43-favlist{height:auto!important;max-height:min(28vh,235px)!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-y!important}
 body.pl:not(.pv) #lv:not([hidden]) #bq>.rima-v43-tools{flex:0 0 auto!important}
 body.pl:not(.pv) #lv:not([hidden]){padding-bottom:calc(260px + env(safe-area-inset-bottom,0px))!important}
 #bt #bbq>.bsl,#bt #bbq>.rima-v43-favlist{height:auto!important;max-height:min(36vh,310px)!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important}
}
#lv:not([hidden]) #stg.stage #cn:not(:empty){position:relative!important;transform:translateY(-7px)!important}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V54_FAIL: </body> ausente')
h=h[:pos]+css+'\n'+h[pos:]

player=r'''<script id="rimalab-player-state-settle-v54">
(function(){
 'use strict';
 const settle=()=>{const run=()=>{if(typeof window.rimaV51SyncPlayer==='function')window.rimaV51SyncPlayer()};requestAnimationFrame(run);setTimeout(run,60);setTimeout(run,220)};
 const saved=()=>{try{const a=JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]');return new Set(Array.isArray(a)?a.map(String):[])}catch(_){return new Set()}};
 function decorate(){
  const fav=saved();
  ['bp','bq','bbq'].forEach(id=>{
   const root=document.getElementById(id);if(!root)return;
   root.querySelectorAll('.bsl .bi').forEach(row=>{
    if(row.querySelector('[data-rima-fav]'))return;
    const play=row.querySelector('.beat-info .mc');if(!play)return;
    let key=play.getAttribute('data-rima-track-key')||'';
    if(!key){const m=String(play.getAttribute('onclick')||'').match(/zLP\((\d+),0,'([^']+)'\)/);if(m){const list=window.ZLIB&&window.ZLIB[m[2]]&&window.ZLIB[m[2]][1]||[];const item=list[Number(m[1])];if(item&&item[4]!=null)key='jm-'+String(item[4])}}
    if(!key||key==='jm-')return;
    play.setAttribute('data-rima-track-key',key);
    const heart=document.createElement('button');heart.type='button';heart.className='rima-v29-fav'+(fav.has(key)?' on':'');heart.setAttribute('data-rima-fav',key);heart.setAttribute('aria-pressed',String(fav.has(key)));heart.setAttribute('aria-label',fav.has(key)?'Remover dos favoritos':'Adicionar aos favoritos');heart.textContent=fav.has(key)?'♥':'♡';
    heart.addEventListener('click',ev=>{ev.preventDefault();ev.stopPropagation();if(typeof window.rimaV29ToggleFav==='function')window.rimaV29ToggleFav(key)});
    const dl=row.querySelector('.dlb');if(dl)dl.before(heart);else row.appendChild(heart);
   });
  });
 }
 function syncHearts(){
  const fav=saved();
  document.querySelectorAll('#bp [data-rima-fav],#bq [data-rima-fav],#bbq [data-rima-fav]').forEach(b=>{
   const k=b.getAttribute('data-rima-fav')||'',on=!!k&&fav.has(k);
   b.classList.toggle('on',on);b.setAttribute('aria-pressed',String(on));b.setAttribute('aria-label',on?'Remover dos favoritos':'Adicionar aos favoritos');
   if(b.classList.contains('rima-v29-fav'))b.textContent=on?'♥':'♡';
  });
  document.querySelectorAll('.rima-v29-count').forEach(e=>e.textContent=String(fav.size));
 }
 function refresh(){decorate();syncHearts();if(typeof window.rimaV45SyncSelection==='function')window.rimaV45SyncSelection()}
 function wrapToggle(){const old=window.rimaV29ToggleFav;if(typeof old!=='function'||old.__rimaV54)return;const f=function(){const r=old.apply(this,arguments);requestAnimationFrame(refresh);setTimeout(refresh,50);setTimeout(refresh,180);return r};f.__rimaV54=true;window.rimaV29ToggleFav=f}
 function wrap(name){const old=window[name];if(typeof old!=='function'||old.__rimaV54)return;const f=function(){const r=old.apply(this,arguments);if(name==='pk'){requestAnimationFrame(refresh);setTimeout(refresh,80);setTimeout(refresh,220)}settle();return r};f.__rimaV54=true;window[name]=f}
 wrapToggle();['zLP','zSetPL','zToggle','pk','zBarUI','rimaV41StartFavorites'].forEach(wrap);
 requestAnimationFrame(refresh);setTimeout(refresh,200);setTimeout(refresh,600);
 document.addEventListener('click',e=>{const b=e.target&&e.target.closest?e.target.closest('#pwb,#bp .bsl .bi .mc,#bq .bsl .bi .mc,#bbq .bsl .bi .mc,#bp [data-v43-play],#bq [data-v43-play],#bbq [data-v43-play]'):null;if(b)settle()},true);
 window.addEventListener('resize',settle,{passive:true});window.addEventListener('orientationchange',settle,{passive:true});settle();
})();
</script>'''
pos=h.lower().rfind('</body>');h=h[:pos]+player+'\n'+h[pos:]

m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='74': raise SystemExit('V54_FAIL: base versionCode != 74')
g=g[:m.start()]+re.sub('74','75',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.3.2': raise SystemExit('V54_FAIL: base versionName != 3.3.2')
g=g[:m.start()]+m.group(0).replace('3.3.2','3.3.3')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V54_OK: compact countdown, unified list/favorites across BP/BQ/BBQ, player gate re-sync, 3.3.3/code75')
