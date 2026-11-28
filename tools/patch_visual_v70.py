#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V70_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-favorites-status-retry-spacing-v70' in h: raise SystemExit('V70_FAIL: patch já aplicado')
# Clear the persistent setup error notice and stage status at the point a
# different catalog track is selected, not merely when audio starts loading.
needle="const __rimaSelectNote=document.getElementById('rima-select-beat-note');if(__rimaSelectNote)__rimaSelectNote.remove();"
replacement=needle+"const __rimaAudioError=document.querySelectorAll('.rima-v58-audio-error');__rimaAudioError.forEach(e=>e.remove());const __rimaStatusRoots=['bp','bq','bbq'];__rimaStatusRoots.forEach(id=>{const r=document.getElementById(id);if(r)r.querySelectorAll('.rima-v58-audio-error').forEach(e=>e.remove())});const __rimaStageStatus=document.getElementById('cs');if(__rimaStageStatus)__rimaStageStatus.textContent='';"
if h.count(needle)!=1: raise SystemExit('V70_FAIL: seleção de faixa zLP não encontrada unicamente')
h=h.replace(needle,replacement,1)
css=r'''<style id="rimalab-favorites-status-retry-spacing-v70">
/* One consistent rhythm for category chips and Favorites in setup and stage. */
#bp .rima-v50-category-row,#bq .rima-v50-category-row,#bbq .rima-v50-category-row{
 margin-bottom:12px!important;margin-top:0!important;padding-bottom:0!important
}
#bp>.rima-v43-tools,#bq>.rima-v43-tools,#bbq>.rima-v43-tools{
 margin-top:0!important;margin-bottom:10px!important
}
/* Match favorite card title and metadata to the regular Boom bap/Trap/Drill rows.
   Actual favorite markup uses .beat-info/.beat-meta/.beat-artist/.okc. */
#bp .rima-v43-fav-row .rima-v43-fav-play,
#bq .rima-v43-fav-row .rima-v43-fav-play,
#bbq .rima-v43-fav-row .rima-v43-fav-play{
 font-family:'Archivo',system-ui,sans-serif!important;
 font-size:16px!important;font-weight:750!important;line-height:1.2!important;
 letter-spacing:-.015em!important
}
#bp .rima-v43-fav-row .rima-v43-fav-play b,
#bq .rima-v43-fav-row .rima-v43-fav-play b,
#bbq .rima-v43-fav-row .rima-v43-fav-play b{
 font:750 16px/1.2 'Archivo',system-ui,sans-serif!important;
 letter-spacing:-.015em!important
}
#bp .rima-v43-fav-row .beat-meta,
#bq .rima-v43-fav-row .beat-meta,
#bbq .rima-v43-fav-row .beat-meta{
 display:flex!important;align-items:center!important;flex-wrap:wrap!important;
 gap:8px!important;padding:0 12px 7px!important;min-height:24px!important
}
#bp .rima-v43-fav-row .beat-artist,
#bq .rima-v43-fav-row .beat-artist,
#bbq .rima-v43-fav-row .beat-artist{
 font:600 13px/1.3 'Archivo',system-ui,sans-serif!important
}
#bp .rima-v43-fav-row .rima-v48-fav-status,
#bq .rima-v43-fav-row .rima-v48-fav-status,
#bbq .rima-v43-fav-row .rima-v48-fav-status,
#bp .rima-v43-fav-row .okc,
#bq .rima-v43-fav-row .okc,
#bbq .rima-v43-fav-row .okc{
 display:inline-block!important;flex:0 0 auto!important;
 font:600 13px/1.3 'Archivo',system-ui,sans-serif!important;
 white-space:normal!important
}
/* A new selection removes the previous failure notice; keep hidden stale notices hidden. */
.rima-v58-audio-error:empty{display:none!important}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V70_FAIL: body ausente')
h=h[:pos]+css+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='89': raise SystemExit('V70_FAIL: versionCode base não é 89')
g=g[:m.start(1)]+'90'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.4.7': raise SystemExit('V70_FAIL: versionName base não é 3.4.7')
g=g[:m.start(1)]+'3.4.8'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V70_OK: clear previous audio error on every new zLP selection; actual favorite metadata selectors normalized; shared category/favorites rhythm; 3.4.8/code90')
