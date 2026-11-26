#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')

# Use the exact same R-in-frame lockup as the home header, scaled up for splash.
old='<div class="splash-mark" aria-hidden="true"><span class="splash-initial">R</span></div>'
new='<div class="brand-mark splash-brand-mark" aria-hidden="true"><span>R</span><i></i></div>'
if old in h:
    h=h.replace(old,new,1)
elif new not in h:
    raise SystemExit('V22_FAIL: splash mark source not found')

css=r"""<style id="rimalab-v22-brand-and-navigation">
/* Splash usa a marca oficial do cabeçalho: mesmo R, moldura e ponto de sinal. */
#rima-splash .brand-mark.splash-brand-mark{
 width:86px!important;height:86px!important;flex:0 0 86px!important;
 margin:0 auto 20px!important;border-radius:24px!important;
 transform:rotate(-5deg)!important;
}
#rima-splash .brand-mark.splash-brand-mark span{
 font:52px/.95 Anton,Impact,sans-serif!important;
 color:var(--ac)!important;transform:rotate(5deg)!important;
}
#rima-splash .brand-mark.splash-brand-mark i{
 width:9px!important;height:9px!important;right:11px!important;top:11px!important;
}
/* Não animar nem deformar a marca; a animação de carregamento permanece nos indicadores. */
#rima-splash .brand-mark.splash-brand-mark,
#rima-splash .brand-mark.splash-brand-mark span{
 animation:none!important;transition:none!important;
}
</style>"""
if 'id="rimalab-v22-brand-and-navigation"' not in h:
    pos=h.lower().rfind('</body>')
    if pos<0: raise SystemExit('V22_FAIL: body closing tag not found')
    h=h[:pos]+css+'\n'+h[pos:]

helper=r"""function rimaReturnPreviousScreenToTop(){
 const reset=()=>{
  try{window.scrollTo(0,0)}catch(e){}
  const root=document.scrollingElement;
  if(root)root.scrollTop=0;
  if(document.documentElement)document.documentElement.scrollTop=0;
  if(document.body)document.body.scrollTop=0;
 };
 reset();
 requestAnimationFrame(()=>{reset();requestAnimationFrame(reset)});
}
"""
if 'function rimaReturnPreviousScreenToTop()' not in h:
    marker='function lvStop(){'
    i=h.find(marker)
    if i<0: raise SystemExit('V22_FAIL: lvStop not found')
    h=h[:i]+helper+h[i:]

old_fn="function lvStop(){const f=LVFROM;CNT=0;wKill();stop();addMin();$('#su').hidden=false;$('#lv').hidden=true;$('#lv').style.display='';pk();if(f)go(1);else{if($('#train-step-1'))$('#train-step-1').hidden=true;if($('#train-step-2'))$('#train-step-2').hidden=false}}"
new_fn="function lvStop(){const f=LVFROM;CNT=0;wKill();stop();addMin();$('#su').hidden=false;$('#lv').hidden=true;$('#lv').style.display='';pk();if(f)go(1);else{if($('#train-step-1'))$('#train-step-1').hidden=true;if($('#train-step-2'))$('#train-step-2').hidden=false}rimaReturnPreviousScreenToTop()}"
if old_fn in h:
    h=h.replace(old_fn,new_fn,1)
elif new_fn not in h:
    raise SystemExit('V22_FAIL: unexpected lvStop implementation')
hp.write_text(h,encoding='utf-8')

g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+41\b',g):
    g=re.sub(r'\bversionCode\s+41\b','versionCode 42',g,count=1)
elif not re.search(r'\bversionCode\s+42\b',g):
    raise SystemExit('V22_FAIL: unexpected versionCode')
if "versionName '2.9.14'" in g:
    g=g.replace("versionName '2.9.14'","versionName '3.0.0'",1)
elif "versionName '3.0.0'" not in g:
    raise SystemExit('V22_FAIL: unexpected versionName')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V22_OK: splash com logo oficial R+moldura; retorno do palco sempre no topo; versão 3.0.0')
