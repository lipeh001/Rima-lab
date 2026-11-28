#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V63_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-favorites-selection-colors-v63' in h: raise SystemExit('V63_FAIL: patch já aplicado')
if 'rimalab-favorites-player-scroll-stage-v62' not in h: raise SystemExit('V63_FAIL: base V62 ausente')

# Favorites mode owns the visible list. Clear all category selection classes at
# the source, so the previous Boom bap/Trap/Drill chip cannot remain highlighted.
tag='<script id="rimalab-favorites-layout-runtime-v43">'
a=h.find(tag)
if a<0: raise SystemExit('V63_FAIL: runtime Favorites V43 ausente')
b=a+len(tag);z=h.find('</script>',b)
if z<0: raise SystemExit('V63_FAIL: fechamento V43 ausente')
js=h[b:z]
old="function setMode(v,root){showing=!!v;if(root)activeRoot=root;render()}"
new="""function setMode(v,root){
  showing=!!v;if(root)activeRoot=root;
  if(showing){
   ['bp','bq','bbq'].forEach(id=>{
    const r=document.getElementById(id);if(!r)return;
    r.querySelectorAll('.rima-v50-category-row .tag.chip,.row .tag.chip').forEach(c=>{
     c.classList.remove('on','active','selected');
     c.setAttribute('aria-pressed','false');
    });
   });
  }
  render();
 }"""
if js.count(old)!=1: raise SystemExit('V63_FAIL: setMode V43 não corresponde')
js=js.replace(old,new,1)
h=h[:b]+js+h[z:]

# Derive Favorites-open from the actual visible list, not a toolbar class that
# can be stale during the first render after switching tabs.
tag62='<script id="rimalab-favorites-player-scroll-stage-v62">'
a=h.find(tag62)
if a<0: raise SystemExit('V63_FAIL: runtime V62 ausente')
b=a+len(tag62);z=h.find('</script>',b)
js=h[b:z]
old="const favOpen=!!document.querySelector('#bp>.rima-v43-tools .rima-v43-toggle.active,#bq>.rima-v43-tools .rima-v43-toggle.active');"
new="const favOpen=!!document.querySelector('#bp>.rima-v43-favlist:not([hidden]),#bq>.rima-v43-favlist:not([hidden]),#bbq>.rima-v43-favlist:not([hidden])');"
if js.count(old)!=1: raise SystemExit('V63_FAIL: detector de Favorites V62 não corresponde')
js=js.replace(old,new,1)
h=h[:b]+js+h[z:]

css=r'''<style id="rimalab-favorites-selection-colors-v63">
/* Match Favorites hearts to the regular Boom bap / Trap / Drill favorite button:
   dark interior, gold outline and gold filled glyph (never yellow fill/black glyph). */
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart,#bbq .rima-v43-fav-heart,
#bp .rima-v43-fav-heart[aria-pressed="true"],#bq .rima-v43-fav-heart[aria-pressed="true"],#bbq .rima-v43-fav-heart[aria-pressed="true"],
#bp .rima-v29-fav[aria-pressed="true"],#bq .rima-v29-fav[aria-pressed="true"],#bbq .rima-v29-fav[aria-pressed="true"]{
 background:rgba(255,203,84,.16)!important;
 border:1px solid #ffcb54!important;
 color:#ffcb54!important;
 box-shadow:none!important;
}
#bp .rima-v43-fav-heart::before,#bq .rima-v43-fav-heart::before,#bbq .rima-v43-fav-heart::before,
#bp .rima-v29-fav::before,#bq .rima-v29-fav::before,#bbq .rima-v29-fav::before{
 color:#ffcb54!important;
}
/* The active category stays yellow, but has no white offset/drop-shadow underneath. */
#bp .rima-v50-category-row>.tag.chip.on,#bq .rima-v50-category-row>.tag.chip.on,#bbq .rima-v50-category-row>.tag.chip.on,
#bp .rima-v50-category-row>.tag.chip.active,#bq .rima-v50-category-row>.tag.chip.active,#bbq .rima-v50-category-row>.tag.chip.active{
 background:var(--ac)!important;color:var(--on)!important;
 border-color:var(--ink)!important;box-shadow:none!important;
 filter:none!important;transform:none!important;
}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V63_FAIL: </body> ausente')
h=h[:pos]+css+'\n'+h[pos:]

m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='82': raise SystemExit('V63_FAIL: versionCode base não é 82')
g=g[:m.start(1)]+'83'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.4.0': raise SystemExit('V63_FAIL: versionName base não é 3.4.0')
g=g[:m.start(1)]+'3.4.1'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V63_OK: Favorites clears previous category selection; Favorites heart colors match catalog; selected chip has no white shadow; 3.4.1/code83')
