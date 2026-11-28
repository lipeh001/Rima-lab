#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V67_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-stage-entry-spacing-source-v67' in h: raise SystemExit('V67_FAIL: patch já aplicado')
# Fix at the original message lifecycle: publish WD.info from wStart itself,
# including synchronized mode, then let wWord replace it with the rhyme hint.
old="if(ZS.k=='syn')return;const br=240/ZS.bpm;"
new="if(ZS.k=='syn'){WD.info='Sincronização ativa. Prepare sua primeira rima.';const line=$('#cs');if(line)line.textContent=WD.info;return;}const br=240/ZS.bpm;"
if h.count(old)!=1: raise SystemExit('V67_FAIL: wStart sync branch not found uniquely')
h=h.replace(old,new,1)
old="WD.info=ZS.auto?'Beat sem introdução: já começa com tudo.':'Virada detectada. Entrando um pouco antes dela.';"
new="WD.info=ZS.auto?'Beat sem introdução: já começa com tudo.':'Virada detectada. Entrando um pouco antes dela.';const introLine=$('#cs');if(introLine)introLine.textContent=WD.info;"
if h.count(old)!=1: raise SystemExit('V67_FAIL: WD.info assignment not found uniquely')
h=h.replace(old,new,1)
# Apply spacing in the component that creates and positions the category row
# and Favorites toolbar. Inline !important defeats the legacy compact/landscape
# rules that repeatedly reset their margins.
old="if(categoryRow){categoryRow.classList.add('rima-v50-category-row');if(categoryRow.nextElementSibling!==bar)categoryRow.insertAdjacentElement('afterend',bar)}"
new="if(categoryRow){categoryRow.classList.add('rima-v50-category-row');categoryRow.style.setProperty('margin-bottom','22px','important');categoryRow.style.setProperty('margin-top','0px','important');if(categoryRow.nextElementSibling!==bar)categoryRow.insertAdjacentElement('afterend',bar);bar.style.setProperty('margin-top','0px','important');bar.style.setProperty('margin-bottom','14px','important')}"
if h.count(old)!=1: raise SystemExit('V67_FAIL: toolbar/category placement source not found uniquely')
h=h.replace(old,new,1)
css=r'''<style id="rimalab-stage-entry-spacing-source-v67">
/* Live stage catalog: source-created category and Favorites rows must not touch. */
#lv:not([hidden]) #bq>.rima-v50-category-row{
 margin-bottom:22px!important;height:auto!important;min-height:44px!important;
 padding-bottom:4px!important;overflow:visible!important
}
#lv:not([hidden]) #bq>.rima-v43-tools{
 margin-top:0!important;margin-bottom:14px!important;height:auto!important;
 min-height:46px!important;overflow:visible!important
}
#lv:not([hidden]) #stg.stage #cs{
 display:block!important;visibility:visible!important;opacity:1!important;
 flex:0 0 auto!important;min-height:1.35em!important;height:auto!important;
 max-height:none!important;overflow:visible!important;white-space:normal!important;
 margin:8px auto 0!important;padding:0 8px!important;line-height:1.35!important;
 text-align:center!important
}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V67_FAIL: body ausente')
h=h[:pos]+css+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='86': raise SystemExit('V67_FAIL: versionCode base não é 86')
g=g[:m.start(1)]+'87'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.4.4': raise SystemExit('V67_FAIL: versionName base não é 3.4.4')
g=g[:m.start(1)]+'3.4.5'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V67_OK: source-level intro publication and inline selector spacing; 3.4.5/code87')
