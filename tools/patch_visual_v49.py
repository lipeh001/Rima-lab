#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V49_FAIL: missing HTML or Gradle')
h=hp.read_text(encoding='utf-8')
g=gp.read_text(encoding='utf-8')
if 'rimalab-shared-selector-orientation-v49' in h: raise SystemExit('V49_FAIL: already applied')
if 'rimalab-favorites-layout-runtime-v43' not in h or 'rimalab-landscape-stage-download-v47' not in h:
    raise SystemExit('V49_FAIL: expected V43/V47 runtime missing')

# The V42 dockPlayer() writes landscape geometry as inline !important styles.
# It returned early in portrait without undoing those writes. Remove the V48
# seekbar workaround entirely; the original player CSS is the single source of truth.
for ident in ('rimalab-favorites-details-v48','rimalab-orientation-recovery-runtime-v48'):
    pattern=re.compile(r'<(?:style|script) id="'+re.escape(ident)+r'">.*?</(?:style|script)>',re.S)
    h,n=pattern.subn('',h,count=1)
    if n!=1: raise SystemExit('V49_FAIL: expected V48 block missing: '+ident)

# One shared renderer for the setup selector (#bp) and live selector (#bq).
open_tag='<script id="rimalab-favorites-layout-runtime-v43">'
a=h.find(open_tag)
if a<0: raise SystemExit('V49_FAIL: V43 opening tag missing')
body=a+len(open_tag); z=h.find('</script>',body)
if z<0: raise SystemExit('V49_FAIL: V43 closing tag missing')
js=h[body:z]

# Put the same Favorites control after the category chips in both selectors.
old_toolbar="""  if(!bar){bar=document.createElement('div');bar.className='rima-v43-tools';root.insertBefore(bar,root.firstChild)}
  // Isolate from V40/V42 legacy handlers; the V43 controller owns both selectors.
  bar.className='rima-v43-tools';"""
new_toolbar="""  if(!bar){bar=document.createElement('div');bar.className='rima-v43-tools'}
  // Both roots use the same component order: description, categories, Favorites, catalog.
  bar.className='rima-v43-tools';
  const categoryRow=Array.from(root.children).find(e=>e.classList.contains('row')&&e.querySelector('.tag.chip'));
  if(categoryRow){if(categoryRow.nextElementSibling!==bar)categoryRow.insertAdjacentElement('afterend',bar)}
  else if(bar.parentElement!==root)root.insertBefore(bar,root.firstChild);"""
if old_toolbar not in js: raise SystemExit('V49_FAIL: toolbar insertion block missing')
js=js.replace(old_toolbar,new_toolbar,1)

# Replace the #bp/#bq divergent display logic with one common renderer.
pat=re.compile(r" function renderRoot\(root\)\{.*?\n \}\n function render\(\)",re.S)
new_render=""" function renderRoot(root){
  const bar=ensureToolbar(root);
  removeView(root);
  // zBpick() produces the same direct-child .bsl catalog in both roots.
  // Hide/show that exact same catalog and attribution in both places.
  root.querySelectorAll(':scope > .bsl').forEach(list=>{list.hidden=showing});
  root.querySelectorAll(':scope > .catalog-attribution').forEach(note=>{note.hidden=showing});
  if(showing)bar.insertAdjacentHTML('afterend',favoriteMarkup());
 }
 function render()"""
js,n=pat.subn(new_render,js,count=1)
if n!=1: raise SystemExit('V49_FAIL: divergent renderRoot function not found')

# Tapping Favorites while already open is a navigation action: return to Boom bap.
old_click="""  if(!b)return;e.preventDefault();e.stopImmediatePropagation();setMode(!showing,b.closest('#bp,#bq').id);"""
new_click="""  if(!b)return;
  e.preventDefault();e.stopImmediatePropagation();
  const root=b.closest('#bp,#bq').id;
  if(showing){
   setMode(false,root);
   if(typeof window.zLS==='function')window.zLS('Boom bap');
   else if(typeof ZS!=='undefined')ZS.s='Boom bap';
   render();
  }else setMode(true,root);"""
if old_click not in js: raise SystemExit('V49_FAIL: Favorites toggle click handler missing')
js=js.replace(old_click,new_click,1)

h=h[:body]+js+h[z:]

# Make the live landscape screen an opaque, scroll-locked app surface. The
# previous inset-bottom layout exposed the still-scrollable setup page behind it.
old_main=""" body.pl:not(.pv) main,body.pl.sy:not(.pv) main{
  width:100%!important;max-width:none!important;box-sizing:border-box!important;
 }"""
new_main=""" body.pl:not(.pv) main,body.pl.sy:not(.pv) main{
  position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;
  max-width:none!important;max-height:100vh!important;box-sizing:border-box!important;
  margin:0!important;padding:0!important;overflow:hidden!important;overscroll-behavior:none!important;
 }"""
if old_main not in h: raise SystemExit('V49_FAIL: landscape main rule missing')
h=h.replace(old_main,new_main,1)
old_lv="""  position:fixed!important;inset:0 0 var(--rima-stage-bottom,90px) 0!important;
  display:grid!important;width:auto!important;height:auto!important;min-height:0!important;
  max-height:none!important;box-sizing:border-box!important;overflow:hidden!important;"""
new_lv="""  position:fixed!important;inset:0!important;
  display:grid!important;width:auto!important;height:100vh!important;min-height:0!important;
  max-height:100vh!important;box-sizing:border-box!important;overflow:hidden!important;
  padding-bottom:calc(var(--rima-stage-bottom,90px) + 4px)!important;
  background:#0b0b0e!important;isolation:isolate!important;"""
if old_lv not in h: raise SystemExit('V49_FAIL: landscape live-stage inset rule missing')
h=h.replace(old_lv,new_lv,1)

# Remove the earlier V48 workaround's effects by restoring every property set by
# V42 dockPlayer() whenever the viewport returns to portrait.
css=r"""<style id="rimalab-shared-selector-orientation-v49">
/* The page behind the live stage must not remain scrollable in landscape. */
@media (orientation:landscape) and (min-width:560px){
 html.rima-live-landscape,body.rima-live-landscape{
  width:100%!important;height:100%!important;min-height:100%!important;
  overflow:hidden!important;overscroll-behavior:none!important;
 }
 body.rima-live-landscape main{
  position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;
  overflow:hidden!important;overscroll-behavior:none!important;
 }
 body.rima-live-landscape #lv:not([hidden]){
  inset:0!important;bottom:0!important;background:#0b0b0e!important;
 }
}
#bp>.rima-v43-tools,#bq>.rima-v43-tools{
 display:flex!important;position:relative!important;float:none!important;clear:both!important;
 width:100%!important;max-width:100%!important;box-sizing:border-box!important;
}
#bp>.rima-v43-favlist,#bq>.rima-v43-favlist{
 display:block!important;position:relative!important;clear:both!important;float:none!important;
 width:100%!important;max-width:100%!important;box-sizing:border-box!important;
}
#bp>.bsl[hidden],#bq>.bsl[hidden],
#bp>.catalog-attribution[hidden],#bq>.catalog-attribution[hidden]{display:none!important}
</style>
<script id="rimalab-shared-selector-orientation-runtime-v49">
(function(){
 'use strict';
 const body=document.body,lv=document.getElementById('lv'),bar=document.getElementById('pbar');
 const dockProps=['position','top','bottom','left','right','inset','transform','z-index','width','max-width','height','min-height','max-height','display'];
 function landscape(){return !!(window.matchMedia&&window.matchMedia('(orientation:landscape) and (min-width:560px)').matches)}
 function live(){return !!(lv&&!lv.hidden)}
 function clearPortraitDock(){
  if(!bar)return;
  dockProps.forEach(k=>bar.style.removeProperty(k));
  // Keep the original progress controls and markup intact. Only discard the
  // inline geometry that the landscape dock wrote to this same player node.
 }
 function sync(){
  const wide=landscape(),active=wide&&live()&&body.classList.contains('pl')&&!body.classList.contains('pv');
  body.classList.toggle('rima-live-landscape',active);
  if(!wide)clearPortraitDock();
 }
 function settle(){
  requestAnimationFrame(sync);
  setTimeout(sync,120);
  setTimeout(sync,320);
  setTimeout(sync,620);
 }
 if(lv&&window.MutationObserver)new MutationObserver(settle).observe(lv,{attributes:true,attributeFilter:['hidden']});
 window.addEventListener('resize',settle,{passive:true});
 window.addEventListener('orientationchange',settle,{passive:true});
 window.addEventListener('pageshow',settle,{passive:true});
 if(window.visualViewport)window.visualViewport.addEventListener('resize',settle,{passive:true});
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)settle()});
 settle();
 window.rimaV49SyncOrientation=sync;
 window.rimaV49ClearPortraitPlayer=clearPortraitDock;
})();
</script>"""
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V49_FAIL: body close missing')
h=h[:pos]+css+'\n'+h[pos:]

m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='69': raise SystemExit('V49_FAIL: expected base versionCode 69')
g=g[:m.start()]+re.sub('69','70',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.2.7': raise SystemExit('V49_FAIL: expected base versionName 3.2.7')
g=g[:m.start()]+m.group(0).replace('3.2.7','3.2.8')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V49_OK: shared #bp/#bq selector renderer and order; Favorites returns to Boom bap; hide both catalog lists; lock landscape page; clear V42 inline dock styles on portrait; 3.2.8/code70')
