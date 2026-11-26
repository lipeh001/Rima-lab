#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1]).resolve()
html_path = root / 'app/src/main/assets/rima-lab.html'
gradle_path = next((p for p in (root / 'app/build.gradle', root / 'app/build.gradle.kts') if p.exists()), None)
if not html_path.is_file() or gradle_path is None:
    raise SystemExit('V42_FAIL: HTML or Gradle file missing')

html = html_path.read_text(encoding='utf-8')
gradle = gradle_path.read_text(encoding='utf-8')
if 'rimalab-selector-favorites-sync-v42' in html or 'rimalab-landscape-player-dock-v42' in html:
    raise SystemExit('V42_FAIL: patch already applied')
if 'rimalab-playlist-player-landscape-v41' not in html:
    raise SystemExit('V42_FAIL: v41 playlist runtime missing')
if 'id="bp"' not in html or 'id="bq"' not in html or 'id="pbar"' not in html:
    raise SystemExit('V42_FAIL: expected selectors/player missing')

css = r'''<style id="rimalab-landscape-player-dock-v42">
/* Both selectors share Favorites controls, selected state and touch targets. */
#bp .rima-v29-tools,#bq .rima-v29-tools{display:flex!important;justify-content:center!important;align-items:center!important;margin:4px 0 6px!important;gap:6px!important}
#bp .rima-v29-tools button,#bq .rima-v29-tools button{flex:0 1 270px!important;max-width:100%!important;min-height:38px!important;padding:7px 10px!important}
#bp .rima-v29-tools button.active,#bq .rima-v29-tools button.active{background:rgba(220,190,80,.24)!important;border-color:#e5c45b!important;color:#fff1b5!important;box-shadow:0 0 0 1px rgba(229,196,91,.16),0 4px 14px rgba(229,196,91,.10)!important}
#bp .rima-v42-favlist,#bq .rima-v42-favlist{display:grid!important;gap:6px!important;margin:4px 0 8px!important}
#bp .rima-v42-favlist .bi,#bq .rima-v42-favlist .bi{display:flex!important;align-items:center!important;gap:8px!important;padding:4px 0!important;margin:0!important}
#bp .rima-v42-favlist .beat-info,#bq .rima-v42-favlist .beat-info{flex:1 1 auto!important;min-width:0!important}
#bp .rima-v42-favlist .rima-v42-fav-play,#bq .rima-v42-favlist .rima-v42-fav-play{width:100%!important;min-height:44px!important;text-align:left!important;cursor:pointer!important;pointer-events:auto!important}
#bp .rima-v42-favlist .rima-v42-fav-heart,#bq .rima-v42-favlist .rima-v42-fav-heart{display:grid!important;place-items:center!important;flex:0 0 40px!important;width:40px!important;height:40px!important;border-radius:50%!important;border:1px solid rgba(230,193,78,.45)!important;background:rgba(230,193,78,.13)!important;color:#e8c45c!important;cursor:pointer!important}
/* Landscape: compact stage on the left and scrollable beat list on the right. */
@media(orientation:landscape) and (max-height:900px),(max-height:700px) and (min-width:500px){
 main{width:100%!important;max-width:none!important;padding:6px 8px 82px!important;box-sizing:border-box!important}
 #lv:not([hidden]){display:grid!important;width:100%!important;box-sizing:border-box!important;grid-template-columns:minmax(0,1.42fr) minmax(0,1fr)!important;grid-template-rows:40px minmax(0,1fr) 40px!important;gap:6px 10px!important;align-items:stretch!important;height:clamp(245px,calc(100svh - 200px),295px)!important;min-height:245px!important;max-height:295px!important;padding:0 0 4px!important;margin:0!important}
 #lv:not([hidden])>.bk{grid-column:2!important;grid-row:1!important;align-self:stretch!important;width:100%!important;min-height:38px!important;height:40px!important;margin:0!important;padding:6px 10px!important}
 #lv:not([hidden])>#stg.stage{grid-column:1!important;grid-row:1/4!important;align-self:stretch!important;width:100%!important;height:100%!important;min-height:0!important;max-height:none!important;margin:0!important;box-sizing:border-box!important;overflow:hidden!important;padding:8px 10px!important;gap:0!important}
 #lv:not([hidden])>#stg.stage #ck{margin:0 0 3px!important;font-size:clamp(10px,1.1vw,13px)!important;line-height:1.15!important}
 #lv:not([hidden])>#stg.stage #cb{min-height:clamp(66px,15svh,88px)!important;height:auto!important;margin:0 auto 2px!important;padding:2px 4px!important;line-height:1.02!important;max-width:100%!important;box-sizing:border-box!important}
 #lv:not([hidden])>#stg.stage #rm{gap:4px!important;margin:2px auto 4px!important;padding:0 2px!important}
 #lv:not([hidden])>#stg.stage #rm>*{max-width:24%!important;padding:3px 5px!important;font-size:clamp(9px,1.15vw,12px)!important;line-height:1.08!important}
 #lv:not([hidden])>#stg.stage #sg{min-height:5px!important;margin:3px 0 1px!important}
 #lv:not([hidden])>#stg.stage #cs{margin:3px auto 0!important;font-size:clamp(10px,1.2vw,13px)!important;line-height:1.15!important}
 #lv:not([hidden])>#stg.stage #cn{margin:3px auto 0!important;font-size:clamp(10px,1.15vw,12px)!important;line-height:1.15!important}
 #lv:not([hidden])>#stg.stage .v3bar{margin:4px auto 0!important;min-height:34px!important;padding:0!important}
 #lv:not([hidden])>#stg.stage .v3bar button{min-height:32px!important;padding:5px 11px!important;font-size:11px!important}
 #lv:not([hidden])>.card:not(.stage){grid-column:2!important;grid-row:2!important;align-self:stretch!important;min-width:0!important;min-height:0!important;height:100%!important;max-height:none!important;margin:0!important;padding:7px 8px!important;box-sizing:border-box!important;overflow-y:auto!important;overscroll-behavior:contain!important}
 #lv:not([hidden])>.btn.w{grid-column:2!important;grid-row:3!important;align-self:stretch!important;width:100%!important;min-height:38px!important;height:40px!important;margin:0!important;padding:6px 10px!important}
 #lv:not([hidden]) #bq{min-width:0!important;margin:0!important}
 #lv:not([hidden]) #bq .rima-v29-tools{margin:4px auto 6px!important}
 #lv:not([hidden]) #bq .bsl{margin:3px 0!important}
 #lv:not([hidden]) #bq .bi{padding:4px 0!important}
 /* Dock player at bottom edge; preserve −10s/+10s and seek bar. */
 #pbar{position:fixed!important;inset:auto 8px 5px 8px!important;top:auto!important;bottom:5px!important;left:8px!important;right:8px!important;transform:none!important;width:auto!important;max-width:none!important;height:70px!important;min-height:70px!important;max-height:70px!important;display:flex!important;flex-direction:column!important;align-items:stretch!important;justify-content:flex-start!important;gap:0!important;margin:0!important;padding:4px 8px 3px!important;overflow:visible!important;z-index:12000!important;border-radius:14px!important;box-sizing:border-box!important}
 #pbar .pwrow{display:flex!important;flex:0 0 36px!important;height:36px!important;min-height:36px!important;gap:5px!important}
 #pbar .pw-art{display:none!important}
 #pbar .pw-controls{display:flex!important;flex:0 0 auto!important;align-items:center!important;gap:2px!important}
 #pbar .pw-controls button{width:27px!important;height:29px!important}
 #pbar .pw-controls #pwb{width:33px!important;height:33px!important}
 #pbar .pwi{display:block!important;flex:1 1 auto!important;min-width:0!important;overflow:hidden!important}
 #pbar #pwn{display:block!important;max-width:100%!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;font-size:clamp(10px,1.2vw,13px)!important}
 #pbar #pws{display:block!important;font-size:9px!important;line-height:1.1!important}
 #pbar button.pws,#pbar #rima-v29-player-heart{display:grid!important;width:27px!important;height:27px!important;flex:0 0 27px!important}
 #pbar .pwinfo{display:flex!important;position:absolute!important;right:10px!important;top:29px!important;bottom:auto!important;height:9px!important;min-height:9px!important;margin:0!important;font-size:8px!important}
 #pbar .pwscr{display:flex!important;visibility:visible!important;position:relative!important;inset:auto!important;flex:0 0 25px!important;align-items:center!important;gap:7px!important;width:100%!important;height:25px!important;min-height:25px!important;margin:0!important;padding:0 1px!important;z-index:10!important}
 #pbar .pwscr .pwm{display:grid!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;width:40px!important;min-width:40px!important;height:22px!important;flex:0 0 40px!important;font-size:9px!important}
 #pbar .pwscr .pwp{display:block!important;visibility:visible!important;position:relative!important;flex:1 1 auto!important;min-width:20px!important;width:auto!important;height:5px!important;min-height:5px!important;margin:0!important}
 body.pl main,body.pl #lv:not([hidden]){padding-bottom:78px!important}
}
@media(orientation:landscape) and (max-height:380px),(max-height:380px) and (min-width:500px){
 #lv:not([hidden]){height:245px!important;min-height:245px!important}
 #lv:not([hidden])>#stg.stage{padding:5px 7px!important}
 #lv:not([hidden])>#stg.stage #cb{min-height:58px!important}
 #pbar{height:66px!important;min-height:66px!important;max-height:66px!important;padding:3px 7px 2px!important}
 #pbar .pwrow{flex-basis:34px!important;height:34px!important;min-height:34px!important}
 #pbar .pwscr{flex-basis:24px!important;min-height:24px!important}
}
</style>'''

runtime = r'''<script id="rimalab-selector-favorites-sync-v42">
(function(){
 'use strict';
 const KEY='rimalab_favorites_v29';
 let favoritesMode=false,activeSelector='bp';
 const $=s=>document.querySelector(s);
 const roots=()=>['bp','bq'].map(id=>document.getElementById(id)).filter(Boolean);
 const catalog=()=>typeof ZLIB!=='undefined'&&ZLIB?ZLIB:{};
 const norm=k=>{k=String(k||'');return k.startsWith('jm-')?k:'jm-'+k};
 const tracks=()=>Object.keys(catalog()).flatMap(cat=>(catalog()[cat]&&catalog()[cat][1]||[]).map((x,i)=>({cat,x,i,key:x&&x[4]!=null?'jm-'+String(x[4]):''})).filter(t=>t.key));
 const favorites=()=>{try{const raw=JSON.parse(localStorage.getItem(KEY)||'[]');const list=Array.isArray(raw)?Array.from(new Set(raw.filter(Boolean).map(norm))):[];if(JSON.stringify(raw)!==JSON.stringify(list))localStorage.setItem(KEY,JSON.stringify(list));return list}catch(_){return[]}};
 const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function toolbar(root){
  const bar=root.querySelector('.rima-v29-tools');if(!bar)return null;
  Array.from(bar.querySelectorAll('button')).forEach(b=>{if((b.textContent||'').toLowerCase().includes('beat aleatório'))b.remove()});
  const b=Array.from(bar.querySelectorAll('button')).find(x=>(x.textContent||'').toLowerCase().includes('favoritos'));
  if(!b)return null;
  b.type='button';b.classList.add('rima-v42-favorites-toggle');b.removeAttribute('onclick');
  b.innerHTML='♥ Favoritos <span class="rima-v29-count">'+favorites().length+'</span>';
  b.classList.toggle('active',favoritesMode);b.setAttribute('aria-pressed',String(favoritesMode));
  return b;
 }
 function restoreCategoryChips(root){
  const selected=String(typeof ZS!=='undefined'&&ZS&&ZS.s||'');
  root.querySelectorAll('.row .tag.chip').forEach(b=>{
   const text=(b.textContent||'').trim().toLowerCase(),on=!!selected&&text.startsWith(selected.toLowerCase());
   b.classList.toggle('on',on);b.setAttribute('aria-pressed',String(on));
  });
 }
 function favoriteMarkup(){
  const saved=favorites(),list=tracks().filter(t=>saved.includes(t.key));
  if(!list.length)return '<div class="bsl rima-v42-favlist"><p class="mut">Nenhum beat favoritado ainda. Use o coração ao lado de um beat para guardá-lo aqui.</p></div>';
  return '<div class="bsl rima-v42-favlist" aria-label="Seus beats favoritos">'+list.map(({cat,x,key})=>
   '<div class="bi"><div class="beat-info"><button class="mc rima-v42-fav-play" type="button" data-rima-v42-play="'+esc(key)+'" aria-label="Ouvir '+esc(x[1])+'"><b>'+esc(x[1])+'</b></button><div class="beat-meta">'+esc(cat)+'</div></div><button class="rima-v42-fav-heart" type="button" data-rima-v42-heart="'+esc(key)+'" aria-label="Remover dos favoritos" aria-pressed="true">♥</button></div>'
  ).join('')+'</div>';
 }
 function renderRoot(root){
  const bar=toolbar(root);if(!bar)return;
  const old=root.querySelector('.rima-v42-favlist');if(old)old.remove();
  root.querySelectorAll('.bsl:not(.rima-v42-favlist)').forEach(e=>{e.hidden=favoritesMode});
  root.querySelectorAll('.catalog-attribution').forEach(e=>{e.hidden=favoritesMode});
  if(favoritesMode){
   root.querySelectorAll('.row .tag.chip').forEach(b=>{b.classList.remove('on');b.setAttribute('aria-pressed','false')});
   const wrap=document.createElement('div');wrap.innerHTML=favoriteMarkup();
   const view=wrap.firstElementChild;if(view)bar.insertAdjacentElement('afterend',view);
  }else{
   root.querySelectorAll('.bsl:not(.rima-v42-favlist)').forEach(e=>{e.hidden=false});
   restoreCategoryChips(root);
  }
 }
 function renderAll(){roots().forEach(renderRoot)}
 function setMode(on,selector){favoritesMode=!!on;if(selector)activeSelector=selector;renderAll()}
 function closeForCategory(){if(!favoritesMode)return;favoritesMode=false;renderAll()}
 function playFavorite(k){
  const key=norm(k);
  if(typeof window.rimaV41StartFavorites==='function'){window.rimaV41StartFavorites(key);return}
  const item=tracks().find(t=>t.key===key);if(!item)return;
  const list=catalog()[item.cat]&&catalog()[item.cat][1]||[],i=list.findIndex(x=>'jm-'+String(x[4])===key);
  if(i>=0&&typeof window.zLP==='function')window.zLP(i,0,item.cat);
 }
 function updateFavorites(){renderAll()}
 document.addEventListener('click',e=>{
  const t=e.target&&e.target.closest?e.target.closest('#bp .rima-v42-favorites-toggle,#bq .rima-v42-favorites-toggle'):null;
  if(!t)return;
  const root=t.closest('#bp,#bq');e.preventDefault();e.stopImmediatePropagation();
  setMode(!favoritesMode,root&&root.id||'bp');
 },true);
 document.addEventListener('click',e=>{
  const chip=e.target&&e.target.closest?e.target.closest('#bp .row .tag.chip,#bq .row .tag.chip'):null;
  if(chip)closeForCategory();
 },true);
 document.addEventListener('click',e=>{
  const b=e.target&&e.target.closest?e.target.closest('[data-rima-v42-play]'):null;
  if(!b)return;e.preventDefault();e.stopImmediatePropagation();
  const key=b.getAttribute('data-rima-v42-play');
  setMode(true,b.closest('#bp,#bq')?.id||activeSelector);playFavorite(key);
 },true);
 document.addEventListener('click',e=>{
  const b=e.target&&e.target.closest?e.target.closest('[data-rima-v42-heart]'):null;
  if(!b)return;e.preventDefault();e.stopImmediatePropagation();
  const k=norm(b.getAttribute('data-rima-v42-heart'));
  if(typeof window.rimaV29ToggleFav==='function')window.rimaV29ToggleFav(k);
  else{const next=favorites().filter(x=>x!==k);try{localStorage.setItem(KEY,JSON.stringify(next))}catch(_){}}
  updateFavorites();
 },true);
 window.addEventListener('storage',e=>{if(e.key===KEY)updateFavorites()});
 const oldPk=window.pk;
 if(typeof oldPk==='function'&&!oldPk.__rimaV42){
  const wrapped=function(){const result=oldPk.apply(this,arguments);renderAll();setTimeout(renderAll,60);return result};
  wrapped.__rimaV42=true;window.pk=wrapped;
 }
 const oldToggle=window.rimaV29ToggleFav;
 if(typeof oldToggle==='function'&&!oldToggle.__rimaV42){
  const wrapped=function(){const result=oldToggle.apply(this,arguments);setTimeout(updateFavorites,0);return result};
  wrapped.__rimaV42=true;window.rimaV29ToggleFav=wrapped;
 }
 window.rimaV42ShowFavorites=on=>setMode(on==null?!favoritesMode:!!on,activeSelector);
 window.rimaV29ShowFavorites=()=>setMode(!favoritesMode,activeSelector);
 function dockPlayer(){
  const bar=$('#pbar');if(!bar)return;
  const landscape=(window.matchMedia&&window.matchMedia('(orientation:landscape)').matches)||window.innerWidth>window.innerHeight;
  if(!landscape)return;
  const set=(k,v)=>bar.style.setProperty(k,v,'important');
  set('position','fixed');set('top','auto');set('bottom','5px');
  set('left','8px');set('right','8px');set('transform','none');set('z-index','12000');
  set('height','70px');set('min-height','70px');set('max-height','70px');
  // Do not override V36 on-demand hiding: only display it when its visibility flag is set.
  if(document.body.classList.contains('rima-player-visible'))set('display','flex');
 }
 function ready(){renderAll();dockPlayer()}
 const oldBar=window.zBarUI;
 if(typeof oldBar==='function'&&!oldBar.__rimaV42){
  const wrapped=function(){const result=oldBar.apply(this,arguments);setTimeout(ready,60);return result};
  wrapped.__rimaV42=true;window.zBarUI=wrapped;
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
 window.addEventListener('resize',dockPlayer,{passive:true});
 window.addEventListener('orientationchange',()=>setTimeout(dockPlayer,120),{passive:true});
 if(window.visualViewport)window.visualViewport.addEventListener('resize',dockPlayer,{passive:true});
})();
</script>'''

body_pos = html.lower().rfind('</body>')
if body_pos < 0:
    raise SystemExit('V42_FAIL: </body> missing')
html = html[:body_pos] + css + '\n' + runtime + '\n' + html[body_pos:]

m = re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)', gradle)
if not m or (m.group(1) or m.group(2)) != '61':
    raise SystemExit('V42_FAIL: expected versionCode 61')
gradle = gradle[:m.start()] + re.sub(r'61', '62', m.group(0), count=1) + gradle[m.end():]
name = re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]", gradle)
if not name or (name.group(1) or name.group(2)) != '3.1.9':
    raise SystemExit('V42_FAIL: expected versionName 3.1.9')
gradle = gradle[:name.start()] + name.group(0).replace('3.1.9', '3.2.0') + gradle[name.end():]
html_path.write_text(html, encoding='utf-8')
gradle_path.write_text(gradle, encoding='utf-8')
print('V42_OK: shared favorites selectors, clickable Favorites queue, bottom landscape player, compact stage; 3.2.0 / code 62')
