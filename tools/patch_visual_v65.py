#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V65_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-favorites-count-heart-stage-v65' in h: raise SystemExit('V65_FAIL: patch já aplicado')
tag='<script id="rimalab-favorites-layout-runtime-v43">'
a=h.find(tag)
if a<0: raise SystemExit('V65_FAIL: runtime V43 ausente')
b=a+len(tag);z=h.find('</script>',b)
js=h[b:z]
old='function count(){return read().length}'
new="""function count(){
  const available=new Set(allTracks().map(t=>t.key));
  return read().filter(key=>available.has(key)).length;
 }"""
if js.count(old)!=1: raise SystemExit('V65_FAIL: count V43 não corresponde')
js=js.replace(old,new,1);h=h[:b]+js+h[z:]
css=r'''<style id="rimalab-favorites-count-heart-stage-v65">
html body #lv:not([hidden]) #bq>.rima-v50-category-row,
html body #lv:not([hidden]) #bp>.rima-v50-category-row,
html body #lv:not([hidden]) #bbq>.rima-v50-category-row{
 display:flex!important;position:relative!important;float:none!important;clear:both!important;
 flex:0 0 auto!important;grid-column:1 / -1!important;width:100%!important;min-width:0!important;
 height:auto!important;min-height:46px!important;max-height:none!important;flex-flow:row wrap!important;
 align-items:center!important;gap:9px!important;margin:0 0 13px!important;padding:3px 2px 7px!important;
 box-sizing:border-box!important;overflow:visible!important
}
html body #lv:not([hidden]) #bq>.rima-v43-tools,
html body #lv:not([hidden]) #bp>.rima-v43-tools,
html body #lv:not([hidden]) #bbq>.rima-v43-tools{
 display:flex!important;position:relative!important;float:none!important;clear:both!important;
 flex:0 0 auto!important;grid-column:1 / -1!important;width:100%!important;min-width:0!important;
 height:auto!important;min-height:48px!important;max-height:none!important;margin:0 0 12px!important;
 padding:0!important;box-sizing:border-box!important;overflow:visible!important
}
html body #lv:not([hidden]) #bq>.rima-v43-tools>button,
html body #lv:not([hidden]) #bp>.rima-v43-tools>button,
html body #lv:not([hidden]) #bbq>.rima-v43-tools>button{
 display:flex!important;box-sizing:border-box!important;width:100%!important;min-height:46px!important;
 height:auto!important;margin:0!important;padding:9px 14px!important;overflow:visible!important
}
html body #lv:not([hidden]) #bq>.rima-v50-category-row>.tag.chip,
html body #lv:not([hidden]) #bp>.rima-v50-category-row>.tag.chip,
html body #lv:not([hidden]) #bbq>.rima-v50-category-row>.tag.chip{
 flex:1 1 0!important;min-width:0!important;max-width:none!important;height:auto!important;
 min-height:40px!important;margin:0!important;box-sizing:border-box!important;overflow:visible!important
}
html body #lv:not([hidden]) #bq>p.mut,
html body #lv:not([hidden]) #bp>p.mut,
html body #lv:not([hidden]) #bbq>p.mut{
 display:block!important;position:relative!important;clear:both!important;width:100%!important;
 height:auto!important;min-height:18px!important;max-height:none!important;margin:5px 0 8px!important;
 padding:2px 0!important;overflow:visible!important;white-space:normal!important;line-height:1.35!important
}
#bp .rima-v43-toggle,#bq .rima-v43-toggle,#bbq .rima-v43-toggle,
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart,#bbq .rima-v43-fav-heart,
#bp .rima-v29-fav,#bq .rima-v29-fav,#bbq .rima-v29-fav,
#pbar #rima-v29-player-heart,.rima-v60-heart-glyph,
#bp .rima-v43-fav-heart::before,#bq .rima-v43-fav-heart::before,#bbq .rima-v43-fav-heart::before,
#bp .rima-v29-fav::before,#bq .rima-v29-fav::before,#bbq .rima-v29-fav::before,
#pbar #rima-v29-player-heart::before{
 font-weight:400!important;-webkit-text-stroke:0!important;text-shadow:none!important
}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V65_FAIL: body ausente')
h=h[:pos]+css+'\n'+h[pos:]
runtime=r'''<script id="rimalab-stage-entry-copy-runtime-v65">
(function(){
 function keepIntro(){
  try{
   if(typeof WD==='undefined'||!WD||!WD.info)return;
   if(typeof ZS!=='undefined'&&ZS&&ZS.k==='syn')return;
   const line=document.getElementById('cs'),stage=document.getElementById('stg');
   if(!line||!stage||!stage.classList.contains('stage'))return;
   line.textContent=WD.info;
   ['display','visibility','height','min-height','overflow'].forEach((p,i)=>line.style.setProperty(p,['block','visible','auto','18px','visible'][i],'important'));
  }catch(_){}
 }
 const old=window.wWord;
 if(typeof old==='function'&&!old.__rimaV65){const f=function(){const r=old.apply(this,arguments);keepIntro();return r};f.__rimaV65=true;window.wWord=f}
 const start=window.wStart;
 if(typeof start==='function'&&!start.__rimaV65){const f=function(){const r=start.apply(this,arguments);keepIntro();requestAnimationFrame(keepIntro);setTimeout(keepIntro,100);return r};f.__rimaV65=true;window.wStart=f}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',keepIntro,{once:true});else keepIntro();
 window.rimaV65KeepIntro=keepIntro;
})();</script>'''
pos=h.lower().rfind('</body>');h=h[:pos]+runtime+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='84': raise SystemExit('V65_FAIL: versionCode base')
g=g[:m.start(1)]+'85'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.4.2': raise SystemExit('V65_FAIL: versionName base')
g=g[:m.start(1)]+'3.4.3'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V65_OK')
