#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')

# Do not animate the word when it changes; the word's beat effect is driven by pulse(),
# exactly the same callback that illuminates the frame.
h=h.replace("$('#cs').textContent=c.sub;stamp(w);WD.nw++;WD.cs=-1",
            "$('#cs').textContent=c.sub;WD.nw++;WD.cs=-1",1)

old="""function pulse(q){if(CNT&&q>0){const e=$('#lv').hidden?($('#sb')||(B&&B.cin?$('#cd'):null)):$('#cb');if(e){e.textContent=4-q;e.style.fontSize='96px';stamp(e)}}$$('.dots').forEach(c=>[...c.children].forEach((d,j)=>d.classList.toggle('on',j==q)));$$('#stg,#bt .stage').forEach(e=>{e.classList.add('hit');clearTimeout(e.__rimaBeatTimer);e.__rimaBeatTimer=setTimeout(()=>e.classList.remove('hit'),440)})}"""
new="""function pulse(q){if(CNT&&q>0){const e=$('#lv').hidden?($('#sb')||(B&&B.cin?$('#cd'):null)):$('#cb');if(e){e.textContent=4-q;e.style.fontSize='96px';stamp(e)}}$$('.dots').forEach(c=>[...c.children].forEach((d,j)=>d.classList.toggle('on',j==q)));$$('#stg,#bt .stage').forEach(e=>{e.classList.add('hit');clearTimeout(e.__rimaBeatTimer);e.__rimaBeatTimer=setTimeout(()=>e.classList.remove('hit'),440)});const word=$('#lv').hidden?null:$('#cb');if(word){word.classList.remove('beat-word-hit');void word.offsetWidth;word.classList.add('beat-word-hit');clearTimeout(word.__rimaWordBeatTimer);word.__rimaWordBeatTimer=setTimeout(()=>word.classList.remove('beat-word-hit'),440)}}"""
if old in h:
 h=h.replace(old,new,1)
elif "const word=$('#lv').hidden?null:$('#cb');if(word)" not in h:
 raise SystemExit('V14_FAIL: função pulse() esperada não encontrada')

css=r'''<style id="rimalab-visual-v14">
#stg.stage.hit::after,#bt .stage.hit::after{animation:rimalab-gold-bloom-v14 .48s ease-out!important}
@keyframes rimalab-gold-bloom-v14{
 0%{opacity:.42;border-color:rgba(237,195,77,.52)!important;box-shadow:inset 0 0 22px rgba(237,195,77,.11),0 0 22px rgba(237,195,77,.16)!important}
 100%{opacity:.14;border-color:rgba(237,195,77,.16)!important;box-shadow:inset 0 0 8px rgba(237,195,77,.025),0 0 5px rgba(237,195,77,.02)!important}
}
#stg.stage #cb.beat-word-hit{
 color:#ffe6a0!important;
 text-shadow:0 0 7px rgba(255,226,151,.52),0 0 20px rgba(237,195,77,.32),0 0 34px rgba(237,195,77,.14)!important;
 filter:brightness(1.12)!important;
 transform:none!important;
 animation:rimalab-word-beat-v14 .48s ease-out!important;
}
@keyframes rimalab-word-beat-v14{
 0%{color:#ffe6a0;text-shadow:0 0 7px rgba(255,226,151,.52),0 0 20px rgba(237,195,77,.32),0 0 34px rgba(237,195,77,.14);filter:brightness(1.12)}
 100%{color:#edc34d;text-shadow:0 0 18px rgba(237,195,77,.16);filter:brightness(1)}
}
@media(prefers-reduced-motion:reduce){#stg.stage #cb.beat-word-hit{animation:none!important;color:#edc34d!important}}
</style>'''
if 'id="rimalab-visual-v14"' not in h:
 pos=h.lower().rfind('</body>')
 if pos<0:raise SystemExit('V14_FAIL: </body> não encontrado')
 h=h[:pos]+css+'\n'+h[pos:]

hp.write_text(h,encoding='utf-8')
g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+32\b',g):g=re.sub(r'\bversionCode\s+32\b','versionCode 33',g,count=1)
elif not re.search(r'\bversionCode\s+33\b',g):raise SystemExit('V14_FAIL: versionCode inesperado')
if "versionName '2.9.5'" in g:g=g.replace("versionName '2.9.5'","versionName '2.9.6'",1)
elif "versionName '2.9.6'" not in g:raise SystemExit('V14_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V14_OK: palavra e moldura recebem o mesmo pulso agendado pelo relógio real do beat')
