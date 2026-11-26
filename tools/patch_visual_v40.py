#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
if 'rimalab-favorites-and-stage-v40' in h: raise SystemExit('V40_FAIL: already applied')

# Replace the v35 favorites adapter. The old version looked up window.ZLIB/window.ZS,
# but the app declares ZLIB and ZS as top-level const bindings, not window properties.
fav=r"""<script id="rimalab-favorites-and-stage-v40">
(function(){
 'use strict';
 const $=s=>document.querySelector(s),$$=s=>Array.from(document.querySelectorAll(s));
 const KEY='rimalab_favorites_v29';
 let favoritesMode=false,renderQueued=false;
 const catalog=()=>typeof ZLIB!=='undefined'&&ZLIB?ZLIB:{};
 const playerState=()=>typeof ZS!=='undefined'&&ZS?ZS:null;
 const keyOf=x=>x&&x[4]!=null?'jm-'+String(x[4]):'';
 const allTracks=()=>Object.keys(catalog()).flatMap(cat=>(catalog()[cat]&&catalog()[cat][1]||[]).map(x=>({cat,x,key:keyOf(x)})));
 const normalize=k=>{k=String(k||'');return k.startsWith('jm-')?k:'jm-'+k};
 function readFav(){
  try{
   const raw=JSON.parse(localStorage.getItem(KEY)||'[]');
   const list=Array.isArray(raw)?Array.from(new Set(raw.filter(Boolean).map(normalize))):[];
   if(JSON.stringify(raw)!==JSON.stringify(list))localStorage.setItem(KEY,JSON.stringify(list));
   return list;
  }catch(_){return[]}
 }
 const escapeHTML=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function currentKey(){const s=playerState();return s&&s.key?String(s.key):''}
 function sync(){
  const fav=readFav(),key=currentKey(),on=!!key&&fav.includes(normalize(key));
  const p=$('#rima-v29-player-heart');
  if(p){p.textContent=on?'♥':'♡';p.classList.toggle('on',on);p.setAttribute('aria-pressed',String(on));p.setAttribute('aria-label',on?'Remover dos favoritos':'Adicionar aos favoritos')}
  $$('[data-rima-fav]').forEach(b=>{
   const yes=fav.includes(normalize(b.getAttribute('data-rima-fav')||''));
   b.classList.toggle('on',yes);b.classList.toggle('rima-v40-fav-on',yes);
   b.textContent=yes?'♥':'♡';b.setAttribute('aria-pressed',String(yes));
  });
  $$('.rima-v29-count').forEach(e=>e.textContent=String(fav.length));
  const tool=$('#bp .rima-v29-tools button');
  if(tool){tool.innerHTML='♥ Favoritos <span class="rima-v29-count">'+fav.length+'</span>';tool.classList.toggle('active',favoritesMode);tool.setAttribute('aria-pressed',String(favoritesMode))}
 }
 function removeFavoritesView(){
  const bp=$('#bp');if(!bp)return;
  const view=bp.querySelector('.rima-v40-favlist');if(view)view.remove();
  bp.querySelectorAll('.bsl:not(.rima-v40-favlist)').forEach(e=>e.hidden=false);
  const attr=bp.querySelector('.catalog-attribution');if(attr)attr.hidden=false;
  favoritesMode=false;sync();
 }
 function favoriteMarkup(){
  const fav=readFav(),tracks=allTracks().filter(o=>fav.includes(o.key));
  if(!tracks.length)return '<div class="bsl rima-v40-favlist"><p class="rima-v29-note">Nenhum beat favoritado ainda. Use o coração ao lado de um beat ou no player para guardá-lo aqui.</p></div>';
  return '<div class="bsl rima-v40-favlist" aria-label="Seus beats favoritos">'+tracks.map(({cat,x,key})=>
   '<div class="bi"><div class="beat-info"><button class="mc rima-v40-play" type="button" data-rima-play="'+escapeHTML(key)+'"><b>'+escapeHTML(x[1])+'</b></button><div class="beat-meta">'+escapeHTML(cat)+'</div></div><button class="rima-v40-fav-toggle rima-v29-fav on" type="button" data-rima-fav="'+escapeHTML(key)+'" aria-pressed="true" aria-label="Remover dos favoritos">♥</button></div>'
  ).join('')+'</div>';
 }
 function renderFavorites(){
  const bp=$('#bp');if(!bp)return;
  const tools=bp.querySelector('.rima-v29-tools');
  const row=Array.from(bp.querySelectorAll('.row')).find(e=>e.querySelectorAll('.tag.chip').length>=3);
  if(!tools||!row)return;
  let view=bp.querySelector('.rima-v40-favlist');
  if(!favoritesMode){if(view)view.remove();bp.querySelectorAll('.bsl:not(.rima-v40-favlist)').forEach(e=>e.hidden=false);const a=bp.querySelector('.catalog-attribution');if(a)a.hidden=false;sync();return}
  bp.querySelectorAll('.bsl:not(.rima-v40-favlist)').forEach(e=>e.hidden=true);
  const attr=bp.querySelector('.catalog-attribution');if(attr)attr.hidden=true;
  if(view)view.remove();
  const wrap=document.createElement('div');wrap.innerHTML=favoriteMarkup();view=wrap.firstElementChild;
  if(view)tools.insertAdjacentElement('afterend',view);
  sync();
 }
 function toggleView(){favoritesMode=!favoritesMode;renderFavorites()}
 window.rimaV29ShowFavorites=toggleView;
 function toggleFav(k){
  k=normalize(k);if(!k||k==='jm-')return;
  if(typeof window.rimaV29ToggleFav==='function')window.rimaV29ToggleFav(k);
  else{
   const fav=readFav(),next=fav.includes(k)?fav.filter(x=>x!==k):fav.concat(k);
   try{localStorage.setItem(KEY,JSON.stringify(next))}catch(_){}
  }
  requestAnimationFrame(()=>{if(favoritesMode)renderFavorites();else sync()});
 }
 function playFavorite(k){
  const tracks=allTracks(),o=tracks.find(t=>t.key===normalize(k));if(!o)return;
  const c=catalog(),list=c[o.cat]&&c[o.cat][1]||[],i=list.findIndex(x=>keyOf(x)===o.key);
  if(i<0)return;
  if(typeof window.rimaV29PlayFav==='function')window.rimaV29PlayFav(o.key);
  else if(typeof window.zLP==='function')zLP(i,0,o.cat);
 }
 function bindPlayer(){
  const p=$('#rima-v29-player-heart');if(!p)return;
  p.type='button';p.onclick=e=>{
   e.preventDefault();e.stopPropagation();
   const k=currentKey();if(k)toggleFav(k);
  };
 }
 function wireTools(){
  const b=$('#bp .rima-v29-tools button');if(b){b.setAttribute('type','button');b.setAttribute('aria-label','Mostrar favoritos');b.innerHTML='♥ Favoritos <span class="rima-v29-count">'+readFav().length+'</span>';b.classList.toggle('active',favoritesMode);b.setAttribute('aria-pressed',String(favoritesMode))}
 }
 function scheduleRender(){if(renderQueued)return;renderQueued=true;requestAnimationFrame(()=>{renderQueued=false;wireTools();bindPlayer();if(favoritesMode)renderFavorites();else sync()})}
 // Capture category taps BEFORE zLS() redraws #bp. This closes Favorites and lets
 // the category's original inline handler (Boom bap / Trap / Drill) execute normally.
 document.addEventListener('click',e=>{
  const chip=e.target&&e.target.closest?e.target.closest('#bp .row .tag.chip'):null;
  if(chip&&favoritesMode)removeFavoritesView();
 },true);
 document.addEventListener('click',e=>{
  const play=e.target&&e.target.closest?e.target.closest('.rima-v40-play'):null;
  if(play){e.preventDefault();playFavorite(play.getAttribute('data-rima-play'));return}
  const heart=e.target&&e.target.closest?e.target.closest('.rima-v40-fav-toggle'):null;
  if(heart){e.preventDefault();e.stopPropagation();toggleFav(heart.getAttribute('data-rima-fav'));return}
  if(e.target&&e.target.closest&&e.target.closest('#rima-v29-player-heart'))setTimeout(sync,0);
  else if(e.target&&e.target.closest&&e.target.closest('#bp [data-rima-fav]'))setTimeout(()=>{sync();if(favoritesMode)renderFavorites()},0);
 });
 window.addEventListener('storage',e=>{if(e.key===KEY){if(favoritesMode)renderFavorites();else sync()}});
 window.addEventListener('orientationchange',()=>setTimeout(scheduleRender,180));
 window.addEventListener('resize',scheduleRender,{passive:true});
 document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')setTimeout(scheduleRender,80)});
 const oldBar=window.zBarUI;
 if(typeof oldBar==='function'&&!oldBar.__rimaV40){
  const f=function(){const r=oldBar.apply(this,arguments);scheduleRender();return r};
  f.__rimaV40=true;window.zBarUI=f;
 }
 const oldPk=window.pk;
 if(typeof oldPk==='function'&&!oldPk.__rimaV40){
  const f=function(){const r=oldPk.apply(this,arguments);scheduleRender();return r};
  f.__rimaV40=true;window.pk=f;
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scheduleRender,{once:true});
 else scheduleRender();
})();
</script>"""
pat=r'<script id="rimalab-favorites-inline-v35">[\s\S]*?</script>'
h,n=re.subn(pat,lambda _:fav,h,count=1)
if n!=1: raise SystemExit('V40_FAIL: v35 favorites script not found')

stage=r"""<style id="rimalab-stage-responsive-spacing-v40">
/* Uma única distribuição vertical: palavra, sugestões, cronômetro e dica sem sobreposição. */
#lv:not([hidden]) #stg.stage{
 display:flex!important;flex-direction:column!important;justify-content:flex-start!important;align-items:stretch!important;
 box-sizing:border-box!important;overflow:visible!important;height:auto!important;max-height:none!important;
 min-height:clamp(440px,52svh,760px)!important;padding:clamp(14px,2.2vh,22px) clamp(12px,2.2vw,20px) clamp(14px,2.2vh,22px)!important;
 gap:0!important;align-self:stretch!important;
}
#lv:not([hidden]) #stg.stage #ck{flex:0 0 auto!important;margin:4px 0 10px!important;line-height:1.2!important}
#lv:not([hidden]) #stg.stage #cb{
 flex:1 1 auto!important;min-width:0!important;width:100%!important;max-width:100%!important;box-sizing:border-box!important;
 min-height:clamp(92px,13vh,156px)!important;height:auto!important;margin:2px auto 4px!important;padding:6px 5px!important;
 line-height:1.10!important;letter-spacing:.032em!important;white-space:nowrap!important;
}
#lv:not([hidden]) #stg.stage #cs{flex:0 0 auto!important;min-height:0!important;margin:7px 0 0!important;line-height:1.25!important}
#lv:not([hidden]) #stg.stage #rm{
 position:relative!important;inset:auto!important;flex:0 0 auto!important;display:flex!important;flex-wrap:wrap!important;
 justify-content:center!important;align-items:center!important;gap:7px!important;
 width:100%!important;min-height:0!important;height:auto!important;margin:4px auto 9px!important;padding:0 5px!important;
 transform:translateY(-2px)!important;pointer-events:none!important;
}
#lv:not([hidden]) #stg.stage #rm>*{
 box-sizing:border-box!important;max-width:48%!important;min-width:0!important;margin:0!important;
 font-size:clamp(11px,2vw,16px)!important;line-height:1.14!important;letter-spacing:.012em!important;
 padding:5px 9px!important;white-space:nowrap!important;
}
#lv:not([hidden]) #stg.stage #sg{flex:0 0 auto!important;min-height:8px!important;margin:7px 0 3px!important}
#lv:not([hidden]) #stg.stage #cn{flex:0 0 auto!important;min-height:1.2em!important;margin:9px auto 0!important;padding:0 3px!important;line-height:1.25!important}
#lv:not([hidden]) #stg.stage .v3bar{
 flex:0 0 auto!important;position:relative!important;inset:auto!important;z-index:7!important;display:flex!important;
 justify-content:center!important;align-items:center!important;width:100%!important;margin:14px auto 2px!important;
 padding:0 0 5px!important;min-height:46px!important;
}
#lv:not([hidden]) #stg.stage .v3bar button{
 flex:0 1 auto!important;min-width:min(210px,72%)!important;max-width:min(300px,92%)!important;
 min-height:44px!important;margin:0!important;padding:10px 17px!important;white-space:normal!important;
}
/* Paisagem: devolve espaço ao botão da dica e alonga ligeiramente o palco para ele não ser cortado. */
@media(orientation:landscape){
 #lv:not([hidden]) #stg.stage{
  min-height:clamp(300px,calc(100svh - 66px),430px)!important;
  height:auto!important;max-height:none!important;padding:10px clamp(12px,1.8vw,22px) 12px!important;
 }
 #lv:not([hidden]) #stg.stage #ck{margin:1px 0 5px!important}
 #lv:not([hidden]) #stg.stage #cb{min-height:clamp(82px,20svh,132px)!important;margin:0 auto 3px!important;padding:3px 5px!important;letter-spacing:.032em!important}
 #lv:not([hidden]) #stg.stage #cs{margin:4px 0 0!important}
 #lv:not([hidden]) #stg.stage #rm{gap:6px!important;margin:2px auto 7px!important;transform:translateY(-1px)!important}
 #lv:not([hidden]) #stg.stage #rm>*{max-width:24%!important;padding:3px 6px!important;font-size:clamp(10px,1.5vw,14px)!important}
 #lv:not([hidden]) #stg.stage #sg{margin:5px 0 2px!important}
 #lv:not([hidden]) #stg.stage #cn{margin:6px auto 0!important;font-size:clamp(11px,1.6vw,14px)!important}
 #lv:not([hidden]) #stg.stage .v3bar{margin:11px auto 0!important;padding:0 0 3px!important;min-height:44px!important}
 #lv:not([hidden]) #stg.stage .v3bar button{min-height:42px!important;padding:8px 14px!important}
}
/* Telas estreitas: chips e botão respeitam a largura útil, sem encostar nas bordas. */
@media(max-width:380px){
 #lv:not([hidden]) #stg.stage{padding-left:10px!important;padding-right:10px!important}
 #lv:not([hidden]) #stg.stage #rm{gap:5px!important;padding:0 2px!important}
 #lv:not([hidden]) #stg.stage #rm>*{max-width:49%!important;padding:4px 7px!important;font-size:clamp(10px,3.1vw,13px)!important}
 #lv:not([hidden]) #stg.stage .v3bar button{min-width:min(190px,78%)!important}
}
@media(orientation:landscape) and (max-height:380px){
 #lv:not([hidden]) #stg.stage{min-height:286px!important;height:auto!important;padding-top:7px!important;padding-bottom:8px!important}
 #lv:not([hidden]) #stg.stage #cb{min-height:72px!important}
 #lv:not([hidden]) #stg.stage #rm{margin:1px auto 4px!important}
 #lv:not([hidden]) #stg.stage .v3bar{margin-top:7px!important;min-height:40px!important}
 #lv:not([hidden]) #stg.stage .v3bar button{min-height:38px!important;padding:6px 12px!important}
}
</style>"""
if 'id="rimalab-stage-responsive-spacing-v40"' not in h:
 pos=h.lower().rfind('</body>')
 if pos<0: raise SystemExit('V40_FAIL: </body> missing')
 h=h[:pos]+stage+'\n'+h[pos:]

g=gp.read_text(encoding='utf-8')
m=re.search(r'\bversionCode\s+(\d+)',g)
if not m: raise SystemExit('V40_FAIL: versionCode missing')
if int(m.group(1))>=60: raise SystemExit('V40_FAIL: versionCode already >=60')
g=g[:m.start(1)]+'60'+g[m.end(1):]
m=re.search(r"""versionName\s+['"]([^'"]+)['"]""",g)
if not m: raise SystemExit('V40_FAIL: versionName missing')
g=g[:m.start(1)]+'3.1.8'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V40_OK: favorites use lexical ZLIB/ZS; all categories stay visible/clickable; saved favorites render across categories; stage spacing responsive in portrait/landscape; version 3.1.8')
