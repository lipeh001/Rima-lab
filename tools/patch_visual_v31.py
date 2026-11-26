#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
g=gp.read_text(encoding='utf-8')
css=r"""
<style id="rimalab-player-stage-fixes-v31">
/* Beat ticker: radio-style marquee, only when the title does not fit. */
#pbar .rima-v31-ticker{display:block!important;position:relative!important;overflow:hidden!important;white-space:nowrap!important;min-width:0!important;max-width:100%!important}
#pbar .rima-v31-ticker-track{display:inline-flex!important;width:max-content!important;min-width:100%!important;align-items:center!important;gap:56px!important;white-space:nowrap!important;will-change:transform}
#pbar .rima-v31-ticker.is-overflow .rima-v31-ticker-track{animation:rimaV31Marquee var(--rima-v31-duration,16s) ease-in-out infinite alternate}
#pbar .rima-v31-ticker:not(.is-overflow) .rima-v31-ticker-track{transform:none!important;animation:none!important}
@keyframes rimaV31Marquee{0%,8%{transform:translateX(0)}92%,100%{transform:translateX(calc(-1 * var(--rima-v31-distance,0px)))}}
#pbar{position:fixed!important;top:auto!important;transform:none!important}
@media(orientation:landscape) and (max-height:850px){
 #pbar{left:12px!important;right:12px!important;bottom:calc(10px + env(safe-area-inset-bottom,0px))!important;width:auto!important;max-width:none!important;z-index:120!important}
 nav{bottom:calc(6px + env(safe-area-inset-bottom,0px))!important;z-index:121!important}
 body.pl main{padding-bottom:calc(132px + env(safe-area-inset-bottom,0px))!important}
 #pbar .rima-v31-ticker{max-width:min(42vw,520px)!important}
}
#pbar[data-rima-playing="false"] .rima-v31-ticker-track,
#pbar[data-rima-playing="false"] .progress,
#pbar[data-rima-playing="false"] .progress-fill,
#pbar[data-rima-playing="false"] .seek-fill{animation-play-state:paused!important}
#lv:not([hidden]) #stg.stage #cb{letter-spacing:.015em!important;word-spacing:.035em!important}
#lv:not([hidden]) #stg.stage #rm{bottom:68px!important;gap:8px!important}
#lv:not([hidden]) #stg.stage #rm span{margin-top:0!important;margin-bottom:0!important}
#lv:not([hidden]) #stg.stage #cs{margin-top:8px!important;margin-bottom:12px!important}
#lv:not([hidden]) #stg.stage button{margin-top:8px!important}
#bp .rima-v29-tools{justify-content:center!important;align-items:center!important;margin:8px auto 10px!important;max-width:100%!important}
#bp .rima-v29-tools button:first-child{display:none!important}
#bp .rima-v29-tools button:last-child{flex:0 1 260px!important;min-width:210px!important;max-width:85%!important;margin:0 auto!important}
#bp .rima-v29-tools{gap:0!important}
#bp .bsl{margin-top:8px!important;padding-top:0!important}
#bp .bsl .bi{margin-top:7px!important;margin-bottom:7px!important}
@media(orientation:landscape) and (max-height:850px){
 #lv:not([hidden]) #stg.stage{margin-bottom:16px!important}
 #lv:not([hidden]) #stg.stage #rm{bottom:62px!important}
 #lv:not([hidden]) #stg.stage #cs{margin-top:10px!important}
}
</style>
"""
script=r"""
<script id="rimalab-player-stage-runtime-v31">
(function(){
'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function tracks(){
 try{return Object.keys(window.ZLIB||{}).flatMap(cat=>(ZLIB[cat]?.[1]||[]).map(x=>({cat,x,key:String(x?.[4]??''),title:clean(x?.[1])})))}
 catch(e){return []}
}
function playerTitleNode(){
 const p=$('#pbar');if(!p)return null;
 const candidates=[...p.querySelectorAll('*')].filter(e=>e.children.length===0&&clean(e.textContent).length>8&&!/^\d+:\d+/.test(clean(e.textContent)));
 candidates.sort((a,b)=>clean(b.textContent).length-clean(a.textContent).length);
 return candidates[0]||null;
}
function installTicker(){
 const node=playerTitleNode();if(!node)return;
 if(node.closest('.rima-v31-ticker'))return;
 const title=clean(node.textContent);if(!title)return;
 const wrap=document.createElement('span');wrap.className='rima-v31-ticker';
 const track=document.createElement('span');track.className='rima-v31-ticker-track';
 const a=document.createElement('span');a.textContent=title;
 const b=document.createElement('span');b.textContent=title; b.setAttribute('aria-hidden','true');
 track.append(a,b);wrap.append(track);
 node.textContent='';node.append(wrap);
 const measure=()=>{const overflow=a.scrollWidth>wrap.clientWidth+8;wrap.classList.toggle('is-overflow',overflow);const distance=Math.max(0,a.scrollWidth-wrap.clientWidth+56);wrap.style.setProperty('--rima-v31-distance',distance+'px');wrap.style.setProperty('--rima-v31-duration',Math.max(10,Math.min(26,distance/22))+'s')};
 requestAnimationFrame(measure);if(window.ResizeObserver)new ResizeObserver(measure).observe(wrap);
}
function currentTrack(){
 const list=tracks();
 const key=String(window.ZS?.key??'');
 if(key){const byKey=list.find(t=>t.key===key);if(byKey)return byKey}
 const p=$('#pbar');const text=clean(p?.innerText||p?.textContent);
 let found=list.filter(t=>t.title&&text.includes(t.title)).sort((a,b)=>b.title.length-a.title.length)[0];
 if(found)return found;
 const audio=$('audio');const src=audio?.currentSrc||audio?.src||'';
 return list.find(t=>t.x?.[0]&&src.includes(String(t.x[0])))||null;
}
function favs(){try{const x=JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]');return Array.isArray(x)?x.map(String):[]}catch(e){return []}}
function syncHearts(){
 const list=favs(),cur=currentTrack(),key=cur?.key||'';
 const p=$('#rima-v29-player-heart');
 if(p){p.classList.toggle('on',!!key&&list.includes(key));p.textContent=key&&list.includes(key)?'♥':'♡';p.dataset.trackKey=key}
 $$('[data-rima-fav]').forEach(b=>{const on=list.includes(String(b.dataset.rimaFav||b.getAttribute('data-rima-fav')));b.classList.toggle('on',on);b.textContent=on?'♥':'♡'});
}
function bindPlayerHeart(){
 const p=$('#rima-v29-player-heart');if(!p||p.dataset.v31Bound)return;
 p.dataset.v31Bound='1';
 p.addEventListener('click',()=>{
  const cur=currentTrack();if(!cur?.key)return;
  if(typeof window.rimaV29ToggleFav==='function')window.rimaV29ToggleFav(cur.key);
  setTimeout(syncHearts,80);
 });
}
function audioState(){
 const p=$('#pbar'),a=$('audio');if(!p)return;
 const playing=!!a&&!a.paused&&!a.ended;
 p.dataset.rimaPlaying=String(playing);
 if(!playing){p.querySelectorAll('.rima-v31-ticker-track').forEach(e=>e.style.animationPlayState='paused')}
 else p.querySelectorAll('.rima-v31-ticker-track').forEach(e=>e.style.animationPlayState='running');
}
function layoutHints(){
 const stage=$('#stg');if(!stage)return;
 const hint=[...stage.querySelectorAll('button')].find(b=>/dica de rima/i.test(clean(b.textContent)));
 if(hint){hint.style.setProperty('margin-top','14px','important');hint.style.setProperty('margin-bottom','8px','important')}
 const chips=$('#rm');if(chips){chips.style.setProperty('bottom','68px','important');chips.style.setProperty('gap','8px','important')}
}
function centerFavorites(){
 const tools=$('#bp .rima-v29-tools');if(!tools)return;
 const buttons=[...tools.querySelectorAll('button')];
 buttons.forEach(b=>{if(/beat aleatório/i.test(clean(b.textContent)))b.style.setProperty('display','none','important')});
 const fav=buttons.find(b=>/favoritos/i.test(clean(b.textContent)));
 if(fav){tools.style.setProperty('display','flex','important');tools.style.setProperty('justify-content','center','important');fav.style.setProperty('flex','0 1 260px','important');fav.style.setProperty('margin','0 auto','important')}
}
function tick(){
 installTicker();bindPlayerHeart();syncHearts();audioState();layoutHints();centerFavorites();
}
function init(){
 tick();
 const root=$('#pbar');if(root&&window.MutationObserver)new MutationObserver(tick).observe(root,{childList:true,subtree:true,characterData:true});
 const bp=$('#bp');if(bp&&window.MutationObserver)new MutationObserver(tick).observe(bp,{childList:true,subtree:true});
 const audio=$('audio');if(audio)['play','pause','ended','timeupdate','loadedmetadata'].forEach(ev=>audio.addEventListener(ev,audioState));
 window.addEventListener('resize',tick,{passive:true});
 setInterval(tick,1200);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
</script>
"""
if 'id="rimalab-player-stage-fixes-v31"' not in h:
 p=h.lower().rfind('</head>');h=h[:p]+css+h[p:] if p>=0 else h+css
if 'id="rimalab-player-stage-runtime-v31"' not in h:
 p=h.lower().rfind('</body>')
 if p<0:raise SystemExit('V31_FAIL: body ausente')
 h=h[:p]+script+h[p:]
# bump Android version
m=re.search(r'versionCode\s+(\d+)',g)
if not m:raise SystemExit('V31_FAIL: versionCode ausente')
g=g[:m.start(1)]+str(max(53,int(m.group(1))+1))+g[m.end(1):]
m=re.search(r"versionName\s+['\"]([^'\"]+)['\"]",g)
if not m:raise SystemExit('V31_FAIL: versionName ausente')
g=g[:m.start(1)]+'3.1.1'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V31_OK: marquee do player, favoritos sincronizados, layout horizontal, dicas e espaçamento do catálogo')
