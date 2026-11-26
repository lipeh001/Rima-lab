#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
html=hp.read_text(encoding='utf-8')

# Restore the original word/stage beat trigger removed in v12.
old="$('#cs').textContent=c.sub;WD.nw++"
new="$('#cs').textContent=c.sub;stamp(w);WD.nw++"
if old in html:
    html=html.replace(old,new,1)
elif new not in html:
    raise SystemExit('V13_FAIL: gatilho stamp(w) não encontrado; não vou inventar sincronização')

# Remove the v12 sizing code that constrained every word to a small computed size.
html=re.sub(r'<style id="rima-word-fit-v12">.*?</style>\s*<script id="rima-word-fit-script-v12">.*?</script>', '', html, count=1, flags=re.S)

fit = r'''<style id="rima-word-fit-v13">
#stg.stage #cb{
 display:block!important;box-sizing:border-box!important;width:100%!important;max-width:100%!important;
 margin:12px auto!important;padding:8px 6px!important;text-align:center!important;
 font-family:Anton,Impact,"Arial Narrow",sans-serif!important;font-size:72px!important;
 font-weight:900!important;line-height:1.02!important;letter-spacing:-.045em!important;
 color:#edc34d!important;text-shadow:0 0 18px rgba(237,195,77,.16)!important;
 white-space:nowrap!important;word-break:normal!important;overflow-wrap:normal!important;
 transform:none!important;animation:none!important;transition:none!important;filter:none!important;
}
#stg.stage #cb.word,#stg.stage.hit #cb{transform:none!important;animation:none!important}
.rm span{font-size:18px!important;line-height:1.2!important;padding:10px 15px!important}
</style>
<script id="rima-word-fit-script-v13">
(function(){
 const fit=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');
  if(!e||!stage)return;
  const raw=(e.textContent||'').trim();
  if(!raw)return;
  const available=Math.max(120,stage.clientWidth-54);
  // Short/medium words retain the large fixed stage typography.
  e.style.setProperty('font-size','72px','important');
  if(raw.length<=12 && e.scrollWidth<=available)return;
  if(raw.length<=12 && e.scrollWidth>available){
   // Only shrink when a medium word truly exceeds the usable width.
  }
  let low=22,high=72;
  for(let i=0;i<14;i++){
   const mid=(low+high)/2;
   e.style.setProperty('font-size',mid.toFixed(1)+'px','important');
   if(e.scrollWidth<=available)low=mid;else high=mid;
  }
  e.style.setProperty('font-size',Math.floor(low)+'px','important');
 };
 const boot=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');
  if(!e||!stage)return;
  new MutationObserver(fit).observe(e,{childList:true,subtree:true,characterData:true});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(fit).observe(stage);
  window.addEventListener('resize',fit,{passive:true});
  fit();
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
</script>'''
if 'id="rima-word-fit-v13"' not in html:
    pos=html.lower().rfind('</body>')
    if pos<0: raise SystemExit('V13_FAIL: </body> não encontrado')
    html=html[:pos]+fit+'\n'+html[pos:]

# Softer bloom pulse, tied to the same stage hit class; no text movement or harsh blink.
visual=r'''<style id="rimalab-visual-v13">
#stg.stage,#bt .stage{transition:border-color .22s ease,box-shadow .22s ease!important;transform:none!important}
#stg.stage.hit,#bt .stage.hit{
 border-color:rgba(237,195,77,.82)!important;
 box-shadow:0 0 0 1px rgba(237,195,77,.14),0 0 24px rgba(237,195,77,.19),inset 0 0 22px rgba(237,195,77,.075)!important;
 transform:none!important;
}
#stg.stage.hit::after,#bt .stage.hit::after{animation:rimalab-gold-bloom-v13 .52s ease-out!important}
@keyframes rimalab-gold-bloom-v13{
 0%{opacity:.48;border-color:rgba(237,195,77,.56)!important;box-shadow:inset 0 0 24px rgba(237,195,77,.12),0 0 24px rgba(237,195,77,.18)!important}
 100%{opacity:.14;border-color:rgba(237,195,77,.16)!important;box-shadow:inset 0 0 8px rgba(237,195,77,.025),0 0 5px rgba(237,195,77,.02)!important}
}
#stg.stage #cb,.stage .word,#bt .stage .word{color:#edc34d!important;text-shadow:0 0 18px rgba(237,195,77,.16)!important;transform:none!important;animation:none!important;filter:none!important}
.splash-mark .splash-initial{color:#fff!important;text-shadow:0 1px 2px rgba(0,0,0,.24)!important}
@media(prefers-reduced-motion:reduce){#stg.stage.hit::after,#bt .stage.hit::after{animation:none!important;opacity:.2!important}}
</style>'''
if 'id="rimalab-visual-v13"' not in html:
    pos=html.lower().rfind('</body>')
    html=html[:pos]+visual+'\n'+html[pos:]

hp.write_text(html,encoding='utf-8')

g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+31\b',g):g=re.sub(r'\bversionCode\s+31\b','versionCode 32',g,count=1)
elif not re.search(r'\bversionCode\s+32\b',g):raise SystemExit('V13_FAIL: versionCode inesperado')
if "versionName '2.9.4'" in g:g=g.replace("versionName '2.9.4'","versionName '2.9.5'",1)
elif "versionName '2.9.5'" not in g:raise SystemExit('V13_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V13_OK: gatilho do beat restaurado, tipografia grande, redução só por overflow, brilho dourado suave, R branco')
