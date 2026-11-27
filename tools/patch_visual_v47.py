#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V47_FAIL: missing app assets or Gradle')
h=hp.read_text(encoding='utf-8')
g=gp.read_text(encoding='utf-8')
if 'rimalab-landscape-stage-download-runtime-v47' not in h or 'rimalab-selection-feedback-runtime-v45' not in h:
    raise SystemExit('V47_FAIL: expected V46 layout/Favorites runtimes missing')
if 'rimalab-favorites-details-v48' in h:
    raise SystemExit('V47_FAIL: already applied')

# Two older patches wrote the characters backslash+n between script/style tags.
# Those characters become visible text nodes in Android WebView.
h=h.replace('</script>\\n<style','</script>\n<style')

# Add a visible status label matching the catalog's "SALVO NO CELULAR" treatment.
open_tag='<script id="rimalab-favorites-layout-runtime-v43">'
a=h.find(open_tag)
if a<0: raise SystemExit('V47_FAIL: V43 Favorites runtime missing')
body=a+len(open_tag)
z=h.find('</script>',body)
if z<0: raise SystemExit('V47_FAIL: V43 Favorites runtime closing tag missing')
js=h[body:z]
if 'function favoriteStatusMarkup(t)' not in js:
    marker=' function favoriteMarkup(){'
    status=r''' function favoriteStatusMarkup(t){
  const state=window.rimaDownloadStateByKey?window.rimaDownloadStateByKey(t.key):null;
  if(state&&state.local)return '<small class="okc rima-v48-fav-status">✓ SALVO NO CELULAR</small>';
  if(state&&state.busy)return '<small class="rima-v48-fav-status busy">SALVANDO NO CELULAR…</small>';
  return '';
 }
'''
    if marker not in js: raise SystemExit('V47_FAIL: favoriteMarkup insertion point missing')
    js=js.replace(marker,status+marker,1)

old_markup='''<span class="rima-v43-fav-meta">'+esc(t.cat)+'</span></div>'+favoriteDownloadMarkup(t)+'''
new_markup='''<span class="rima-v43-fav-meta">'+esc(t.cat)+'</span>'+favoriteStatusMarkup(t)+'</div>'+favoriteDownloadMarkup(t)+'''
if old_markup not in js: raise SystemExit('V47_FAIL: favorite row meta markup did not match')
js=js.replace(old_markup,new_markup,1)

# Refresh the status label whenever the native downloader reports success/failure,
# and when the user starts or removes an offline copy.
old_sync='''   const t=tracks.find(item=>item.key===k);
   if(t)button.outerHTML=favoriteDownloadMarkup(t);'''
new_sync='''   const t=tracks.find(item=>item.key===k);
   if(t){
    const row=button.closest('.rima-v43-fav-row');
    button.outerHTML=favoriteDownloadMarkup(t);
    const info=row&&row.querySelector('.rima-v43-fav-info');
    if(info){
     const oldStatus=info.querySelector('.rima-v48-fav-status');
     const markup=favoriteStatusMarkup(t);
     if(markup){if(oldStatus)oldStatus.outerHTML=markup;else info.insertAdjacentHTML('beforeend',markup)}
     else if(oldStatus)oldStatus.remove();
    }
   }'''
if old_sync not in js: raise SystemExit('V47_FAIL: favorite download state sync block missing')
js=js.replace(old_sync,new_sync,1)
h=h[:body]+js+h[z:]

# Keep setup step 2 completely out of view while the live stage is active.
old_start=''' screen.style.display='';
 screen.hidden=false;
 wInit();'''
new_start=''' screen.style.display='';
 screen.hidden=false;
 const setupStep=document.getElementById('train-step-2');
 if(setupStep){setupStep.hidden=true;setupStep.setAttribute('aria-hidden','true')}
 wInit();'''
if old_start not in h: raise SystemExit('V47_FAIL: lvStart setup visibility insertion point missing')
h=h.replace(old_start,new_start,1)
old_stop="else{if($('#train-step-1'))$('#train-step-1').hidden=true;if($('#train-step-2'))$('#train-step-2').hidden=false}"
new_stop="else{if($('#train-step-1'))$('#train-step-1').hidden=true;if($('#train-step-2')){$('#train-step-2').hidden=false;$('#train-step-2').setAttribute('aria-hidden','false')}}"
if old_stop not in h: raise SystemExit('V47_FAIL: lvStop setup restore block missing')
h=h.replace(old_stop,new_stop,1)

css=r"""<style id="rimalab-favorites-details-v48">
/* The Favorites count is regular weight, like the category counters. */
#bp .rima-v43-toggle .rima-v29-count,#bq .rima-v43-toggle .rima-v29-count,
#bp .rima-v42-favorites-toggle .rima-v29-count,#bq .rima-v42-favorites-toggle .rima-v29-count,
#bp .rima-v29-tools .rima-v29-count,#bq .rima-v29-tools .rima-v29-count{
 font-weight:500!important;
}
#bp .rima-v48-fav-status,#bq .rima-v48-fav-status{
 display:block!important;margin:4px 3px 0!important;color:#3dffa0!important;
 font-size:11px!important;font-weight:700!important;letter-spacing:.015em!important;line-height:1.15!important;
}
#bp .rima-v48-fav-status.busy,#bq .rima-v48-fav-status.busy{color:#e8c45c!important}
/* Never let the previous setup page peek through the live stage. */
#train-step-2[hidden]{display:none!important}
#lv:not([hidden])~#train-step-2{display:none!important}
#lv:not([hidden]) #stg.stage #ck{margin:18px 0 8px!important}
#lv:not([hidden]) #stg.stage .v3bar{margin:5px auto 0!important;padding-bottom:4px!important}
/* Rebuild the thin seek line after returning from landscape to portrait. */
@media (orientation:portrait) and (max-width:700px){
 #pbar .pwscr{
  display:flex!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;
  position:absolute!important;left:12px!important;right:12px!important;top:auto!important;bottom:3px!important;
  width:auto!important;height:3px!important;min-height:3px!important;max-height:3px!important;
  margin:0!important;padding:0!important;gap:0!important;z-index:12003!important;
 }
 #pbar .pwscr .pwm{display:none!important}
 #pbar .pwscr .pwp{
  display:block!important;visibility:visible!important;position:relative!important;inset:auto!important;
  flex:1 1 auto!important;min-width:20px!important;width:100%!important;height:3px!important;min-height:3px!important;
  margin:0!important;padding:0!important;
 }
 #pbar .pwscr .pwp:before,#pbar .pwscr .pwp i{top:0!important;height:3px!important}
 #pbar .pwscr .pwp b{top:-4px!important;width:11px!important;height:11px!important;margin-left:-5px!important}
}
</style>
<script id="rimalab-orientation-recovery-runtime-v48">
(function(){
 'use strict';
 const bar=document.getElementById('pbar');
 function restorePortraitProgress(){
  const portrait=window.matchMedia?window.matchMedia('(orientation:portrait) and (max-width:700px)').matches:window.innerHeight>=window.innerWidth;
  if(!portrait||!bar)return;
  const seek=bar.querySelector('.pwscr');
  if(seek){
   ['display','visibility','opacity','position','left','right','top','bottom','width','height','min-height','max-height','flex','flex-basis','margin','padding','gap','z-index'].forEach(k=>seek.style.removeProperty(k));
   seek.querySelectorAll('.pwm').forEach(b=>b.style.removeProperty('display'));
  }
  const info=bar.querySelector('.pwinfo');
  if(info){info.style.removeProperty('display');info.style.removeProperty('visibility')}
 }
 function refresh(){
  requestAnimationFrame(restorePortraitProgress);
  setTimeout(restorePortraitProgress,180);
  setTimeout(restorePortraitProgress,420);
 }
 window.addEventListener('orientationchange',refresh,{passive:true});
 window.addEventListener('resize',refresh,{passive:true});
 window.addEventListener('pageshow',refresh,{passive:true});
 document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')refresh()});
 refresh();
 window.rimaV48RestorePortraitProgress=restorePortraitProgress;
})();
</script>"""
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V47_FAIL: body close missing')
h=h[:pos]+css+'\n'+h[pos:]

m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='68': raise SystemExit('V47_FAIL: expected base versionCode 68')
g=g[:m.start()]+re.sub('68','69',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.2.6': raise SystemExit('V47_FAIL: expected base versionName 3.2.6')
g=g[:m.start()]+m.group(0).replace('3.2.6','3.2.7')+g[m.end():]
hp.write_text(h,encoding='utf-8')
gp.write_text(g,encoding='utf-8')
print('V47_OK: normal Favorites count; downloaded status text in Favorites; portrait progress restored; setup page hidden during live stage; text escape cleanup; spacing; 3.2.7/code69')
