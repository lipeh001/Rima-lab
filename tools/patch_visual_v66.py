#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V66_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-favorites-entry-fix-v66' in h: raise SystemExit('V66_FAIL: patch já aplicado')
# Remove late message publishers from V64/V65. The original wLoop already
# displays WD.info during phase 0 and clears it when the first word starts.
for script_id in ('rimalab-stage-selector-gap-entry-message-runtime-v64','rimalab-stage-entry-copy-runtime-v65'):
    pattern=r'<script id="'+re.escape(script_id)+r'">[\\s\\S]*?</script>'
    h,n=re.subn(pattern,'',h,count=1)
    if n!=1: raise SystemExit('V66_FAIL: runtime tardio não encontrado: '+script_id)
# Count exactly the unique tracks that are rendered in the Favorites view.
needle=" const read=()=>{try{const a=JSON.parse(localStorage.getItem(KEY)||'[]');return Array.isArray(a)?[...new Set(a.map(String).filter(Boolean))]:[]}catch(_){return[]}};"
if h.count(needle)!=1: raise SystemExit('V66_FAIL: reader de favoritos não localizado')
replacement=needle+"""
 const favoriteItems=()=>{
  const saved=new Set(read()),seen=new Set(),items=[];
  for(const track of allTracks()){
   if(!saved.has(track.key)||seen.has(track.key))continue;
   seen.add(track.key);items.push(track);
  }
  return items;
 };"""
h=h.replace(needle,replacement,1)
old=""" function count(){
  const available=new Set(allTracks().map(t=>t.key));
  return read().filter(key=>available.has(key)).length;
 }"""
if h.count(old)!=1: raise SystemExit('V66_FAIL: contador V65 não localizado')
h=h.replace(old," function count(){return favoriteItems().length}",1)
old2=" const saved=new Set(read()),seen=new Set(),items=allTracks().filter(t=>{if(!saved.has(t.key)||seen.has(t.key))return false;seen.add(t.key);return true});"
if h.count(old2)!=1: raise SystemExit('V66_FAIL: montagem da lista não localizada')
h=h.replace(old2," const items=favoriteItems();",1)
# Never republish the intro message after the first word is on stage.
# The core wLoop already shows WD.info during its preparation phase.
h=h.replace("if(line&&msg)line.textContent=msg;","if(line&&msg&&typeof WD!=='undefined'&&WD&&WD.ph===0&&!document.getElementById('stg')?.classList.contains('stage'))line.textContent=msg;",1)
h=h.replace("if(message&&line.textContent.trim()!==message)line.textContent=message;","if(message&&typeof WD!=='undefined'&&WD&&WD.ph===0&&!document.getElementById('stg')?.classList.contains('stage')&&line.textContent.trim()!==message)line.textContent=message;",1)
# CSS: explicit physical separation; override all older stage-specific margins.
css=r'''<style id="rimalab-favorites-entry-fix-v66">
/* Put a real, measurable gap between category selectors and Favorites. */
html body #lv:not([hidden]) #bq>.rima-v50-category-row,
html body #lv:not([hidden]) #bp>.rima-v50-category-row,
html body #lv:not([hidden]) #bbq>.rima-v50-category-row{
 display:flex!important;position:relative!important;float:none!important;clear:both!important;
 box-sizing:border-box!important;flex:0 0 auto!important;width:100%!important;height:auto!important;
 min-height:48px!important;max-height:none!important;overflow:visible!important;
 margin:0 0 22px!important;padding:2px 0 6px!important;gap:9px!important;
}
html body #lv:not([hidden]) #bq>.rima-v43-tools,
html body #lv:not([hidden]) #bp>.rima-v43-tools,
html body #lv:not([hidden]) #bbq>.rima-v43-tools{
 display:block!important;position:relative!important;float:none!important;clear:both!important;
 box-sizing:border-box!important;flex:0 0 auto!important;width:100%!important;height:auto!important;
 min-height:46px!important;margin:0 0 14px!important;padding:0!important;overflow:visible!important;
}
html body #lv:not([hidden]) #bq>.rima-v43-tools .rima-v43-toggle,
html body #lv:not([hidden]) #bp>.rima-v43-tools .rima-v43-toggle,
html body #lv:not([hidden]) #bbq>.rima-v43-tools .rima-v43-toggle{
 width:100%!important;height:auto!important;min-height:46px!important;margin:0!important;
}
/* Intro copy belongs to preparation only, never under the first prompt. */
#lv #cs{display:block;min-height:1.35em;line-height:1.35;white-space:normal}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V66_FAIL: body ausente')
h=h[:pos]+css+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='85': raise SystemExit('V66_FAIL: versionCode base inesperada')
g=g[:m.start(1)]+'86'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.4.3': raise SystemExit('V66_FAIL: versionName base inesperada')
g=g[:m.start(1)]+'3.4.4'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V66_OK')
