#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve(); hp=root/'app/src/main/assets/rima-lab.html'; gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
if 'rimalab-player-polish-v33' in h: raise SystemExit('V33_FAIL: patch already present')
css=r"""<style id="rimalab-player-polish-v33">
#pbar .pwi{min-width:0!important;overflow:hidden!important}
#pbar #pwn{display:block!important;max-width:100%!important;overflow:hidden!important;white-space:nowrap!important;line-height:1.25!important}
#pbar #pwn .rima-title-track{display:inline-flex!important;align-items:center!important;gap:34px!important;width:max-content!important;max-width:none!important;white-space:nowrap!important;will-change:transform}
#pbar #pwn .rima-title-track span{display:inline-block!important;white-space:nowrap!important}
#pbar #pwn .rima-title-track.is-long{animation:rima-title-marquee-v33 13s linear infinite!important}
@keyframes rima-title-marquee-v33{0%,8%{transform:translateX(0)}92%,100%{transform:translateX(calc(-50% - 17px))}}
#pbar #pwn:hover .rima-title-track.is-long{animation-play-state:paused!important}
@media(orientation:landscape){
 #pbar{position:fixed!important;top:auto!important;bottom:calc(5px + env(safe-area-inset-bottom,0px))!important;left:10px!important;right:10px!important;transform:none!important;width:auto!important;max-width:none!important;height:48px!important;min-height:48px!important;padding:4px 9px!important;display:flex!important;flex-direction:row!important;align-items:center!important;gap:6px!important;z-index:120!important}
 #pbar .pwrow{min-height:36px!important;flex:1 1 auto!important;min-width:0!important;gap:5px!important}
 #pbar .pw-controls button{width:26px!important;height:29px!important}
 #pbar .pw-controls #pwb{width:32px!important;height:32px!important}
 #pbar .pwinfo{display:none!important}
 #pbar .pwscr{position:absolute!important;left:10px!important;right:10px!important;bottom:2px!important;height:3px!important;min-height:3px!important;padding:0!important;gap:0!important}
 #pbar .pwscr .pwm{display:none!important}
 #pbar .pwp{height:3px!important;min-height:3px!important}
 #pbar .pwp:before,#pbar .pwp i{top:0!important;height:3px!important}
 #pbar .pwp b{top:-5px!important;width:12px!important;height:12px!important;margin-left:-6px!important}
 body.pl main,body.pl #lv:not([hidden]){padding-bottom:68px!important}
}
#bp .bsl{margin:2px 0 5px!important}
#bp .row[style*="margin:8px 0"]{margin:6px 0 2px!important}
#bp .rima-v29-tools:not(:has(#rima-v29-backcat)){justify-content:center!important;align-items:center!important;margin:7px auto 9px!important}
#bp .rima-v29-tools:not(:has(#rima-v29-backcat)) button{flex:0 1 260px!important;max-width:100%!important}
#lv:not([hidden]) #stg.stage #rm{margin:0 auto 9px!important;transform:translateY(-2px)!important}
#lv:not([hidden]) #stg.stage .v3bar{order:6!important;margin:9px auto 0!important;padding:2px 0 4px!important}
#lv:not([hidden]) #stg.stage #cb{letter-spacing:.008em!important}
@media(orientation:landscape){#lv:not([hidden]) #stg.stage .v3bar{margin-top:7px!important}#lv:not([hidden]) #stg.stage #rm{margin-bottom:7px!important}}
</style>"""
runtime=r"""<script id="rimalab-player-polish-v33">
(function(){
'use strict';
const $=s=>document.querySelector(s),esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let pausedAt=null;
function syncHearts(){
 let fav=[];try{fav=JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]')}catch(_){}
 const key=String(window.ZS&&ZS.key||''),on=!!key&&fav.includes(key),player=$('#rima-v29-player-heart');
 if(player){player.classList.toggle('on',on);player.textContent=on?'♥':'♡';player.setAttribute('aria-label',on?'Remover dos favoritos':'Adicionar aos favoritos')}
 document.querySelectorAll('[data-rima-fav]').forEach(b=>{const yes=fav.includes(String(b.getAttribute('data-rima-fav')||''));b.classList.toggle('on',yes);b.textContent=yes?'♥':'♡';b.setAttribute('aria-label',yes?'Remover dos favoritos':'Adicionar aos favoritos')});
 document.querySelectorAll('.rima-v29-count').forEach(e=>e.textContent=String(fav.length));
}
function ticker(){
 const e=$('#pwn');if(!e||!window.ZS)return;const name=String(ZS.name||'Beat');if(e.dataset.rimaTitle===name)return;
 e.dataset.rimaTitle=name;e.innerHTML='<span class="rima-title-track"><span>'+esc(name)+'</span><span aria-hidden="true">'+esc(name)+'</span></span>';
 const track=e.firstElementChild;requestAnimationFrame(()=>{if(!track||!e.isConnected)return;const long=track.firstElementChild.scrollWidth>e.clientWidth+12;track.classList.toggle('is-long',long);if(long)track.style.animationDuration=Math.max(10,Math.min(24,track.scrollWidth/38))+'s'});
}
const oldBar=window.zBarUI;if(typeof oldBar==='function')window.zBarUI=function(){oldBar.apply(this,arguments);ticker();syncHearts()};
const oldUI=window.zUI;if(typeof oldUI==='function')window.zUI=function(){if(window.play&&!window.zPL&&pausedAt!==null){const d=typeof zDur==='function'?zDur():0,c=Math.max(0,pausedAt),w=(d>0?Math.min(100,c/d*100):0)+'%',f=$('#pwf'),k=$('#pwk'),t=$('#pwtm');if(f)f.style.width=w;if(k)k.style.left=w;if(t)t.textContent=(typeof zFm==='function'?zFm(c):'0:00')+(d>0?' / '+zFm(d):'');return}return oldUI.apply(this,arguments)};
const oldSet=window.zSetPL;if(typeof oldSet==='function')window.zSetPL=function(v){if(!v){try{pausedAt=typeof zCur==='function'?zCur():0}catch(_){pausedAt=0}}else pausedAt=null;const r=oldSet.apply(this,arguments);syncHearts();return r};
const oldSeek=window.zSeek;if(typeof oldSeek==='function')window.zSeek=function(){const r=oldSeek.apply(this,arguments);if(window.play&&!window.zPL){try{pausedAt=typeof zCur==='function'?zCur():pausedAt}catch(_){}}return r};
const oldFav=window.rimaV29ToggleFav;if(typeof oldFav==='function')window.rimaV29ToggleFav=function(){const r=oldFav.apply(this,arguments);requestAnimationFrame(syncHearts);return r};
const oldPick=window.zBpick;if(typeof oldPick==='function')window.zBpick=function(){let out=oldPick.apply(this,arguments);return out.replace(/<button onclick="rimaV29Random\(\)">[\s\S]*?<\/button>/g,'')};
function install(){syncHearts();ticker();const tools=$('#bp .rima-v29-tools');if(tools){tools.style.justifyContent='center';tools.querySelectorAll('button').forEach(b=>{if(b.textContent.includes('Beat aleatório'))b.remove()})}const p=$('#pbar');if(p&&!p.dataset.v33HeartSync){p.dataset.v33HeartSync='1';p.addEventListener('click',e=>{if(e.target.closest('#rima-v29-player-heart'))setTimeout(syncHearts,0)})}}
function selectDefault(){if(!window.ZS||ZS.key)return;const run=()=>{if(!window.ZS||ZS.key)return;const list=window.ZLIB&&ZLIB['Boom bap']&&ZLIB['Boom bap'][1];if(Array.isArray(list)&&list.length&&typeof window.zLP==='function')zLP(0,0,'Boom bap')};run();if(window.rimaCatalogReady&&typeof window.rimaCatalogReady.then==='function')window.rimaCatalogReady.then(run).catch(()=>{})}
const oldNext=window.trainNext;if(typeof oldNext==='function')window.trainNext=function(){const r=oldNext.apply(this,arguments);selectDefault();setTimeout(install,80);return r};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
setInterval(install,1200);
})();
</script>"""
p=h.lower().rfind('</body>')
if p<0: raise SystemExit('V33_FAIL: </body> ausente')
h=h[:p]+css+'\n'+runtime+'\n'+h[p:]
g=gp.read_text(encoding='utf-8');m=re.search(r'\bversionCode\s+(\d+)',g)
if not m: raise SystemExit('V33_FAIL: versionCode ausente')
if int(m.group(1))<53:g=g[:m.start(1)]+'53'+g[m.end(1):]
m=re.search(r"""versionName\s+['"]([^'"]+)['"]""",g)
if not m: raise SystemExit('V33_FAIL: versionName ausente')
g=g[:m.start(1)]+'3.1.1'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V33_OK: ticker, favoritos sincronizados, aleatório removido da lista, player horizontal inferior, pausa congelada, beat inicial selecionado, espaçamentos ajustados; 3.1.1')