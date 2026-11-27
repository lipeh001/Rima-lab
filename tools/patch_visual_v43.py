#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V43_FAIL: missing app assets/Gradle')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-favorites-layout-runtime-v43' in h: raise SystemExit('V43_FAIL: already applied')
if 'rimalab-selector-favorites-sync-v42' not in h or 'rimalab-playlist-player-landscape-v41' not in h: raise SystemExit('V43_FAIL: expected V41/V42 runtimes missing')
if not all(f'id="{x}"' in h for x in ('bp','bq','pbar')): raise SystemExit('V43_FAIL: selectors/player missing')
css=r'''<style id="rimalab-favorites-layout-v43">
/* Favorites controls are full-width rows, never siblings of a beat card. */
#bp>.rima-v43-tools,#bq>.rima-v43-tools{display:flex!important;position:relative!important;box-sizing:border-box!important;clear:both!important;float:none!important;width:100%!important;max-width:100%!important;min-width:0!important;min-height:48px!important;align-items:stretch!important;justify-content:stretch!important;gap:0!important;margin:8px 0 12px!important;padding:0!important}
#bp>.rima-v43-tools button,#bq>.rima-v43-tools button{display:flex!important;position:relative!important;box-sizing:border-box!important;flex:1 1 100%!important;width:100%!important;max-width:none!important;min-width:0!important;min-height:48px!important;align-items:center!important;justify-content:center!important;gap:7px!important;margin:0!important;padding:9px 14px!important;border:1px solid rgba(229,196,91,.55)!important;border-radius:14px!important;background:rgba(220,190,80,.12)!important;color:#f0d77d!important;font-weight:800!important;font-size:16px!important;white-space:nowrap!important}
#bp>.rima-v43-tools button.active,#bq>.rima-v43-tools button.active{background:rgba(220,190,80,.22)!important;border-color:#e5c45b!important;box-shadow:0 0 0 1px rgba(229,196,91,.16),0 4px 14px rgba(229,196,91,.10)!important}
#bp>.rima-v43-favlist,#bq>.rima-v43-favlist{display:block!important;position:relative!important;box-sizing:border-box!important;clear:both!important;float:none!important;width:100%!important;max-width:100%!important;min-width:0!important;max-height:46vh!important;overflow-y:auto!important;overflow-x:hidden!important;padding:3px 3px 8px!important;margin:0 0 10px!important;border-radius:14px!important;overscroll-behavior:contain!important}
#bp>.rima-v43-favlist>.rima-v43-empty,#bq>.rima-v43-favlist>.rima-v43-empty{display:block!important;width:100%!important;box-sizing:border-box!important;padding:15px!important;text-align:center!important}
#bp .rima-v43-fav-row,#bq .rima-v43-fav-row{display:grid!important;grid-template-columns:minmax(0,1fr) 46px!important;align-items:center!important;gap:9px!important;width:100%!important;min-width:0!important;box-sizing:border-box!important;margin:0 0 8px!important;padding:8px!important;border:1px solid rgba(150,140,180,.22)!important;border-radius:15px!important;background:rgba(255,255,255,.025)!important}
#bp .rima-v43-fav-info,#bq .rima-v43-fav-info{display:block!important;min-width:0!important;width:100%!important;max-width:100%!important}
#bp .rima-v43-fav-play,#bq .rima-v43-fav-play{display:flex!important;position:relative!important;box-sizing:border-box!important;align-items:center!important;justify-content:flex-start!important;width:100%!important;min-width:0!important;max-width:100%!important;min-height:52px!important;height:auto!important;margin:0!important;padding:9px 11px!important;border:1px solid rgba(150,140,180,.24)!important;border-radius:11px!important;background:rgba(20,19,27,.7)!important;color:#f2e6ad!important;text-align:left!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important;line-height:1.25!important;font-size:14px!important;cursor:pointer!important;pointer-events:auto!important}
#bp .rima-v43-fav-play b,#bq .rima-v43-fav-play b{display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;overflow:hidden!important;font-weight:800!important}
#bp .rima-v43-fav-meta,#bq .rima-v43-fav-meta{display:block!important;padding:5px 3px 0!important;color:var(--muted,#aaa)!important;font-size:12px!important;line-height:1.2!important}
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart{display:grid!important;position:relative!important;place-items:center!important;box-sizing:border-box!important;flex:none!important;width:44px!important;min-width:44px!important;max-width:44px!important;height:44px!important;min-height:44px!important;max-height:44px!important;margin:0!important;padding:0!important;border:1px solid rgba(230,193,78,.55)!important;border-radius:50%!important;background:rgba(230,193,78,.13)!important;color:#e8c45c!important;font-size:21px!important;line-height:1!important;cursor:pointer!important;pointer-events:auto!important}
#bp .rima-v43-fav-heart[aria-pressed="true"],#bq .rima-v43-fav-heart[aria-pressed="true"]{background:rgba(230,193,78,.22)!important;color:#ffdb72!important;box-shadow:0 0 0 1px rgba(230,193,78,.12)!important}
#bp .bsl[hidden],#bq .bsl[hidden]{display:none!important}
#bq .bc{box-sizing:border-box!important;max-width:100%!important}
@media(max-width:380px){
 #bp .rima-v43-fav-row,#bq .rima-v43-fav-row{grid-template-columns:minmax(0,1fr) 42px!important;gap:7px!important;padding:6px!important}
 #bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart{width:40px!important;min-width:40px!important;max-width:40px!important;height:40px!important;min-height:40px!important;max-height:40px!important}
}
</style>'''
js=r'''<script id="rimalab-favorites-layout-runtime-v43">
(function(){
 'use strict';
 const KEY='rimalab_favorites_v29',ids=['bp','bq'];
 let showing=false,activeRoot='bp',busy=false;
 const $=s=>document.querySelector(s),esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const catalog=()=>window.ZLIB||{};
 const allTracks=()=>Object.keys(catalog()).flatMap(cat=>(catalog()[cat]&&catalog()[cat][1]||[]).map((x,i)=>({cat,x,i,key:'jm-'+String(x[4])})).filter(t=>t.key!=='jm-'));
 const read=()=>{try{const a=JSON.parse(localStorage.getItem(KEY)||'[]');return Array.isArray(a)?[...new Set(a.map(String).filter(Boolean))]:[]}catch(_){return[]}};
 function count(){return read().length}
 function ensureToolbar(root){
  let bar=root.querySelector(':scope > .rima-v43-tools');
  if(!bar){
   const old=root.querySelector(':scope > .rima-v29-tools');
   if(old){old.classList.remove('rima-v29-tools');old.classList.add('rima-v43-tools');bar=old}
  }
  if(!bar){bar=document.createElement('div');bar.className='rima-v43-tools';root.insertBefore(bar,root.firstChild)}
  // Isolate from V40/V42 legacy handlers; the V43 controller owns both selectors.
  bar.className='rima-v43-tools';
  let b=bar.querySelector('button');
  if(!b){b=document.createElement('button');bar.appendChild(b)}
  b.type='button';b.className='rima-v43-toggle';b.removeAttribute('onclick');
  b.innerHTML='♥ Favoritos <span class="rima-v29-count">'+count()+'</span>';
  b.classList.toggle('active',showing);b.setAttribute('aria-pressed',String(showing));
  return bar;
 }
 function favoriteMarkup(){
  const saved=new Set(read()),items=allTracks().filter(t=>saved.has(t.key));
  if(!items.length)return '<div class="rima-v43-favlist"><div class="rima-v43-empty rima-v29-note">Nenhum beat favoritado ainda. Toque no coração de um beat ou no coração do player para adicioná-lo.</div></div>';
  return '<div class="rima-v43-favlist" aria-label="Seus beats favoritos">'+items.map(t=>
   '<div class="rima-v43-fav-row" data-key="'+esc(t.key)+'"><div class="rima-v43-fav-info"><button class="rima-v43-fav-play" type="button" data-v43-play="'+esc(t.key)+'" aria-label="Ouvir '+esc(t.x[1])+'"><b>'+esc(t.x[1])+'</b></button><span class="rima-v43-fav-meta">'+esc(t.cat)+'</span></div><button class="rima-v43-fav-heart" type="button" data-v43-heart="'+esc(t.key)+'" aria-label="Remover dos favoritos" aria-pressed="true">♥</button></div>'
  ).join('')+'</div>';
 }
 function removeView(root){const v=root.querySelector(':scope > .rima-v43-favlist');if(v)v.remove()}
 function renderRoot(root){
  const id=root.id,bar=ensureToolbar(root);removeView(root);
  if(id==='bp'){
   root.querySelectorAll(':scope > .bsl').forEach(e=>{if(!e.classList.contains('rima-v43-favlist'))e.hidden=showing});
   root.querySelectorAll(':scope > .catalog-attribution').forEach(e=>e.hidden=showing);
   root.querySelectorAll('.row .tag.chip').forEach(b=>{if(showing){b.classList.remove('on');b.setAttribute('aria-pressed','false')}});
   if(showing)bar.insertAdjacentHTML('afterend',favoriteMarkup());
  }else{
   // #bq is rebuilt by pk() during training. Keep its native beat buttons intact
   // while browsing normally, and swap only its contents while Favorites is open.
   if(showing){
    root.querySelectorAll('.bc').forEach(e=>e.hidden=true);
    bar.insertAdjacentHTML('afterend',favoriteMarkup());
   }else root.querySelectorAll('.bc').forEach(e=>e.hidden=false);
  }
 }
 function render(){ids.forEach(id=>{const r=document.getElementById(id);if(r)renderRoot(r)})}
 function setMode(v,root){showing=!!v;if(root)activeRoot=root;render()}
 function sync(){document.querySelectorAll('.rima-v29-count').forEach(e=>e.textContent=String(count()));if(showing)render()}
 function play(k){
  const key=String(k||'');if(!allTracks().some(t=>t.key===key))return;
  const start=window.rimaV41StartFavorites||window.rimaV29PlayFav;
  if(typeof start==='function')start(key);
  else {const t=allTracks().find(t=>t.key===key);if(t&&typeof window.zLP==='function')window.zLP(t.i,0,t.cat)}
 }
 function toggleFavorite(k){
  const key=String(k||'');if(!key)return;
  if(typeof window.rimaV29ToggleFav==='function')window.rimaV29ToggleFav(key);
  else{
   const old=read(),next=old.includes(key)?old.filter(x=>x!==key):old.concat(key);
   try{localStorage.setItem(KEY,JSON.stringify(next))}catch(_){}
  }
  sync();
 }
 document.addEventListener('click',e=>{
  const b=e.target&&e.target.closest?e.target.closest('#bp .rima-v43-toggle,#bq .rima-v43-toggle'):null;
  if(!b)return;e.preventDefault();e.stopImmediatePropagation();setMode(!showing,b.closest('#bp,#bq').id);
 },true);
 document.addEventListener('click',e=>{
  const b=e.target&&e.target.closest?e.target.closest('#bp [data-v43-play],#bq [data-v43-play]'):null;
  if(!b)return;e.preventDefault();e.stopImmediatePropagation();play(b.getAttribute('data-v43-play'));
 },true);
 document.addEventListener('click',e=>{
  const b=e.target&&e.target.closest?e.target.closest('#bp [data-v43-heart],#bq [data-v43-heart]'):null;
  if(!b)return;e.preventDefault();e.stopImmediatePropagation();toggleFavorite(b.getAttribute('data-v43-heart'));
 },true);
 document.addEventListener('click',e=>{
  const chip=e.target&&e.target.closest?e.target.closest('#bp .row .tag.chip'):null;
  if(chip&&showing)setMode(false,'bp');
 },true);
 document.addEventListener('click',e=>{
  if(e.target&&e.target.closest&&e.target.closest('#bp [data-rima-fav],#rima-v29-player-heart'))setTimeout(sync,0);
 });
 window.addEventListener('storage',e=>{if(e.key===KEY)sync()});
 const oldPk=window.pk;
 if(typeof oldPk==='function'&&!oldPk.__rimaV43){
  const f=function(){const r=oldPk.apply(this,arguments);render();return r};
  f.__rimaV43=true;window.pk=f;
 }
 const oldBar=window.zBarUI;
 if(typeof oldBar==='function'&&!oldBar.__rimaV43){
  const f=function(){const r=oldBar.apply(this,arguments);render();return r};
  f.__rimaV43=true;window.zBarUI=f;
 }
 function ready(){render()}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
 window.rimaV43ShowFavorites=v=>setMode(v==null?!showing:!!v,activeRoot);
})();
</script>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V43_FAIL: body close missing')
h=h[:pos]+css+'\n'+js+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='62': raise SystemExit('V43_FAIL: expected versionCode 62')
g=g[:m.start()]+re.sub('62','63',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.2.0': raise SystemExit('V43_FAIL: expected versionName 3.2.0')
g=g[:m.start()]+m.group(0).replace('3.2.0','3.2.1')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V43_OK: rebuilt Favorites layout; shared toggle in #bp and live #bq; reliable add/remove/play; 3.2.1/code63')
