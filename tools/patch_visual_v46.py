#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V46_FAIL: missing app assets or Gradle')
h=hp.read_text(encoding='utf-8')
g=gp.read_text(encoding='utf-8')
if 'rimalab-favorites-layout-runtime-v43' not in h or 'rimalab-selection-feedback-runtime-v45' not in h:
    raise SystemExit('V46_FAIL: expected V43/V45 runtime missing')
if 'rimalab-landscape-stage-download-v47' in h:
    raise SystemExit('V46_FAIL: already applied')

# Add a download control to every favorite row, using the same permission and local-state
# rules as the main catalog download button.
v43_open='<script id="rimalab-favorites-layout-runtime-v43">'
a=h.find(v43_open)
if a<0: raise SystemExit('V46_FAIL: V43 opening tag missing')
body=a+len(v43_open)
z=h.find('</script>',body)
if z<0: raise SystemExit('V46_FAIL: V43 closing tag missing')
js=h[body:z]
pattern=re.compile(r" function favoriteMarkup\(\)\{.*?\n \}\n function removeView",re.S)
replacement=r''' function favoriteDownloadMarkup(t){
  const x=t.x,k=t.key,local=zIsLocal(x)||!!ZDL[k],busy=ZDS[k]==='busy',can=x[10]===true&&!!x[9];
  const cls=local?'ok':busy?'busy':(!can?'nodl':'');
  const icon=local?'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>':busy?'…':'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11M7 11l5 5 5-5M5 20h14"/></svg>';
  const label=local?'Salvo no celular. Toque para apagar':busy?'Salvando beat':can?'Salvar no celular':'Download offline não autorizado para esta faixa';
  return '<button class="dlb rima-v47-fav-download '+cls+'" type="button" data-rima-fav-download="'+esc(k)+'" aria-label="'+esc(label)+'" title="'+esc(label)+'" '+((!local&&!can)||busy?'disabled':'')+' onclick="zDlFavorite(\''+esc(k)+'\')">'+icon+'</button>';
 }
 function favoriteMarkup(){
  const saved=new Set(read()),items=allTracks().filter(t=>saved.has(t.key));
  if(!items.length)return '<div class="rima-v43-favlist"><div class="rima-v43-empty rima-v29-note">Nenhum beat favoritado ainda. Toque no coração de um beat ou no coração do player para adicioná-lo.</div></div>';
  return '<div class="rima-v43-favlist" aria-label="Seus beats favoritos">'+items.map(t=>
   '<div class="rima-v43-fav-row" data-key="'+esc(t.key)+'"><div class="rima-v43-fav-info"><button class="rima-v43-fav-play" type="button" data-v43-play="'+esc(t.key)+'" aria-label="Ouvir '+esc(t.x[1])+'"><b>'+esc(t.x[1])+'</b></button><span class="rima-v43-fav-meta">'+esc(t.cat)+'</span></div>'+favoriteDownloadMarkup(t)+'<button class="rima-v43-fav-heart" type="button" data-v43-heart="'+esc(t.key)+'" aria-label="Remover dos favoritos" aria-pressed="true">♥</button></div>'
  ).join('')+'</div>';
 }
 function syncFavoriteDownloads(key){
  const tracks=allTracks(),wanted=key==null?null:String(key);
  document.querySelectorAll('[data-rima-fav-download]').forEach(button=>{
   const k=button.getAttribute('data-rima-fav-download');
   if(wanted&&k!==wanted)return;
   const t=tracks.find(item=>item.key===k);
   if(t)button.outerHTML=favoriteDownloadMarkup(t);
  });
 }
 function downloadFavorite(key){
  const k=String(key||''),t=allTracks().find(item=>item.key===k);
  if(!t)return;
  const x=t.x,local=zIsLocal(x)||!!ZDL[k];
  if(local){
   if(!confirm('Apagar o beat “'+x[1]+'” do celular?'))return;
   try{if(window.RimaNative&&RimaNative.apagar)RimaNative.apagar(k)}catch(_){}
   ZLOCAL.delete(k);delete ZDL[k];delete ZMETA[k];
   zSv('jm_local_ids',[...ZLOCAL]);zSv('dlmeta1',ZMETA);
   zBuild(t.cat);if(typeof window.pk==='function')window.pk();
   setTimeout(()=>syncFavoriteDownloads(k),80);
   return;
  }
  if(ZDS[k]==='busy')return;
  if(!(x[10]===true&&x[9])){if(typeof zFlash==='function')zFlash('Esta faixa não tem autorização para download offline.');return}
  if(!(window.RimaNative&&RimaNative.baixar)){if(typeof zFlash==='function')zFlash('O salvamento offline funciona no app instalado.');return}
  ZMETA[k]=x;zSv('dlmeta1',ZMETA);ZDS[k]='busy';syncFavoriteDownloads(k);
  try{RimaNative.baixar(k,x[9],1)}catch(e){window.__dl(k,'erro',1)}
 }
 window.rimaV47SyncFavoriteDownloads=syncFavoriteDownloads;
 window.zDlFavorite=downloadFavorite;
 function removeView'''
js2,n=pattern.subn(replacement,js,count=1)
if n!=1: raise SystemExit('V46_FAIL: favorite markup function did not match exactly once')
h=h[:body]+js2+h[z:]

# Remove the incomplete V46 layout block produced by the previous build script.
old_id='<style id="rimalab-landscape-stage-reflow-v46">'
old=h.find(old_id)
if old>=0:
    old_end=h.find('</style>',old)
    if old_end<0: raise SystemExit('V46_FAIL: old landscape style close missing')
    h=h[:old]+h[old_end+len('</style>'):]

css=r"""<style id="rimalab-landscape-stage-download-v47">
/* Favorites label is deliberately regular weight everywhere, including legacy toolbars. */
#bp .rima-v43-toggle,#bq .rima-v43-toggle,
#bp .rima-v42-favorites-toggle,#bq .rima-v42-favorites-toggle,
#bp .rima-v29-tools button,#bq .rima-v29-tools button,
#bp .rima-v43-tools button,#bq .rima-v43-tools button,#rima-v29-favs{
 font-weight:500!important;
}
#bp .rima-v43-toggle .rima-v29-count,#bq .rima-v43-toggle .rima-v29-count,
#bp .rima-v42-favorites-toggle .rima-v29-count,#bq .rima-v42-favorites-toggle .rima-v29-count,
#bp .rima-v29-tools .rima-v29-count,#bq .rima-v29-tools .rima-v29-count{font-weight:800!important}
#bp .rima-v43-fav-row,#bq .rima-v43-fav-row{
 grid-template-columns:minmax(0,1fr) 42px 44px!important;
 gap:8px!important;
}
#bp .rima-v47-fav-download,#bq .rima-v47-fav-download{
 display:grid!important;place-items:center!important;box-sizing:border-box!important;
 width:40px!important;min-width:40px!important;max-width:40px!important;
 height:40px!important;min-height:40px!important;max-height:40px!important;
 padding:0!important;margin:0!important;flex:none!important;
 border:1px solid rgba(230,193,78,.52)!important;border-radius:50%!important;
 background:rgba(230,193,78,.10)!important;color:#e8c45c!important;
 opacity:1!important;cursor:pointer!important;touch-action:manipulation!important;
}
#bp .rima-v47-fav-download.ok,#bq .rima-v47-fav-download.ok{
 background:#83edac!important;color:#0b2113!important;border-color:#83edac!important;
}
#bp .rima-v47-fav-download.busy,#bq .rima-v47-fav-download.busy{opacity:.8!important}
#bp .rima-v47-fav-download.nodl,#bq .rima-v47-fav-download.nodl,
#bp .rima-v47-fav-download:disabled,#bq .rima-v47-fav-download:disabled{opacity:.34!important;cursor:not-allowed!important}
@media (orientation:landscape) and (min-width:560px){
 body.pl:not(.pv) main,body.pl.sy:not(.pv) main{
  width:100%!important;max-width:none!important;box-sizing:border-box!important;
 }
 body.pl:not(.pv) #lv:not([hidden]),body.pl.sy:not(.pv) #lv:not([hidden]){
  position:fixed!important;inset:0 0 var(--rima-stage-bottom,90px) 0!important;
  display:grid!important;width:auto!important;height:auto!important;min-height:0!important;
  max-height:none!important;box-sizing:border-box!important;overflow:hidden!important;
  grid-template-columns:minmax(0,1.18fr) minmax(0,.82fr)!important;
  grid-template-rows:42px minmax(0,1fr) 42px!important;
  gap:8px 12px!important;align-items:stretch!important;align-content:stretch!important;
  margin:0!important;padding:8px max(12px,env(safe-area-inset-right,0px)) 4px max(12px,env(safe-area-inset-left,0px))!important;
 }
 body.pl:not(.pv) #lv:not([hidden])>*,body.pl.sy:not(.pv) #lv:not([hidden])>*{
  box-sizing:border-box!important;width:100%!important;max-width:none!important;min-width:0!important;
  margin-left:0!important;margin-right:0!important;
 }
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage,body.pl.sy:not(.pv) #lv:not([hidden])>#stg.stage{
  grid-column:1!important;grid-row:1/4!important;align-self:stretch!important;
  display:flex!important;flex-direction:column!important;justify-content:center!important;
  height:100%!important;min-height:0!important;max-height:none!important;overflow:hidden!important;
  margin:0!important;padding:clamp(10px,2vh,20px) clamp(12px,1.5vw,24px)!important;
 }
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage #ck,
 body.pl.sy:not(.pv) #lv:not([hidden])>#stg.stage #ck{flex:0 0 auto!important;margin:0 0 8px!important}
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage #cb,
 body.pl.sy:not(.pv) #lv:not([hidden])>#stg.stage #cb{
  flex:1 1 auto!important;display:flex!important;align-items:center!important;justify-content:center!important;
  box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;
  min-height:90px!important;height:auto!important;max-height:none!important;white-space:normal!important;
  overflow-wrap:anywhere!important;line-height:1.04!important;margin:0 auto!important;padding:8px 5px!important;
 }
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage #rm,
 body.pl.sy:not(.pv) #lv:not([hidden])>#stg.stage #rm{
  position:relative!important;inset:auto!important;flex:0 0 auto!important;
  display:flex!important;flex-wrap:wrap!important;justify-content:center!important;align-items:center!important;
  width:100%!important;max-width:100%!important;min-height:0!important;height:auto!important;
  margin:6px auto!important;padding:0 3px!important;transform:none!important;gap:6px!important;
 }
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage #rm>*,
 body.pl.sy:not(.pv) #lv:not([hidden])>#stg.stage #rm>*{max-width:48%!important;min-width:0!important;white-space:normal!important}
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage #sg,
 body.pl.sy:not(.pv) #lv:not([hidden])>#stg.stage #sg{flex:0 0 auto!important;margin:4px 0!important}
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage #cs,
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage #cn,
 body.pl.sy:not(.pv) #lv:not([hidden])>#stg.stage #cs,
 body.pl.sy:not(.pv) #lv:not([hidden])>#stg.stage #cn{flex:0 0 auto!important;max-width:100%!important;margin:5px auto 0!important;line-height:1.22!important}
 body.pl:not(.pv) #lv:not([hidden])>#stg.stage .v3bar,
 body.pl.sy:not(.pv) #lv:not([hidden])>#stg.stage .v3bar{flex:0 0 auto!important;margin:8px auto 0!important}
 body.pl:not(.pv) #lv:not([hidden])>.bk,body.pl.sy:not(.pv) #lv:not([hidden])>.bk{
  grid-column:2!important;grid-row:1!important;align-self:stretch!important;
  height:42px!important;min-height:42px!important;margin:0!important;
 }
 body.pl:not(.pv) #lv:not([hidden])>.card:not(.stage),body.pl.sy:not(.pv) #lv:not([hidden])>.card:not(.stage){
  grid-column:2!important;grid-row:2!important;align-self:stretch!important;
  height:100%!important;min-height:0!important;max-height:none!important;
  margin:0!important;padding:10px 12px!important;overflow-x:hidden!important;overflow-y:auto!important;
  overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important;
 }
 body.pl:not(.pv) #lv:not([hidden])>.btn.w,body.pl.sy:not(.pv) #lv:not([hidden])>.btn.w{
  grid-column:2!important;grid-row:3!important;align-self:stretch!important;
  width:100%!important;height:42px!important;min-height:42px!important;margin:0!important;
 }
 body.pl:not(.pv) #lv:not([hidden]) #bq,body.pl.sy:not(.pv) #lv:not([hidden]) #bq{
  width:100%!important;max-width:100%!important;min-width:0!important;box-sizing:border-box!important;margin:0!important;
 }
 body.pl:not(.pv) #lv:not([hidden]) #bq .bsl,body.pl.sy:not(.pv) #lv:not([hidden]) #bq .bsl{
  max-width:100%!important;min-width:0!important;max-height:none!important;overflow:visible!important;
 }
 body.pl:not(.pv) #lv:not([hidden]) #bq .bi,body.pl.sy:not(.pv) #lv:not([hidden]) #bq .bi{min-width:0!important}
}
</style>
<script id="rimalab-landscape-stage-download-runtime-v47">
(function(){
 'use strict';
 function adjust(){
  const lv=document.getElementById('lv'),pb=document.getElementById('pbar');
  if(!lv)return;
  const wide=window.matchMedia&&window.matchMedia('(orientation:landscape) and (min-width:560px)').matches;
  if(!wide||lv.hidden){lv.style.removeProperty('--rima-stage-bottom');return}
  let reserve=90;
  if(pb){const r=pb.getBoundingClientRect();if(r.height>0&&r.top>=0&&r.top<window.innerHeight)reserve=Math.max(70,window.innerHeight-r.top+8)}
  lv.style.setProperty('--rima-stage-bottom',reserve+'px');
 }
 const lv=document.getElementById('lv'),pb=document.getElementById('pbar');
 if(lv&&window.MutationObserver)new MutationObserver(()=>{requestAnimationFrame(adjust);setTimeout(adjust,120)}).observe(lv,{attributes:true,attributeFilter:['hidden']});
 window.addEventListener('resize',adjust,{passive:true});
 window.addEventListener('orientationchange',()=>setTimeout(adjust,120),{passive:true});
 if(window.ResizeObserver&&pb){try{new ResizeObserver(adjust).observe(pb)}catch(_){}}
 document.addEventListener('DOMContentLoaded',adjust,{once:true});
 setTimeout(adjust,100);setTimeout(adjust,350);
 window.rimaV47AdjustLandscape=adjust;
 const original=window.__dl;
 if(typeof original==='function'&&!original.__rimaV47){
  const wrapped=function(k,st,perm){
   const result=original.apply(this,arguments);
   const sync=window.rimaV47SyncFavoriteDownloads;
   if(typeof sync==='function'){requestAnimationFrame(()=>sync(k));setTimeout(()=>sync(k),100)}
   return result;
  };
  wrapped.__rimaV47=true;window.__dl=wrapped;
 }
})();
</script>"""
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V46_FAIL: body close missing')
h=h[:pos]+css+'\n'+h[pos:]

m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='67': raise SystemExit('V46_FAIL: expected base versionCode 67 after V45')
g=g[:m.start()]+re.sub('67','68',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.2.5': raise SystemExit('V46_FAIL: expected base versionName 3.2.5 after V45')
g=g[:m.start()]+m.group(0).replace('3.2.5','3.2.6')+g[m.end():]
hp.write_text(h,encoding='utf-8')
gp.write_text(g,encoding='utf-8')
print('V46_OK: full-height horizontal stage above untouched player; Favorites regular-weight; favorite download state/actions in bp and bq; version 3.2.6/code68')
