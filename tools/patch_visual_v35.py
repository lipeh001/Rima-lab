#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve(); hp=root/'app/src/main/assets/rima-lab.html'; gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
if 'rimalab-favorites-inline-v35' in h: raise SystemExit('V35_FAIL: already applied')
css=r"""
<style id="rimalab-favorites-inline-v35">
#bp .rima-v29-tools{display:flex!important;justify-content:center!important;align-items:center!important;margin:8px auto 10px!important}
#bp .rima-v29-tools button{flex:0 1 270px!important;max-width:100%!important}
#bp .rima-v29-tools #rima-v29-backcat{display:none!important}
#bp .rima-v35-favlist{display:grid!important;gap:8px!important;margin:8px 0 14px!important}
#bp .rima-v35-favlist .bi{display:flex!important;align-items:center!important;gap:10px!important}
#bp .rima-v35-favlist .beat-info{flex:1 1 auto!important;min-width:0!important}
#bp .rima-v35-favlist .mc{width:100%!important;text-align:left!important}
#bp .rima-v35-favlist .rima-v35-heart{width:42px!important;height:42px!important;flex:0 0 42px!important;border-radius:50%!important;border:1px solid rgba(230,193,78,.45)!important;background:rgba(230,193,78,.13)!important;color:#e8c45c!important;font-size:22px!important}
#bp .rima-v35-favlist .rima-v35-heart[aria-pressed=true]{background:#e8c45c!important;color:#15150f!important}
#pbar #rima-v29-player-heart{color:#17130a!important;background:#e8c45c!important;border-color:#e8c45c!important}
#pbar #rima-v29-player-heart[aria-pressed=false]{color:#b7a2e8!important;background:transparent!important;border-color:rgba(183,162,232,.45)!important}
#lv:not([hidden]) #stg.stage #rm{margin:5px auto 11px!important;gap:7px!important}
#lv:not([hidden]) #stg.stage .v3bar{margin-top:12px!important}
#lv:not([hidden]) #stg.stage #cb{letter-spacing:.018em!important}
@media(orientation:landscape) and (max-height:900px){
 #pbar{position:fixed!important;inset:auto 10px calc(58px + env(safe-area-inset-bottom,0px)) 10px!important;width:auto!important;height:50px!important;min-height:50px!important;max-width:none!important;transform:none!important;z-index:9999!important;margin:0!important}
 body.pl main,body.pl #lv:not([hidden]){padding-bottom:125px!important}
 #lv:not([hidden]) #stg.stage #rm{margin:7px auto 12px!important}
 #lv:not([hidden]) #stg.stage .v3bar{margin-top:13px!important}
}
</style>
"""
js=r"""
<script id="rimalab-favorites-inline-v35">
(function(){
'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],FKEY='rimalab_favorites_v29';
let favoritesMode=false;
const readFav=()=>{try{const a=JSON.parse(localStorage.getItem(FKEY)||'[]');return Array.isArray(a)?[...new Set(a.map(String))]:[]}catch(_){return[]}};
const trackKey=x=>x&&x[4]!=null?'jm-'+String(x[4]):'';
const allTracks=()=>Object.keys(window.ZLIB||{}).flatMap(cat=>(ZLIB[cat]&&ZLIB[cat][1]||[]).map(x=>({cat,x})));
const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function sync(){
 const fav=readFav(),key=String(window.ZS&&ZS.key||''),on=!!key&&fav.includes(key),p=$('#rima-v29-player-heart');
 if(p){p.textContent=on?'♥':'♡';p.classList.toggle('on',on);p.setAttribute('aria-pressed',String(on));p.setAttribute('aria-label',on?'Remover dos favoritos':'Adicionar aos favoritos')}
 $$('[data-rima-fav]').forEach(b=>{const yes=fav.includes(String(b.getAttribute('data-rima-fav')||''));b.textContent=yes?'♥':'♡';b.classList.toggle('on',yes);b.setAttribute('aria-pressed',String(yes))});
 $$('.rima-v29-count').forEach(e=>e.textContent=String(fav.length));
}
function favMarkup(){
 const fav=readFav(),tracks=fav.map(k=>allTracks().find(o=>trackKey(o.x)===k)).filter(Boolean);
 if(!tracks.length)return '<p class="rima-v29-note">Nenhum beat favoritado ainda. Use o coração ao lado de qualquer beat para adicioná-lo aqui.</p>';
 return '<div class="bsl rima-v35-favlist">'+tracks.map(({cat,x})=>{const k=trackKey(x);return '<div class="bi"><div class="beat-info"><button class="mc" type="button" onclick="rimaV29PlayFav(\\''+k+'\\')"><b>'+esc(x[1])+'</b></button><div class="beat-meta">'+esc(cat)+'</div></div><button class="rima-v35-heart" type="button" data-rima-fav="'+k+'" aria-pressed="true" onclick="rimaV29ToggleFav(\\''+k+'\\');event.stopPropagation()">♥</button></div>'}).join('')+'</div>';
}
function render(){
 const bp=$('#bp');if(!bp)return;
 const old=bp.querySelector('.rima-v35-favlist');if(old)old.remove();
 const row=[...bp.children].find(e=>e.classList&&e.classList.contains('row')&&e.querySelectorAll('button.tag.chip').length>=2);if(!row)return;
 const list=bp.querySelector('.bsl:not(.rima-v35-favlist)'),attr=bp.querySelector('.catalog-attribution');
 if(list)list.hidden=favoritesMode;if(attr)attr.hidden=favoritesMode;
 const tools=bp.querySelector('.rima-v29-tools'),btn=tools&&tools.querySelector('button');
 if(btn){btn.classList.toggle('active',favoritesMode);btn.setAttribute('aria-pressed',String(favoritesMode));btn.innerHTML='♥ Favoritos <span class="rima-v29-count">'+readFav().length+'</span>'}
 if(favoritesMode){const wrap=document.createElement('div');wrap.innerHTML=favMarkup();if(wrap.firstElementChild)row.insertAdjacentElement('afterend',wrap.firstElementChild)}
}
function toggleView(){favoritesMode=!favoritesMode;if(typeof window.pk==='function')window.pk();requestAnimationFrame(()=>{render();sync()})}
window.rimaV29ShowFavorites=toggleView;
const oldToggle=window.rimaV29ToggleFav;
if(typeof oldToggle==='function')window.rimaV29ToggleFav=function(k){const r=oldToggle.apply(this,arguments);setTimeout(()=>{sync();if(favoritesMode){if(typeof window.pk==='function')window.pk();render()}},40);return r};
function bindPlayer(){
 const p=$('#rima-v29-player-heart');if(!p||p.dataset.v35Bound)return;p.dataset.v35Bound='1';
 p.onclick=function(e){e.preventDefault();e.stopPropagation();const k=String(window.ZS&&ZS.key||'');if(k&&typeof window.rimaV29ToggleFav==='function')window.rimaV29ToggleFav(k);setTimeout(sync,30)};
 p.type='button';
}
function dock(){
 const p=$('#pbar');if(!p)return;if(p.parentElement!==document.body)document.body.appendChild(p);
 if(matchMedia('(orientation:landscape)').matches){p.style.setProperty('position','fixed','important');p.style.setProperty('top','auto','important');p.style.setProperty('left','10px','important');p.style.setProperty('right','10px','important');p.style.setProperty('bottom','calc(58px + env(safe-area-inset-bottom, 0px))','important');p.style.setProperty('transform','none','important');p.style.setProperty('z-index','9999','important')}
}
function labels(){
 const s=$('#train-step-2');if(!s)return;const h=[...s.querySelectorAll('.stp')].find(e=>/ESCOLHA SEU MODO|CONFIGURE SEU MODO/i.test(e.textContent||''));if(h){const n=h.querySelector('.n');if(n)n.textContent='1'}
 const b=$('#rima-v29-mode-banner'),strong=b&&b.querySelector('strong');if(strong)strong.textContent=strong.textContent.replace(/^\s*1\s*[·.:-]\s*/,'');
}
function install(){bindPlayer();dock();labels();if(favoritesMode)render();sync()}
document.addEventListener('click',e=>{if(e.target.closest('#rima-v29-player-heart'))setTimeout(sync,30)});
window.addEventListener('storage',e=>{if(e.key===FKEY){sync();if(favoritesMode){window.pk&&pk();render()}}});
window.addEventListener('orientationchange',()=>setTimeout(dock,180));
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')setTimeout(install,100)});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
setInterval(install,900);
})();
</script>
"""
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V35_FAIL: body missing')
h=h[:pos]+css+'\n'+js+'\n'+h[pos:]
g=gp.read_text(encoding='utf-8');m=re.search(r'\bversionCode\s+(\d+)',g)
if not m: raise SystemExit('V35_FAIL: versionCode missing')
g=g[:m.start(1)]+'55'+g[m.end(1):]
m=re.search(r"""versionName\s+['"]([^'"]+)['"]""",g)
if not m: raise SystemExit('V35_FAIL: versionName missing')
g=g[:m.start(1)]+'3.1.3'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V35_OK: persistent player heart, favorites inline with categories preserved, landscape dock, mode label, spacing')
